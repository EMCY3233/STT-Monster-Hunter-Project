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
void ncch(Reader& r,U base,U available,std::ostream& out) {
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
}
int main(int argc,char** argv) {
    if(argc!=2) { std::cerr<<"usage: stt-inspect input.3ds|input.cci|input.ncch\n"; return 2; }
    try {
        Reader r(argv[1]); auto h=r.header(0); std::ostringstream report;
        if(magic(h,"NCCH")) ncch(r,0,r.size,report);
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
                ncch(r,off,len,report);
            }
            require(!parts.empty(),"NCSD has no partitions"); disjoint(parts);
        }
        report<<"file_size="<<r.size<<" file_sha256="<<r.digest(0,r.size)<<"\n";
        std::cout<<report.str(); return 0;
    } catch(const std::exception& e) { std::cerr<<"invalid/unsupported: "<<e.what()<<"\n"; return 1; }
}
