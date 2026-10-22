#include <array>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#else
#include <openssl/evp.h>
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
#include <map>
#include <set>
struct Options { bool verify=false, list=false; };
U rawle(const std::vector<unsigned char>& b,U p,size_t n=4) {
    range(p,n,b.size()); U v=0;
    for(size_t i=0;i<n;++i) v|=U(b[static_cast<size_t>(p)+i])<<(8*i);
    return v;
}
struct Node { U parent,next,child,file,offset,size; std::string name; };
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
void romfs(Reader& r,U base,U size,std::ostream& out) {
    require(size>=0x60,"short IVFC"); Header iv{}; r.read(base,iv.data(),0x60);
    require(std::equal(iv.begin(),iv.begin()+4,"IVFC") && le(iv,4)==0x10000,"unsupported IVFC");
    U exponent=le(iv,0x4c); require(exponent>=9 && exponent<=20,"unsupported IVFC block size");
    U block=U(1)<<exponent, master=le(iv,8);
    U start=((0x60+master+block-1)/block)*block;
    U length=le(iv,0x44,8); range(start,length,size); require(length>=40,"short RomFS level3");
    Header h{}; r.read(base+start,h.data(),40); require(le(h,0)==40,"invalid RomFS level3 header");
    std::vector<Range> tables{{0,40}};
    U end=40;
    for(size_t p=4;p<=28;p+=8) {
        U off=le(h,p),n=le(h,p+4); range(off,n,length);
        require(off>=end && off%4==0 && n%4==0,"invalid RomFS tables");
        tables.push_back({off,n}); end=off+n;
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
            if(isdir) { node.child=rawle(b,p+8); node.file=rawle(b,p+12); }
            else { node.offset=rawle(b,p+8,8); node.size=rawle(b,p+16,8); range(node.offset,node.size,length-data); }
            nodes.emplace(p,node); require(nodes.size()<=100000,"RomFS entry budget exceeded");
            p+=fixed+((n+3)/4)*4; require(p<=b.size(),"truncated metadata padding");
        }
    };
    parse(dirs,true,dn); parse(files,false,fn);
    require(dn.count(0) && dn.at(0).parent==0 && dn.at(0).name.empty() && dn.at(0).next==0xffffffff,"invalid RomFS root");
    struct Work { U id,parent,depth; std::string path; };
    std::vector<Work> pending{{0,0,0,""}};
    std::set<U> seenDirs,seenFiles;
    U total=0,reportBytes=0;
    while(!pending.empty()) {
        auto w=pending.back(); pending.pop_back();
        require(w.depth<=128 && w.path.size()<=8192,"RomFS path budget exceeded");
        require(dn.count(w.id) && seenDirs.insert(w.id).second,"invalid/cyclic RomFS directory link");
        const auto& d=dn.at(w.id); require(d.parent==w.parent,"RomFS directory parent mismatch");
        std::set<std::string> names;
        U f=d.file;
        while(f!=0xffffffff) {
            require(fn.count(f) && seenFiles.insert(f).second,"invalid/cyclic RomFS file link");
            const auto& file=fn.at(f); require(file.parent==w.id && !file.name.empty(),"RomFS file parent/name mismatch");
            require(names.insert(file.name).second,"duplicate RomFS name");
            require(total<=std::numeric_limits<U>::max()-file.size,"RomFS total overflow"); total+=file.size;
            reportBytes+=w.path.size()+file.name.size()+128;
            require(reportBytes<=32*1024*1024,"RomFS report budget exceeded");
            out<<"romfs_file path=\""<<w.path<<"/"<<file.name<<"\" size="<<file.size
               <<" absolute_offset="<<base+start+data+file.offset<<"\n";
            f=file.next;
        }
        std::set<U> siblings;
        U child=d.child;
        while(child!=0xffffffff) {
            require(dn.count(child) && siblings.insert(child).second,"invalid/cyclic RomFS sibling link");
            const auto& c=dn.at(child); require(!c.name.empty() && names.insert(c.name).second,"duplicate/empty RomFS directory name");
            pending.push_back({child,w.id,w.depth+1,w.path+"/"+c.name});
            require(pending.size()<=100000,"RomFS work budget exceeded"); child=c.next;
        }
    }
    require(seenDirs.size()==dn.size() && seenFiles.size()==fn.size(),"unreachable RomFS metadata");
    out<<"romfs_summary directories="<<dn.size()<<" files="<<fn.size()<<" file_bytes="<<total
       <<" ivfc_tree=not_verified hash_buckets=not_verified\n";
}
void verify_region(Reader& r,U offset,U length,const Header& h,size_t stored,const char* label,std::ostream& out) {
    if(!length) { out<<label<<"_hash=absent\n"; return; }
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
       <<"stored_hashes=reported_only signatures=not_verified\n";
    if(options.verify) {
        U logo=scale(le(h,0x19c),exp);
        verify_region(r,base+scale(le(h,0x198),exp),logo,h,0x130,"logo",out);
        if(encrypted) out<<"content_hashes=skipped_encrypted\n";
        else {
            verify_region(r,base+512,ex,h,0x160,"exheader",out);
            verify_region(r,base+scale(le(h,0x1a0),exp),scale(le(h,0x1a8),exp),h,0x1c0,"exefs",out);
            verify_region(r,base+scale(le(h,0x1b0),exp),scale(le(h,0x1b8),exp),h,0x1e0,"romfs_superblock",out);
        }
    }
    if(options.list && le(h,0x1b4)) {
        if(encrypted) out<<"romfs_listing=skipped_encrypted\n";
        else romfs(r,base+scale(le(h,0x1b0),exp),scale(le(h,0x1b4),exp),out);
    }

}
int main(int argc,char** argv) {
    Options options;
    if(argc<2) { std::cerr<<"usage: stt-inspect input [--verify] [--list-romfs]\n"; return 2; }
    for(int i=2;i<argc;++i) {
        std::string arg=argv[i];
        if(arg=="--verify") options.verify=true;
        else if(arg=="--list-romfs") options.list=true;
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
