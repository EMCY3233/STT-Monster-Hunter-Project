#pragma once
bool rsa_embedded_matches(const unsigned char* modulus,const Header& h,const std::string& digest) {
    if(!std::lexicographical_compare(h.begin(),h.begin()+256,modulus,modulus+256)) return false;
#ifdef _WIN32
    BCRYPT_ALG_HANDLE alg=nullptr; BCRYPT_KEY_HANDLE pub=nullptr;
    require(BCryptOpenAlgorithmProvider(&alg,BCRYPT_RSA_ALGORITHM,nullptr,0)==0,"RSA provider init failed");
    BCRYPT_RSAKEY_BLOB info{}; info.Magic=BCRYPT_RSAPUBLIC_MAGIC; info.BitLength=2048;
    info.cbPublicExp=3; info.cbModulus=256;
    std::vector<unsigned char> blob(sizeof(info)+3+256);
    std::memcpy(blob.data(),&info,sizeof(info));
    blob[sizeof(info)]=1; blob[sizeof(info)+1]=0; blob[sizeof(info)+2]=1;
    std::copy(modulus,modulus+256,blob.begin()+sizeof(info)+3);
    auto imported=BCryptImportKeyPair(alg,nullptr,BCRYPT_RSAPUBLIC_BLOB,&pub,blob.data(),static_cast<ULONG>(blob.size()),0);
    if(imported!=0) { BCryptCloseAlgorithmProvider(alg,0); throw std::runtime_error("RSA public modulus import failed"); }
    std::array<unsigned char,32> hash{};
    for(size_t i=0;i<hash.size();++i) hash[i]=static_cast<unsigned char>(std::stoul(digest.substr(i*2,2),nullptr,16));
    BCRYPT_PKCS1_PADDING_INFO padding{BCRYPT_SHA256_ALGORITHM};
    auto status=BCryptVerifySignature(pub,&padding,hash.data(),32,const_cast<PUCHAR>(h.data()),256,BCRYPT_PAD_PKCS1);
    BCryptDestroyKey(pub); BCryptCloseAlgorithmProvider(alg,0);
    require(status==0 || status==static_cast<NTSTATUS>(0xc000a000u),"RSA verification backend failed");
    return status==0;
#else
    using Big=std::unique_ptr<BIGNUM,decltype(&BN_free)>;
    Big n(BN_bin2bn(modulus,256,nullptr),BN_free),s(BN_bin2bn(h.data(),256,nullptr),BN_free);
    Big e(BN_new(),BN_free),result(BN_new(),BN_free);
    std::unique_ptr<BN_CTX,decltype(&BN_CTX_free)> ctx(BN_CTX_new(),BN_CTX_free);
    require(n && s && e && result && ctx,"RSA allocation failed");
    require(BN_set_word(e.get(),65537)==1,"RSA exponent init failed");
    if(BN_cmp(s.get(),n.get())>=0) return false;
    require(BN_mod_exp(result.get(),s.get(),e.get(),n.get(),ctx.get())==1,"RSA public operation failed");
    std::array<unsigned char,256> decoded{};
    require(BN_bn2binpad(result.get(),decoded.data(),256)==256,"RSA encoding failed");
    std::string expected="0001"+std::string(404,'f')+"00"+"3031300d060960864801650304020105000420"+digest;
    return hex(decoded.data(),decoded.size())==expected;
#endif
}
void inspect_signature(Reader& r,U base,const Header& h,bool encrypted,U ex,std::ostream& out) {
    const char* result=nullptr;
    if((h[0x18d]&2)==0 || ex!=0x400) result="not_checked_no_embedded_key";
    else if(encrypted) result="not_checked_encrypted_exheader";
    else {
        std::array<unsigned char,256> modulus{};
        r.read(base+0x700,modulus.data(),modulus.size());
        if((modulus[0]&0x80)==0 || (modulus[255]&1)==0) result="not_checked_invalid_embedded_modulus";
        else result=rsa_embedded_matches(modulus.data(),h,r.digest(base+256,256))?
            "valid_with_embedded_key":"invalid_with_embedded_key";
    }
    out<<"ncch_header_signature="<<result<<" exponent_profile=65537 trust=not_established\n"
       <<"access_descriptor_signature=not_checked_no_trust_anchor authenticity=not_established\n";
}
struct ResourceStats {
    U files=0,arcs=0,arcEntries=0,textures=0,other=0,unsupported=0;
    U decodedEntries=0,decodedBytes=0,compressedBytes=0;
    std::map<U,U> arcVersions,texVersions,typeCodes;
    std::map<std::pair<std::string,U>,U> decodedHeaders;
};
void inspect_resource(Reader& r,U base,U size,ResourceStats& stats,bool decompress) {
    ++stats.files;
    Header h{}; size_t prefix=static_cast<size_t>(std::min<U>(size,16));
    if(prefix) r.read(base,h.data(),prefix);
    if(prefix>=4 && std::equal(h.begin(),h.begin()+4,"ARC\0")) {
        require(size>=12,"truncated ARC header");
        U version=le(h,4,2),count=le(h,6,2); ++stats.arcs; ++stats.arcVersions[version];
        if(version!=19) { ++stats.unsupported; return; }
        require(count<=32768,"ARC entry budget exceeded");
        U bytes=count*80; range(12,bytes,size);
        require(count<=2000000-stats.arcEntries,"ARC aggregate entry budget exceeded"); stats.arcEntries+=count;
        std::vector<unsigned char> table(static_cast<size_t>(bytes));
        if(bytes) r.read(base+12,table.data(),table.size());
        std::vector<Range> ranges;
        for(U i=0;i<count;++i) {
            U p=i*80,compressed=rawle(table,p+68),offset=rawle(table,p+76);
            range(offset,compressed,size);
            require(offset>=12+bytes,"ARC payload overlaps metadata");
            if(compressed) ranges.push_back({offset,compressed});
            if(decompress) {
                U expected=rawle(table,p+72)&0x0fffffff;
                require(expected<=U(8)*1024*1024*1024-stats.decodedBytes,"ARC total output budget exceeded");
                require(compressed<=U(8)*1024*1024*1024-stats.compressedBytes,"ARC total input budget exceeded");
                auto decoded=validate_zlib(r,base+offset,compressed,expected);
                auto kind=decoded_kind(decoded);
                U decodedVersion=kind=="other" || decoded.size<6 ? 0 : U(decoded.bytes[4])|(U(decoded.bytes[5])<<8);
                ++stats.decodedHeaders[{kind,decodedVersion}];
                require(stats.decodedHeaders.size()<=4096,"decoded header category budget exceeded");
                ++stats.decodedEntries; stats.decodedBytes+=decoded.size; stats.compressedBytes+=compressed;
            }
            ++stats.typeCodes[rawle(table,p+64)];
            require(stats.typeCodes.size()<=4096,"ARC distinct type code budget exceeded");
        }
        std::sort(ranges.begin(),ranges.end(),[](const Range& a,const Range& b){return a.offset<b.offset;});
        for(size_t i=1;i<ranges.size();++i)
            require(ranges[i].offset>=ranges[i-1].offset+ranges[i-1].size,"overlapping ARC payloads");
    } else if(prefix>=4 && std::equal(h.begin(),h.begin()+4,"TEX\0")) {
        require(size>=16,"truncated TEX header"); ++stats.textures;
        U version=le(h,4)&0xfff; ++stats.texVersions[version];
        if(version!=165) { ++stats.unsupported; return; }
        U packed=le(h,8),width=(packed>>6)&8191,height=(packed>>19)&8191,mips=packed&63;
        require(width>0 && height>0 && mips>0 && h[12]>0,"invalid TEX header dimensions/counts");
    } else ++stats.other;
}
void resource_report(const ResourceStats& stats,std::ostream& out,bool decompress) {
    out<<"resources files="<<stats.files<<" arc="<<stats.arcs<<" arc19_entries="<<stats.arcEntries
       <<" tex="<<stats.textures<<" other="<<stats.other<<" unsupported="<<stats.unsupported
       <<" payloads="<<(decompress?"arc19_zlib_validated_in_memory":"not_decompressed")<<" pixels=not_decoded\n";
    if(decompress) {
        out<<"arc_zlib validated_entries="<<stats.decodedEntries<<" decoded_bytes="<<stats.decodedBytes
           <<" compressed_bytes="<<stats.compressedBytes<<" retained=prefix_16_bytes_only\n";
        for(const auto& v:stats.decodedHeaders)
            out<<"decoded_header kind="<<v.first.first<<" version_field16="<<v.first.second
               <<" entries="<<v.second<<" scope=magic_and_version_only\n";
    }
    for(const auto& v:stats.arcVersions) out<<"arc_version="<<v.first<<" files="<<v.second<<"\n";
    for(const auto& v:stats.texVersions) out<<"tex_version="<<v.first<<" files="<<v.second<<" scope=header_only\n";
    for(const auto& v:stats.typeCodes) out<<"arc_type_code="<<v.first<<" entries="<<v.second<<" semantic=not_confirmed\n";
}
