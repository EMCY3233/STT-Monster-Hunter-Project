#pragma once
struct DecodedPrefix { std::array<unsigned char,16> bytes{}; U size=0; };
DecodedPrefix validate_zlib(Reader& r,U offset,U compressed,U expected) {
    require(compressed<=64*1024*1024 && expected<=64*1024*1024,"ARC stream budget exceeded");
    struct Stream {
        z_stream z{};
        Stream() { require(inflateInit(&z)==Z_OK,"zlib init failed"); }
        ~Stream() { inflateEnd(&z); }
        Stream(const Stream&)=delete; Stream& operator=(const Stream&)=delete;
    } stream;
    std::array<unsigned char,65536> input{},output{}; U loaded=0,total=0;
    DecodedPrefix result; size_t prefix=0;
    for(;;) {
        if(stream.z.avail_in==0 && loaded<compressed) {
            size_t n=static_cast<size_t>(std::min<U>(input.size(),compressed-loaded));
            r.read(offset+loaded,input.data(),n); loaded+=n;
            stream.z.next_in=input.data(); stream.z.avail_in=static_cast<uInt>(n);
        }
        stream.z.next_out=output.data(); stream.z.avail_out=static_cast<uInt>(output.size());
        auto before=stream.z.avail_in; int status=inflate(&stream.z,Z_NO_FLUSH);
        size_t produced=output.size()-stream.z.avail_out;
        require(produced<=expected-total,"ARC decompressed size exceeds declaration");
        total+=produced;
        size_t keep=std::min(result.bytes.size()-prefix,produced);
        std::copy(output.begin(),output.begin()+keep,result.bytes.begin()+prefix); prefix+=keep;
        if(status==Z_STREAM_END) {
            require(total==expected,"ARC decompressed size mismatch");
            require(loaded-stream.z.avail_in==compressed,"ARC trailing compressed bytes");
            result.size=total; return result;
        }
        require(status==Z_OK,"invalid/truncated zlib stream");
        require(produced>0 || stream.z.avail_in<before,"zlib made no progress");
    }
}
std::string decoded_kind(const DecodedPrefix& prefix) {
    const char* names[]={"MOD","TEX","MRL","LMT","ARC"};
    if(prefix.size<4) return "other";
    for(const char* name:names)
        if(std::equal(prefix.bytes.begin(),prefix.bytes.begin()+3,name) && prefix.bytes[3]==0)
            return std::string(name);
    return "other";
}
