#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace fs=std::filesystem;
using U=uint64_t;
using Bytes=std::vector<unsigned char>;
void check(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
void span(U at,U size,U limit){check(at<=limit&&size<=limit-at,"range outside input");}
U integer(const Bytes& b,U at,unsigned width=4){span(at,width,b.size());U out=0;for(unsigned i=0;i<width;++i)out|=U(b[size_t(at)+i])<<(8*i);return out;}
double scalar(const Bytes& b,U at){uint32_t bits=uint32_t(integer(b,at));float out;std::memcpy(&out,&bits,4);check(std::isfinite(out),"nonfinite float");return out;}
struct Region{U at,size;};
bool operator<(Region a,Region b){return a.at<b.at||(a.at==b.at&&a.size<b.size);}
bool operator==(Region a,Region b){return a.at==b.at&&a.size==b.size;}
std::string inspect(const Bytes& b){
    span(0,8,b.size());check(integer(b,0)==0x00544d4c&&integer(b,4,2)==67,"requires LMT67 little endian explicit 32-bit profile");
    U slots=integer(b,6,2);check(slots<=4096,"slot budget");span(8,slots*4,b.size());U tableEnd=8+slots*4;
    std::set<U> animations;U nullSlots=0;
    for(U i=0;i<slots;++i){U at=integer(b,8+i*4);if(at)animations.insert(at);else ++nullSlots;}
    std::vector<Region> metadata={{0,tableEnd}},payloads;
    U tracks=0,decodedTracks=0,unsupportedTracks=0,keys=0,zeroDeltas=0;
    std::ostringstream out;out<<std::setprecision(17)<<"[";bool firstTrack=true;
    for(U animation:animations){
        check(animation>=tableEnd&&animation%16==0,"animation alignment/table overlap");span(animation,60,b.size());metadata.push_back({animation,60});
        U trackAt=integer(b,animation),count=integer(b,animation+4),frames=integer(b,animation+8);
        check(count<=4096&&frames<=1000000,"animation budget");tracks+=count;check(tracks<=100000,"aggregate track budget");
        for(U i=0;i<8;++i)scalar(b,animation+16+i*4);
        for(U offset:{U(52),U(56)}){U pointer=integer(b,animation+offset);if(pointer)span(pointer,1,b.size());}
        if(count){check(trackAt!=0,"null track table");span(trackAt,count*36,b.size());metadata.push_back({trackAt,count*36});}
        for(U i=0;i<count;++i){
            U at=trackAt+i*36,codec=integer(b,at,1),type=integer(b,at+1,1),boneType=integer(b,at+2,1),bone=integer(b,at+3,1);
            scalar(b,at+4);for(U j=0;j<4;++j)scalar(b,at+16+j*4);
            U size=integer(b,at+8),buffer=integer(b,at+12),extreme=integer(b,at+32);
            if(size){check(buffer!=0,"null nonempty buffer");span(buffer,size,b.size());payloads.push_back({buffer,size});}
            if(extreme){span(extreme,32,b.size());payloads.push_back({extreme,32});for(U j=0;j<8;++j)scalar(b,extreme+j*4);}
            U stride=codec==1?12:(codec==3?16:(codec==4?8:(codec==5?4:0)));
            if(!firstTrack){out<<',';}firstTrack=false;
            out<<"{\"animation_offset\":"<<animation<<",\"track\":"<<i<<",\"codec_raw\":"<<codec
               <<",\"type_raw\":"<<type<<",\"bone_type_raw\":"<<boneType<<",\"bone_id_raw\":"<<bone
               <<",\"bone_is_sentinel\":"<<(bone==255?"true":"false")<<",\"declared_frames_raw\":"<<frames
               <<",\"supported_vector_codec\":"<<(stride?"true":"false")<<",\"extremes_present\":"<<(extreme?"true":"false")
               <<",\"extremes_applied\":"<<((stride&&extreme&&size)?"true":"false")
               <<",\"buffer_bytes\":"<<size<<",\"samples\":[";
            if(stride){
                check(size%stride==0,"partial vector record");U n=size/stride;keys+=n;check(keys<=100000,"decoded key budget");
                if(n)++decodedTracks;
                U frame=0;
                for(U k=0;k<n;++k){
                    U p=buffer+k*stride,delta=codec==1?1:(codec==3?integer(b,p+12):(codec==4?integer(b,p+6,2):integer(b,p+3,1)));
                    check(delta<=1000000&&frame<=1000000-delta,"raw frame budget");zeroDeltas+=delta==0;
                    if(k){out<<',';}out<<"{\"frame_before_delta\":"<<frame<<",\"delta_raw\":"<<delta<<",\"xyz\":[";
                    for(U axis=0;axis<3;++axis){
                        double v=(codec==1||codec==3)?scalar(b,p+axis*4):
                            (codec==4?double(integer(b,p+axis*2,2))/65535.0:double(integer(b,p+axis,1))/255.0);
                        if(extreme)v=scalar(b,extreme+16+axis*4)+scalar(b,extreme+axis*4)*v;
                        check(std::isfinite(v),"decoded vector overflow");if(axis){out<<',';}out<<v;
                    }
                    out<<"]}";frame+=delta;
                }
            }else ++unsupportedTracks;
            out<<"]}";check(out.tellp()<=std::streamoff(32*1024*1024),"report budget");
        }
    }
    std::sort(metadata.begin(),metadata.end());metadata.erase(std::unique(metadata.begin(),metadata.end()),metadata.end());
    for(size_t i=1;i<metadata.size();++i)check(metadata[i].at>=metadata[i-1].at+metadata[i-1].size,"overlapping interpreted metadata");
    for(auto p:payloads){
        auto next=std::upper_bound(metadata.begin(),metadata.end(),p.at,[](U at,Region r){return at<r.at;});
        if(next!=metadata.end())check(p.at+p.size<=next->at,"payload overlaps metadata");
        if(next!=metadata.begin()){auto previous=next-1;check(previous->at+previous->size<=p.at,"payload overlaps metadata");}
    }
    out<<']';std::ostringstream report;
    report<<"{\"schema\":1,\"profile\":\"LMT67_LE32_60byte_animation_prefix\",\"partial_vector_key_inspection\":true,"
          "\"model_association_verified\":false,\"animation_playback_verified\":false,\"events_and_float_tracks_validated\":false,"
          "\"reference_frame_and_loop_semantics_applied\":false,\"frame_rate_assigned\":false,\"rotation_codecs_decoded\":false,"
          "\"payload_aliases_may_be_counted_repeatedly\":true,\"slots\":"<<slots<<",\"null_slots\":"<<nullSlots
          <<",\"distinct_animation_offsets\":"<<animations.size()<<",\"track_record_occurrences\":"<<tracks
          <<",\"decoded_vector_track_occurrences\":"<<decodedTracks<<",\"unsupported_track_occurrences\":"<<unsupportedTracks
          <<",\"decoded_key_occurrences\":"<<keys<<",\"zero_delta_keys\":"<<zeroDeltas<<",\"tracks\":"<<out.str()<<"}\n";
    check(report.tellp()<=std::streamoff(32*1024*1024),"report budget");return report.str();
}
int main(int argc,char** argv){try{
    check(argc==4&&std::string(argv[2])=="--out","usage: stt-motion INPUT.lmt --out NEW_PRIVATE_DIRECTORY");
    fs::path input=argv[1],dest=fs::absolute(argv[3]);check(!fs::exists(dest),"destination exists");
    auto parent=fs::weakly_canonical(dest);while(!parent.empty()){check(!fs::exists(parent/".git"),"destination inside Git");auto next=parent.parent_path();if(next==parent)break;parent=next;}
    U size=fs::file_size(input);check(size<=32*1024*1024,"input budget");std::ifstream source(input,std::ios::binary);check(bool(source),"cannot open input read-only");
    Bytes b(static_cast<size_t>(size));if(size){source.read(reinterpret_cast<char*>(b.data()),static_cast<std::streamsize>(size));}check(bool(source),"input read failed");auto report=inspect(b);
    check(fs::create_directory(dest),"cannot create new output directory");std::ofstream output(dest/"report.json",std::ios::binary);output<<report;output.close();check(bool(output),"output write failed");
    std::cout<<"Partial vector-key inspection complete; playback unverified.\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
