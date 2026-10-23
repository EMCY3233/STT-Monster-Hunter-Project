#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace fs = std::filesystem;
using U = uint64_t;
using Bytes = std::vector<unsigned char>;
void check(bool ok, const char* why) { if (!ok) throw std::runtime_error(why); }
void span(U at, U n, U size) { check(at <= size && n <= size-at, "range outside input"); }
U number(const Bytes& b, U at, unsigned width=4) {
    span(at,width,b.size()); U out=0;
    for(unsigned i=0;i<width;++i) out |= U(b[size_t(at)+i]) << (8*i);
    return out;
}
float scalar(const Bytes& b,U at) {
    const uint32_t bits=uint32_t(number(b,at)); float out;
    std::memcpy(&out,&bits,4); check(std::isfinite(out),"nonfinite scalar"); return out;
}
struct Region { U at,size; };
void disjoint(std::vector<Region> r) {
    r.erase(std::remove_if(r.begin(),r.end(),[](Region x){return !x.size;}),r.end());
    std::sort(r.begin(),r.end(),[](Region a,Region b){return a.at<b.at;});
    for(size_t i=1;i<r.size();++i) check(r[i].at>=r[i-1].at+r[i-1].size,"overlapping tables");
}
std::string inspect(const Bytes& b) {
    span(0,128,b.size()); check(number(b,0)==0x00444f4d && number(b,4,2)==230,"requires little-endian MOD230");
    const U bones=number(b,6,2),meshes=number(b,8,2),materials=number(b,10,2);
    const U declaredV=number(b,12),declaredI=number(b,16),vbSize=number(b,24),groups=number(b,32),skins=number(b,36);
    const U boneAt=number(b,40),groupAt=number(b,44),matAt=number(b,48),meshAt=number(b,52),vbAt=number(b,56),ibAt=number(b,60);
    check(bones>0&&bones<=255&&meshes>0&&meshes<=4096&&materials<=4096&&groups<=4096&&skins<=256,"count budget");
    check(declaredV<=1000000&&declaredI<=4000000,"vertex/index count budget");
    const U skeletonSize=bones*152+256+skins*28;
    std::vector<Region> regions={{0,128},{boneAt,skeletonSize},{groupAt,groups*32},{matAt,materials*128},{meshAt,meshes*48},{vbAt,vbSize}};
    for(const auto& r:regions) span(r.at,r.size,b.size());
    check(ibAt<=b.size(),"index pointer");
    const U available=std::min(declaredI*2,U(b.size())-ibAt),shortfall=declaredI*2-available;
    check(shortfall==0||shortfall==2,"unsupported global index shortfall");
    regions.push_back({ibAt,available}); disjoint(regions);
    std::vector<U> parents;
    U roots=0,maxDepth=0;
    for(U i=0;i<bones;++i) {
        const U parent=number(b,boneAt+i*24+1,1);
        check(parent==255||parent<bones,"parent outside bone slots"); parents.push_back(parent); roots+=parent==255;
        for(U j=0;j<5;++j) scalar(b,boneAt+i*24+4+j*4);
    }
    check(roots>0,"no root");
    for(U i=0;i<bones;++i) {
        std::set<U> seen; U current=i,depth=0;
        while(parents[size_t(current)]!=255) {
            check(seen.insert(current).second,"parent cycle"); current=parents[size_t(current)]; ++depth;
        }
        maxDepth=std::max(maxDepth,depth);
    }
    for(U i=0;i<bones*32;++i) scalar(b,boneAt+bones*24+i*4);
    const U paletteAt=boneAt+bones*152+256;
    std::vector<std::vector<U>> palettes;
    for(U i=0;i<skins;++i) {
        const U count=number(b,paletteAt+i*28); check(count<=24,"palette capacity");
        std::vector<U> slots;
        for(U j=0;j<count;++j) {
            const U slot=number(b,paletteAt+i*28+4+j,1); check(slot<bones,"palette bone slot"); slots.push_back(slot);
        }
        palettes.push_back(slots);
    }
    std::set<U> groupIds;
    for(U i=0;i<groups;++i) check(groupIds.insert(number(b,groupAt+i*32)).second,"duplicate group id");
    U supported=0,unsupported=0,processed=0,vertices=0,referenced=0,zeroUnused=0,active=0;
    std::ostringstream details; details << '[';
    for(U mesh=0;mesh<meshes;++mesh) {
        const U at=meshAt+mesh*48,nv=number(b,at+2,2),d0=number(b,at+4),d1=number(b,at+8);
        const U start=number(b,at+12),stream=number(b,at+16),fmt=number(b,at+20),indexStart=number(b,at+24),ni=number(b,at+28),adjust=number(b,at+32);
        const U stride=(d1>>16)&255,weightCount=(d1>>3)&31,paletteIndex=number(b,at+37,1);
        check(groupIds.count(d0&4095)>0&&((d0>>12)&4095)<materials,"mesh group/material reference");
        check(stride>0,"zero stride"); const U vstart=vbAt+(start+adjust)*stride+stream;
        check(vstart>=vbAt,"vertex start"); span(vstart-vbAt,nv*stride,vbSize);
        span(indexStart,ni,declaredI); span(ibAt+indexStart*2,ni*2,b.size());
        processed+=ni; check(processed<=1000000,"aggregate index budget");
        const bool four=fmt==0x01b36016||fmt==0xf606f017;
        const bool known=four||fmt==0xd6784014;
        if(mesh) details << ',';
        details << "{\"mesh\":" << mesh << ",\"format\":" << fmt << ",\"supported\":" << (known?"true":"false")
            << ",\"stride\":" << stride << ",\"vertex_records\":" << nv << ",\"index_count\":" << ni
            << ",\"weight_count_raw\":" << weightCount << ",\"palette_index_raw\":" << paletteIndex << '}';
        if(!known) { ++unsupported; continue; }
        check(stride==(four?36:28),"format stride");
        check(((d1>>24)&63)==4,"requires triangle strip primitive 4");
        check(weightCount>0&&weightCount<=(four?4:2),"weight count field");
        check(!skins||paletteIndex<skins,"mesh palette index");
        std::vector<bool> used(size_t(nv),false);
        for(U i=0;i<ni;++i) {
            const U index=number(b,ibAt+(indexStart+i)*2,2);
            if(index==65535) continue;
            check(index>=start&&index-start<nv,"mesh vertex index"); used[size_t(index-start)]=true;
        }
        ++supported; vertices+=nv; check(vertices<=250000,"aggregate vertex budget");
        for(U vertex=0;vertex<nv;++vertex) {
            const U p=vstart+vertex*stride;
            for(U off:{U(0),U(4),U(8),U(16),U(20)}) scalar(b,p+off);
            const std::array<U,4> offsetsI={24,25,32,33},offsetsW={26,27,34,35};
            U sum=0,nactive=0;
            for(size_t i=0;i<(four?4u:2u);++i) {
                const U index=number(b,p+offsetsI[i],1),weight=number(b,p+offsetsW[i],1); sum+=weight;
                if(weight) {
                    ++nactive;
                    check(index<(skins?palettes[size_t(paletteIndex)].size():bones),"active influence palette reference");
                }
            }
            check(nactive<=weightCount,"active weights exceed field");
            if(used[size_t(vertex)]) { check(sum==255,"referenced vertex weight sum is not 255"); ++referenced; }
            else if(!sum) ++zeroUnused;
            active+=nactive;
        }
    }
    check(supported>0,"no supported weighted mesh");
    check(referenced>0,"no referenced vertex in supported meshes"); details << ']';
    std::ostringstream out;
    out << "{\"schema\":1,\"inspection_only\":true,\"functional_skinning_verified\":false,\"matrix_inverses_verified\":false,"
        "\"palette_semantics_verified\":false,\"global_remap_interpreted\":false,\"geometry_exported\":false,"
        "\"vertex_counts_are_window_occurrences\":true,\"has_unsupported_meshes\":" << (unsupported?"true":"false")
        << ",\"declared_vertices_raw\":" << declaredV << ",\"declared_indices_raw\":" << declaredI
        << ",\"bone_count\":" << bones << ",\"roots\":" << roots << ",\"max_depth\":" << maxDepth
        << ",\"skin_palettes\":" << skins << ",\"supported_meshes\":" << supported << ",\"unsupported_meshes\":" << unsupported
        << ",\"supported_vertex_records\":" << vertices << ",\"referenced_vertex_records\":" << referenced
        << ",\"unused_zero_weight_records\":" << zeroUnused << ",\"active_influences\":" << active
        << ",\"global_index_shortfall_bytes\":" << shortfall << ",\"meshes\":" << details.str() << "}\n";
    return out.str();
}
int main(int argc,char** argv) {
    try {
        check(argc==4&&std::string(argv[2])=="--out","usage: stt-skin INPUT.mod --out NEW_PRIVATE_DIRECTORY");
        const fs::path input=argv[1],dest=fs::absolute(argv[3]);
        check(!fs::exists(dest),"destination exists");
        auto parent=fs::weakly_canonical(dest);
        while(!parent.empty()) {
            check(!fs::exists(parent/".git"),"destination inside Git");
            const auto next=parent.parent_path(); if(next==parent) break; parent=next;
        }
        const auto size=fs::file_size(input); check(size<=32*1024*1024,"input budget");
        std::ifstream source(input,std::ios::binary); check(bool(source),"cannot open source read-only");
        Bytes bytes(static_cast<size_t>(size)); if(size) source.read(reinterpret_cast<char*>(bytes.data()),static_cast<std::streamsize>(size));
        check(bool(source),"source read failed"); const auto result=inspect(bytes);
        check(fs::create_directory(dest),"cannot create output directory");
        std::ofstream output(dest/"report.json",std::ios::binary); output << result; output.close(); check(bool(output),"output write failed");
        std::cout << "Inspection complete; no functional skinning claim.\n"; return 0;
    } catch(const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
