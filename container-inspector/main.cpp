#include <array>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <memory>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <zlib.h>
#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#else
#include <openssl/evp.h>
#include <openssl/bn.h>
#endif
using U = std::uint64_t;
using Header = std::array<unsigned char,512>;
void require(bool ok, const char* message) { if (!ok) throw std::runtime_error(message); }
std::string hex(const unsigned char* p, size_t n) {
    std::ostringstream s;
    for(size_t i=0;i<n;++i) s<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(p[i]);
    return s.str();
}
struct Hash {
#ifdef _WIN32
    BCRYPT_ALG_HANDLE alg=nullptr;
    BCRYPT_HASH_HANDLE hash=nullptr;
    Hash() {
        require(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,nullptr,0)==0,"SHA256 init");
        if(BCryptCreateHash(alg,&hash,nullptr,0,nullptr,0,0)!=0) {
            BCryptCloseAlgorithmProvider(alg,0); throw std::runtime_error("SHA256 init");
        }
    }
    ~Hash() { BCryptDestroyHash(hash); BCryptCloseAlgorithmProvider(alg,0); }
    void add(unsigned char* p, size_t n) { require(BCryptHashData(hash,p,static_cast<ULONG>(n),0)==0,"SHA256 update"); }
    std::string finish() { unsigned char out[32]; require(BCryptFinishHash(hash,out,32,0)==0,"SHA256 finish"); return hex(out,32); }
#else
    EVP_MD_CTX* ctx=EVP_MD_CTX_new();
    Hash() { if(!ctx) throw std::runtime_error("SHA256 allocation"); if(EVP_DigestInit_ex(ctx,EVP_sha256(),nullptr)!=1) { EVP_MD_CTX_free(ctx); throw std::runtime_error("SHA256 init"); } }
    ~Hash() { EVP_MD_CTX_free(ctx); }
    void add(unsigned char* p,size_t n) { require(EVP_DigestUpdate(ctx,p,n)==1,"SHA256 update"); }
    std::string finish() { unsigned char out[32]; unsigned n=0; require(EVP_DigestFinal_ex(ctx,out,&n)==1 && n==32,"SHA256 finish"); return hex(out,32); }
#endif
    Hash(const Hash&)=delete;
    Hash& operator=(const Hash&)=delete;
};
struct Reader {
    std::ifstream f;
    U size;
    explicit Reader(const char* path):f(path,std::ios::binary) {
        require(bool(f),"cannot open input");
        f.seekg(0,std::ios::end); auto end=f.tellg();
        require(end>=0,"cannot determine size"); size=static_cast<U>(end);
    }
    void read(U offset, unsigned char* p,size_t n) {
        require(offset<=size && n<=size-offset,"truncated input");
        f.clear(); f.seekg(static_cast<std::streamoff>(offset));
        f.read(reinterpret_cast<char*>(p),static_cast<std::streamsize>(n));
        require(bool(f),"input read failed");
    }
    Header header(U offset) { Header h{}; read(offset,h.data(),h.size()); return h; }
    std::string digest(U offset,U n) {
        require(offset<=size && n<=size-offset,"hash outside file");
        Hash hash; std::array<unsigned char,65536> block{};
        while(n) { auto count=static_cast<size_t>(std::min<U>(n,block.size())); read(offset,block.data(),count); hash.add(block.data(),count); offset+=count; n-=count; }
        return hash.finish();
    }
};
U le(const Header& h,size_t pos,size_t n=4) { U v=0; for(size_t i=0;i<n;++i) v|=U(h.at(pos+i))<<(8*i); return v; }
bool magic(const Header& h,const char* s) { return std::equal(h.begin()+256,h.begin()+260,s); }
U scale(U value,unsigned exponent) {
    require(exponent<=22,"unsupported media unit exponent");
    return value*(U(512)<<exponent); // 32-bit fields times at most 2^31: no overflow.
}
struct Range { U offset,size; };
void range(U offset,U size,U limit) { require(offset<=limit && size<=limit-offset,"range outside declared container"); }
void disjoint(const std::vector<Range>& ranges) {
    for(size_t i=0;i<ranges.size();++i) for(size_t j=0;j<i;++j)
        require(ranges[i].offset>=ranges[j].offset+ranges[j].size || ranges[j].offset>=ranges[i].offset+ranges[i].size,"overlapping regions");
}
U aligned(U n,U unit) {
    require(n<=std::numeric_limits<U>::max()-(unit-1),"alignment overflow");
    return ((n+unit-1)/unit)*unit;
}
U checked_add(U a,U b) {
    require(a<=std::numeric_limits<U>::max()-b,"offset overflow");
    return a+b;
}
void verify_ivfc(Reader& r,U base,U size,std::ostream& out) {
    require(size>=96,"short IVFC"); Header h{}; r.read(base,h.data(),96);
    require(std::equal(h.begin(),h.begin()+4,"IVFC") && le(h,4)==0x10000,"unsupported IVFC integrity profile");
    std::array<U,3> logical{},length{},block{},physical{};
    for(size_t i=0;i<3;++i) {
        size_t p=12+24*i;
        logical[i]=le(h,p,8); length[i]=le(h,p+8,8); U exponent=le(h,p+16);
        require(exponent>=9 && exponent<=20,"unsupported IVFC block size");
        block[i]=U(1)<<exponent;
        require(length[i]>0,"empty IVFC level");
    }
    U master=le(h,8); require(master>0 && master%32==0,"invalid IVFC master hash size");
    range(96,master,size);
    require(logical[0]==0 && logical[1]==aligned(length[0],block[0])
        && logical[2]==checked_add(logical[1],aligned(length[1],block[1])),"unsupported IVFC logical layout");
    physical[2]=aligned(96+master,block[2]);
    range(physical[2],aligned(length[2],block[2]),size);
    physical[0]=checked_add(physical[2],aligned(length[2],block[2]));
    range(physical[0],aligned(length[0],block[0]),size);
    physical[1]=checked_add(physical[0],aligned(length[0],block[0]));
    range(physical[1],aligned(length[1],block[1]),size);
    U budget=0;
    for(size_t i=0;i<3;++i) {
        U count=aligned(length[i],block[i])/block[i];
        U parentOffset=i==0?96:physical[i-1];
        U parentLength=i==0?master:length[i-1];
        require(count<=parentLength/32,"IVFC parent hash table too short");
        require(count<=8000000-budget,"IVFC block budget exceeded"); budget+=count;
        for(U j=0;j<count;++j) {
            std::array<unsigned char,32> expected{};
            r.read(base+parentOffset+j*32,expected.data(),expected.size());
            auto actual=r.digest(base+physical[i]+j*block[i],block[i]);
            if(actual!=hex(expected.data(),expected.size()))
                throw std::runtime_error("IVFC level "+std::to_string(i+1)+" block "+std::to_string(j)+" SHA256 mismatch");
        }
        out<<"ivfc_level="<<i+1<<" hash=verified blocks="<<count<<" block_bytes="<<block[i]<<"\n";
    }
    out<<"ivfc_tree=verified levels=3 blocks="<<budget<<" authenticity=not_established\n";
}
void verify_exefs(Reader& r,U base,U size,std::ostream& out) {
    require(size>=512,"short ExeFS"); auto h=r.header(base);
    std::vector<Range> files; std::set<std::string> names; U count=0;
    for(size_t i=0;i<10;++i) {
        size_t p=i*16;
        bool unused=std::all_of(h.begin()+p,h.begin()+p+16,[](unsigned char c){return c==0;});
        if(unused) continue;
        size_t n=0; while(n<8 && h[p+n]) ++n;
        require(n>0,"empty ExeFS filename");
        for(size_t j=0;j<n;++j) require(h[p+j]>=33 && h[p+j]<127 && h[p+j]!=34
            && h[p+j]!=47 && h[p+j]!=92,"unsupported ExeFS filename");
        for(size_t j=n;j<8;++j) require(h[p+j]==0,"invalid ExeFS filename padding");
        std::string name(reinterpret_cast<const char*>(h.data()+p),n);
        require(names.insert(name).second,"duplicate ExeFS filename");
        U offset=le(h,p+8),length=le(h,p+12); range(offset,length,size-512);
        if(length) files.push_back({512+offset,length});
        auto actual=r.digest(base+512+offset,length);
        if(actual!=hex(h.data()+0x1e0-i*32,32))
            throw std::runtime_error("ExeFS "+name+" SHA256 mismatch");
        out<<"exefs_file name="<<name<<" size="<<length<<" hash=verified\n"; ++count;
    }
    disjoint(files);
    out<<"exefs_files=verified count="<<count<<"\n";
}

struct Options { bool verify=false, list=false, integrity=false, index=false, signatures=false, resources=false, decompress=false; };
U rawle(const std::vector<unsigned char>& b,U p,size_t n=4) {
    range(p,n,b.size()); U v=0;
    for(size_t i=0;i<n;++i) v|=U(b[static_cast<size_t>(p)+i])<<(8*i);
    return v;
}
#include "decompression.hpp"
#include "signature_resource.hpp"
struct Node { U parent,next,child,file,offset,size,hashNext; std::uint32_t pathHash; std::string name; };
std::string name16(const std::vector<unsigned char>& b,U p,U n) {
    require(n%2==0 && n<=1024,"invalid RomFS name length"); range(p,n,b.size());
    std::string s;
    // Escaped UTF-16 code units keep the report ASCII and prevent injected lines.
    for(U i=0;i<n;i+=2) {
        U c=rawle(b,p+i,2);
        require(c!=0 && c!=47 && c!=92,"invalid RomFS path component");
        if(c>=32 && c<127 && c!=34) s+=static_cast<char>(c);
        else { std::ostringstream t; t<<"\\u"<<std::hex<<std::setw(4)<<std::setfill('0')<<c; s+=t.str(); }
    }
    require(s!="." && s!="..","invalid RomFS dot component"); return s;
}

void verify_buckets(Reader& r,U base,U offset,U size,const std::map<U,Node>& nodes,
                    const char* label,std::ostream& out) {
    require(size%4==0 && size<=4*1024*1024,"RomFS hash bucket budget exceeded");
    U count=size/4;
    require(count>0 || nodes.empty(),"missing RomFS hash table");
    std::vector<unsigned char> heads(static_cast<size_t>(size));
    if(size) r.read(base+offset,heads.data(),heads.size());
    std::set<U> seen; U used=0,maxChain=0;
    for(U i=0;i<count;++i) {
        U current=rawle(heads,i*4),chain=0;
        if(current!=0xffffffff) ++used;
        while(current!=0xffffffff) {
            require(nodes.count(current)>0,"RomFS bucket link is not a record boundary");
            require(seen.insert(current).second,"RomFS cyclic/shared bucket link");
            const auto& node=nodes.at(current);
            require(node.pathHash%count==i,"RomFS name in wrong hash bucket");
            current=node.hashNext; ++chain;
        }
        maxChain=std::max(maxChain,chain);
    }
    require(seen.size()==nodes.size(),"RomFS records missing from hash buckets");
    out<<"romfs_index type="<<label<<" hash_buckets=verified buckets="<<count
       <<" used="<<used<<" entries="<<seen.size()<<" max_chain="<<maxChain<<"\n";
}

void romfs(Reader& r,U base,U size,std::ostream& out,bool treeVerified=false,bool printFiles=true,bool verifyIndex=false,bool resources=false,bool decompress=false) {
    require(size>=0x60,"short IVFC"); Header iv{}; r.read(base,iv.data(),0x60);
    require(std::equal(iv.begin(),iv.begin()+4,"IVFC") && le(iv,4)==0x10000,"unsupported IVFC");
    U exponent=le(iv,0x4c); require(exponent>=9 && exponent<=20,"unsupported IVFC block size");
    U block=U(1)<<exponent, master=le(iv,8);
    U start=((0x60+master+block-1)/block)*block;
    U length=le(iv,0x44,8); range(start,length,size); require(length>=40,"short RomFS level3");
    Header h{}; r.read(base+start,h.data(),40); require(le(h,0)==40,"invalid RomFS level3 header");
    U end=40;
    for(size_t p=4;p<=28;p+=8) {
        U off=le(h,p),n=le(h,p+4); range(off,n,length);
        require(off>=end && off%4==0 && n%4==0,"invalid RomFS tables");
        end=off+n;
    }
    U data=le(h,36); require(data>=end && data<=length && data%16==0,"invalid RomFS data offset");
    U dm=le(h,16),fm=le(h,32);
    require(dm>=24 && dm+fm<=64*1024*1024,"RomFS metadata budget exceeded");
    std::vector<unsigned char> dirs(static_cast<size_t>(dm)),files(static_cast<size_t>(fm));
    r.read(base+start+le(h,12),dirs.data(),dirs.size());
    if(fm) r.read(base+start+le(h,28),files.data(),files.size());
    std::map<U,Node> dn,fn;
    auto parse=[&](const std::vector<unsigned char>& b,bool isdir,std::map<U,Node>& nodes) {
        U fixed=isdir?24:32;
        for(U p=0;p<b.size();) {
            range(p,fixed,b.size()); U n=rawle(b,p+fixed-4);
            range(p+fixed,n,b.size()); require(n%2==0,"odd UTF16 name size");
            Node node{}; node.parent=rawle(b,p); node.next=rawle(b,p+4);
            node.name=name16(b,p+fixed,n);
            node.hashNext=rawle(b,p+(isdir?16:24));
            node.pathHash=static_cast<std::uint32_t>(node.parent)^123456789u;
            for(U j=0;j<n;j+=2) {
                node.pathHash=(node.pathHash>>5)|(node.pathHash<<27);
                node.pathHash^=static_cast<std::uint32_t>(rawle(b,p+fixed+j,2));
            }
            if(isdir) { node.child=rawle(b,p+8); node.file=rawle(b,p+12); }
            else { node.offset=rawle(b,p+8,8); node.size=rawle(b,p+16,8); range(node.offset,node.size,length-data); }
            nodes.emplace(p,node); require(nodes.size()<=100000,"RomFS entry budget exceeded");
            p+=fixed+((n+3)/4)*4; require(p<=b.size(),"truncated metadata padding");
        }
    };
    parse(dirs,true,dn); parse(files,false,fn);
    if(verifyIndex) {
        verify_buckets(r,base+start,le(h,4),le(h,8),dn,"directories",out);
        verify_buckets(r,base+start,le(h,20),le(h,24),fn,"files",out);
    }
    require(dn.count(0) && dn.at(0).parent==0 && dn.at(0).name.empty() && dn.at(0).next==0xffffffff,"invalid RomFS root");
    struct Work { U id,parent,depth; std::string path; };
    std::vector<Work> pending{{0,0,0,""}};
    std::set<U> seenDirs,seenFiles;
    U total=0,reportBytes=0,pendingBytes=0; ResourceStats resourceStats;
    while(!pending.empty()) {
        auto w=pending.back(); pending.pop_back(); pendingBytes-=w.path.size();
        require(w.depth<=128 && w.path.size()<=8192,"RomFS path budget exceeded");
        require(dn.count(w.id) && seenDirs.insert(w.id).second,"invalid/cyclic RomFS directory link");
        const auto& d=dn.at(w.id); require(d.parent==w.parent,"RomFS directory parent mismatch");
        std::set<std::string> names;
        U f=d.file;
        while(f!=0xffffffff) {
            require(fn.count(f) && seenFiles.insert(f).second,"invalid/cyclic RomFS file link");
            const auto& file=fn.at(f); require(file.parent==w.id && !file.name.empty(),"RomFS file parent/name mismatch");
            require(names.insert(file.name).second,"duplicate RomFS name");
            require(w.path.size()+1+file.name.size()<=8192,"RomFS complete path budget exceeded");
            require(total<=std::numeric_limits<U>::max()-file.size,"RomFS total overflow"); total+=file.size;
            reportBytes+=w.path.size()+file.name.size()+128;
            require(reportBytes<=32*1024*1024,"RomFS report budget exceeded");
            if(resources) inspect_resource(r,base+start+data+file.offset,file.size,resourceStats,decompress);
            if(printFiles) out<<"romfs_file path=\""<<w.path<<"/"<<file.name<<"\" size="<<file.size
               <<" absolute_offset="<<base+start+data+file.offset<<"\n";
            f=file.next;
        }
        std::set<U> siblings;
        U child=d.child;
        while(child!=0xffffffff) {
            require(dn.count(child) && siblings.insert(child).second,"invalid/cyclic RomFS sibling link");
            const auto& c=dn.at(child); require(!c.name.empty() && names.insert(c.name).second,"duplicate/empty RomFS directory name");
            require(w.path.size()+1+c.name.size()<=8192,"RomFS complete path budget exceeded");
            pendingBytes+=w.path.size()+1+c.name.size();
            require(pendingBytes<=32*1024*1024,"RomFS pending paths budget exceeded");
            pending.push_back({child,w.id,w.depth+1,w.path+"/"+c.name});
            require(pending.size()<=100000,"RomFS work budget exceeded"); child=c.next;
        }
    }
    require(seenDirs.size()==dn.size() && seenFiles.size()==fn.size(),"unreachable RomFS metadata");
    if(resources) resource_report(resourceStats,out,decompress);
    out<<"romfs_summary directories="<<dn.size()<<" files="<<fn.size()<<" file_bytes="<<total
       <<" ivfc_tree="<<(treeVerified?"verified":"not_verified")<<" hash_buckets="<<(verifyIndex?"verified":"not_verified")<<"\n";
}
void verify_region(Reader& r,U offset,U length,const Header& h,size_t stored,const char* label,std::ostream& out,bool present=false) {
    if(!length) {
        out<<label<<"_hash="<<(present?"not_verified_empty_hash_range":"absent")<<"\n";
        return;
    }
    auto actual=r.digest(offset,length); auto expected=hex(h.data()+stored,32);
    if(actual!=expected) throw std::runtime_error(std::string(label)+" SHA256 mismatch");
    out<<label<<"_hash=verified bytes="<<length<<"\n";
}

void ncch(Reader& r,U base,U available,std::ostream& out,const Options& options) {
    require(available>=512,"short NCCH");
    auto h=r.header(base); require(magic(h,"NCCH"),"partition is not NCCH");
    unsigned exp=h[0x18e]; U size=scale(le(h,0x104),exp);
    require(size>=512 && size<=available,"invalid NCCH size");
    bool encrypted=(h[0x18f]&4)==0;
    out<<"NCCH offset="<<base<<" size="<<size<<" version="<<le(h,0x112,2)
       <<" partition_id_le="<<le(h,0x108,8)<<" program_id_le="<<le(h,0x118,8)
       <<" flags="<<hex(h.data()+0x188,8)<<" encrypted_declared="<<encrypted
       <<" fixed_key_flag="<<bool(h[0x18f]&1)<<" seed_flag="<<bool(h[0x18f]&0x20)
       <<" crypto_method="<<unsigned(h[0x18b])<<"\n";
    std::vector<Range> regions{{0,512}};
    U ex=le(h,0x180);
    if(ex) { require(ex==0x400,"unsupported extended header size"); range(512,0x800,size); regions.push_back({512,0x800}); }
    if(options.signatures) inspect_signature(r,base,h,encrypted,ex,out);
    const char* names[]={"plain","logo","exefs","romfs"};
    const size_t fields[]={0x190,0x198,0x1a0,0x1b0};
    for(size_t i=0;i<4;++i) {
        auto p=fields[i]; U off=scale(le(h,p),exp), len=scale(le(h,p+4),exp);
        require((off==0)==(len==0),"inconsistent region offset/size");
        range(off,len,size); if(len) { require(off>=512,"region overlaps header"); regions.push_back({off,len}); }
        out<<names[i]<<" offset="<<off<<" size="<<len<<"\n";
        if(i>=2) require(scale(le(h,p+8),exp)<=len,"hash region exceeds region");
    }
    disjoint(regions);
    out<<"logo_sha256_stored="<<hex(h.data()+0x130,32)<<"\n"
       <<"exheader_sha256_stored="<<hex(h.data()+0x160,32)<<"\n"
       <<"exefs_sha256_stored="<<hex(h.data()+0x1c0,32)<<"\n"
       <<"romfs_sha256_stored="<<hex(h.data()+0x1e0,32)<<"\n"
       <<"stored_hashes="<<(options.verify?"reported comparisons=per_region":"reported_only")
       <<" signatures="<<(options.signatures?"per_partition":"not_verified")<<"\n";
    if(options.verify) {
        U logo=scale(le(h,0x19c),exp);
        verify_region(r,base+scale(le(h,0x198),exp),logo,h,0x130,"logo",out);
        if(encrypted) out<<"content_hashes=skipped_encrypted\n";
        else {
            verify_region(r,base+512,ex,h,0x160,"exheader",out);
            verify_region(r,base+scale(le(h,0x1a0),exp),scale(le(h,0x1a8),exp),h,0x1c0,"exefs",out,le(h,0x1a4)!=0);
            verify_region(r,base+scale(le(h,0x1b0),exp),scale(le(h,0x1b8),exp),h,0x1e0,"romfs_superblock",out,le(h,0x1b4)!=0);
        }
    }
    if(options.integrity) {
        if(encrypted) out<<"file_integrity=skipped_encrypted\n";
        else {
            if(le(h,0x1a4)) {
                require(scale(le(h,0x1a8),exp)>=512,"ExeFS header hash coverage missing");
                verify_exefs(r,base+scale(le(h,0x1a0),exp),scale(le(h,0x1a4),exp),out);
            }
            if(le(h,0x1b4)) {
                U off=scale(le(h,0x1b0),exp),len=scale(le(h,0x1b4),exp);
                require(len>=96,"short IVFC");
                Header iv{}; r.read(base+off,iv.data(),96);
                require(scale(le(h,0x1b8),exp)>=96+le(iv,8),"IVFC master hash coverage missing");
                verify_ivfc(r,base+off,len,out);
            }
        }
    }
    if((options.list || options.index || options.resources) && le(h,0x1b4)) {
        if(encrypted) out<<(options.index?"romfs_index":"romfs_listing")<<"=skipped_encrypted\n";
        else romfs(r,base+scale(le(h,0x1b0),exp),scale(le(h,0x1b4),exp),out,options.integrity,options.list,options.index,options.resources,options.decompress);
    }

}
int main(int argc,char** argv) {
    Options options;
    if(argc<2) { std::cerr<<"usage: stt-inspect input [--verify] [--list-romfs] [--verify-integrity] [--verify-romfs-index] [--inspect-signatures] [--inspect-resources] [--validate-arc-zlib]\n"; return 2; }
    for(int i=2;i<argc;++i) {
        std::string arg=argv[i];
        if(arg=="--verify") options.verify=true;
        else if(arg=="--list-romfs") options.list=true;
        else if(arg=="--verify-integrity") { options.integrity=true; options.verify=true; }
        else if(arg=="--verify-romfs-index") { options.index=true; options.integrity=true; options.verify=true; }
        else if(arg=="--inspect-signatures") options.signatures=true;
        else if(arg=="--validate-arc-zlib") { options.decompress=true; options.resources=true; options.index=true; options.integrity=true; options.verify=true; }
        else if(arg=="--inspect-resources") { options.resources=true; options.index=true; options.integrity=true; options.verify=true; }
        else { std::cerr<<"unknown option\n"; return 2; }
    }
    try {
        Reader r(argv[1]); auto h=r.header(0); std::ostringstream report;
        if(magic(h,"NCCH")) ncch(r,0,r.size,report,options);
        else {
            require(magic(h,"NCSD"),"unsupported magic");
            U declared=scale(le(h,0x104),h[0x18e]);
            require(declared>=512,"invalid NCSD size");
            report<<"NCSD declared_size="<<declared<<" actual_size="<<r.size
                  <<" trimmed="<<(r.size<declared)<<" flags="<<hex(h.data()+0x188,8)<<"\n";
            require(r.size<=declared,"file exceeds declared NCSD size");
            if(options.signatures) report<<"ncsd_signature=not_checked_no_trust_anchor authenticity=not_established\n";
            std::vector<Range> parts;
            for(size_t i=0;i<8;++i) {
                U off=scale(le(h,0x120+i*8),h[0x18e]),len=scale(le(h,0x124+i*8),h[0x18e]);
                require((off==0)==(len==0),"inconsistent partition offset/size");
                if(!len) continue;
                range(off,len,declared); range(off,len,r.size);
                require(off>=512,"partition overlaps header"); parts.push_back({off,len});
                report<<"partition="<<i<<" offset="<<off<<" size="<<len
                      <<" filesystem_type="<<unsigned(h[0x110+i])<<" crypto_type="<<unsigned(h[0x118+i])<<"\n";
                ncch(r,off,len,report,options);
            }
            require(!parts.empty(),"NCSD has no partitions"); disjoint(parts);
        }
        report<<"file_size="<<r.size<<" file_sha256="<<r.digest(0,r.size)<<"\n";
        std::cout<<report.str(); return 0;
    } catch(const std::exception& e) { std::cerr<<"invalid/unsupported: "<<e.what()<<"\n"; return 1; }
}
