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
using Mat = std::array<std::array<double,4>,4>;
using Vec = std::array<double,4>;
Mat product(const Mat& a,const Mat& b) {
    Mat out{};
    for(size_t i=0;i<4;++i) for(size_t j=0;j<4;++j) {
        for(size_t k=0;k<4;++k) out[i][j]+=a[i][k]*b[k][j];
        check(std::isfinite(out[i][j]),"rest diagnostic matrix overflow");
    }
    return out;
}
Vec transform(const Vec& v,const Mat& m) {
    Vec out{};
    for(size_t j=0;j<4;++j) {
        for(size_t k=0;k<4;++k) out[j]+=v[k]*m[k][j];
        check(std::isfinite(out[j]),"rest diagnostic position overflow");
    }
    return out;
}
struct RestDiagnostic {
    const char* status="disabled";
    std::vector<Mat> effective;
    Mat common{};
    U compared=0;
    double maxAbsolute=0,maxRelative=0;
    double commonDeterminant=0;
    bool determinantAvailable=false;
    void initialize(const Bytes& b,U at,const std::vector<U>& parents,U roots) {
        if(roots!=1) { status="unavailable_multiple_roots"; return; }
        const size_t count=parents.size();
        std::vector<Mat> local(count),bind(count),global(count);
        for(size_t i=0;i<count;++i) for(size_t r=0;r<4;++r) for(size_t c=0;c<4;++c) {
            local[i][r][c]=scalar(b,at+count*24+i*64+(r*4+c)*4);
            bind[i][r][c]=scalar(b,at+count*88+i*64+(r*4+c)*4);
        }
        for(size_t i=0;i<count;++i) for(size_t r=0;r<4;++r)
            if(local[i][r][3]!=(r==3?1.0:0.0)||bind[i][r][3]!=(r==3?1.0:0.0)) {
                status="unavailable_non_affine"; return;
            }
        std::vector<bool> ready(count,false);
        auto visit=[&](auto&& self,size_t i)->void {
            if(ready[i]) return;
            if(parents[i]==255) global[i]=local[i];
            else { self(self,size_t(parents[i])); global[i]=product(local[i],global[size_t(parents[i])]); }
            ready[i]=true;
        };
        effective.resize(count);
        for(size_t i=0;i<count;++i) { visit(visit,i); effective[i]=product(bind[i],global[i]); if(parents[i]==255) common=effective[i]; }
        commonDeterminant=common[0][0]*(common[1][1]*common[2][2]-common[1][2]*common[2][1])
            -common[0][1]*(common[1][0]*common[2][2]-common[1][2]*common[2][0])
            +common[0][2]*(common[1][0]*common[2][1]-common[1][1]*common[2][0]);
        check(std::isfinite(commonDeterminant),"rest diagnostic determinant overflow");
        determinantAvailable=true;
        if(commonDeterminant==0) { effective.clear(); status="unavailable_singular_common_transform"; return; }
        status="computed_under_hypothesis";
    }
    void observe(const Vec& position,const std::array<U,4>& slots,const std::array<U,4>& weights,size_t count) {
        if(effective.empty()) return;
        Vec actual{};
        for(size_t i=0;i<count;++i) if(weights[i]) {
            const auto p=transform(position,effective[size_t(slots[i])]);
            for(size_t j=0;j<4;++j) actual[j]+=double(weights[i])/255.0*p[j];
        }
        const auto expected=transform(position,common);
        double error=0,scale=1;
        for(size_t j=0;j<3;++j) {
            check(std::isfinite(actual[j]),"rest diagnostic blend overflow");
            error=std::max(error,std::abs(actual[j]-expected[j])); scale=std::max(scale,std::abs(expected[j]));
        }
        check(std::isfinite(error),"rest diagnostic residual overflow");
        maxAbsolute=std::max(maxAbsolute,error); maxRelative=std::max(maxRelative,error/scale); ++compared;
    }
    std::string json() const {
        std::ostringstream out; out << std::setprecision(17);
        out << "{\"status\":\"" << status << "\",\"compared_records\":" << compared;
        out << ",\"common_linear_determinant\":";
        if(determinantAvailable) out << commonDeterminant; else out << "null";
        if(compared) out << ",\"max_absolute_xyz_error\":" << maxAbsolute << ",\"max_relative_xyz_error\":" << maxRelative;
        else out << ",\"max_absolute_xyz_error\":null,\"max_relative_xyz_error\":null";
        out << ",\"palette_identity_verified\":false,\"weight_distribution_verified\":false,"
            "\"hypothesis\":\"row_vectors; global=local*parent_global; effective=B*global; compare blend to p*root_effective\"}";
        return out.str();
    }
};
std::string inspect(const Bytes& b,bool restEnabled) {
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
    std::vector<U> parents,indexIds;
    std::set<U> distinctIndexIds;
    bool indexIdsEqualSlots=true;
    U roots=0,maxDepth=0;
    for(U i=0;i<bones;++i) {
        const U indexId=number(b,boneAt+i*24,1);
        indexIds.push_back(indexId); distinctIndexIds.insert(indexId); indexIdsEqualSlots=indexIdsEqualSlots&&indexId==i;
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
    RestDiagnostic rest;
    if(restEnabled) rest.initialize(b,boneAt,parents,roots);
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
    U supported=0,unsupported=0,processed=0,vertices=0,referenced=0,zeroUnused=0,active=0,referencedActive=0;
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
        const bool two32=fmt==0x43fb3015||fmt==0x7ba7401b;
        const bool known=four||two32||fmt==0xd6784014;
        if(mesh) details << ',';
        details << "{\"mesh\":" << mesh << ",\"format\":" << fmt << ",\"supported\":" << (known?"true":"false")
            << ",\"stride\":" << stride << ",\"vertex_records\":" << nv << ",\"index_count\":" << ni
            << ",\"weight_count_raw\":" << weightCount << ",\"palette_index_raw\":" << paletteIndex << '}';
        if(!known) { ++unsupported; continue; }
        check(stride==(four?36:(two32?32:28)),"format stride");
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
            std::array<U,4> boneSlots{},weightBytes{};
            U sum=0,nactive=0;
            for(size_t i=0;i<(four?4u:2u);++i) {
                const U index=number(b,p+offsetsI[i],1),weight=number(b,p+offsetsW[i],1); sum+=weight;
                weightBytes[i]=weight;
                if(weight) {
                    ++nactive;
                    check(index<(skins?palettes[size_t(paletteIndex)].size():bones),"active influence palette reference");
                    boneSlots[i]=skins?palettes[size_t(paletteIndex)][size_t(index)]:index;
                }
            }
            check(nactive<=weightCount,"active weights exceed field");
            if(used[size_t(vertex)]) {
                check(sum==255,"referenced vertex weight sum is not 255"); ++referenced; referencedActive+=nactive;
                if(restEnabled) rest.observe({scalar(b,p),scalar(b,p+4),scalar(b,p+8),1.0},boneSlots,weightBytes,four?4u:2u);
            }
            else if(!sum) ++zeroUnused;
            active+=nactive;
        }
    }
    check(supported>0,"no supported weighted mesh");
    check(referenced>0,"no referenced vertex in supported meshes"); details << ']';
    std::ostringstream out;
    std::ostringstream ids; ids << '[';
    for(size_t i=0;i<indexIds.size();++i) { if(i) ids << ','; ids << indexIds[i]; }
    ids << ']';
    out << "{\"schema\":1,\"inspection_only\":true,\"functional_skinning_verified\":false,\"matrix_inverses_verified\":false,"
        "\"palette_semantics_verified\":false,\"global_remap_interpreted\":false,\"geometry_exported\":false,"
        "\"vertex_counts_are_window_occurrences\":true,\"has_unsupported_meshes\":" << (unsupported?"true":"false")
        << ",\"declared_vertices_raw\":" << declaredV << ",\"declared_indices_raw\":" << declaredI
        << ",\"bone_count\":" << bones << ",\"roots\":" << roots << ",\"max_depth\":" << maxDepth
        << ",\"bone_index_ids_raw\":" << ids.str() << ",\"bone_index_ids_unique\":" << (distinctIndexIds.size()==indexIds.size()?"true":"false")
        << ",\"bone_index_ids_equal_slots\":" << (indexIdsEqualSlots?"true":"false")
        << ",\"parent_references_use_record_slots\":true,\"motion_association_verified\":false"
        << ",\"skin_palettes\":" << skins << ",\"supported_meshes\":" << supported << ",\"unsupported_meshes\":" << unsupported
        << ",\"supported_vertex_records\":" << vertices << ",\"referenced_vertex_records\":" << referenced
        << ",\"unused_zero_weight_records\":" << zeroUnused << ",\"active_influences\":" << active
        << ",\"referenced_active_influences\":" << referencedActive
        << ",\"global_index_shortfall_bytes\":" << shortfall << ",\"meshes\":" << details.str()
        << ",\"rest_pose_diagnostic\":" << rest.json() << "}\n";
    return out.str();
}
int main(int argc,char** argv) {
    try {
        check((argc==4||argc==5)&&std::string(argv[2])=="--out"&&(argc==4||std::string(argv[4])=="--check-rest-pose"),
            "usage: stt-skin INPUT.mod --out NEW_PRIVATE_DIRECTORY [--check-rest-pose]");
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
        check(bool(source),"source read failed"); const auto result=inspect(bytes,argc==5);
        check(fs::create_directory(dest),"cannot create output directory");
        std::ofstream output(dest/"report.json",std::ios::binary); output << result; output.close(); check(bool(output),"output write failed");
        std::cout << "Inspection complete; no functional skinning claim.\n"; return 0;
    } catch(const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
