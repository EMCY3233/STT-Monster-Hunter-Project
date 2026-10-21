#include "asset.h"
#include <stdio.h>
#include <string.h>
static SttAssetStatus finish(SttAsset *a, size_t bytes) {
    a->status=(bytes && bytes<=STT_ASSET_CAP && stt_pose_open(&a->pose,a->bytes,bytes))
        ?STT_ASSET_READY:STT_ASSET_INVALID;
    if (a->status!=STT_ASSET_READY) memset(&a->pose,0,sizeof a->pose);
    return a->status;
}
SttAssetStatus stt_asset_memory(SttAsset *a, const void *data, size_t bytes) {
    if (!a) return STT_ASSET_INVALID;
    memset(a,0,sizeof *a);
    if (!data || bytes==0 || bytes>STT_ASSET_CAP) { a->status=STT_ASSET_INVALID; return a->status; }
    memcpy(a->bytes,data,bytes); return finish(a,bytes);
}
SttAssetStatus stt_asset_file(SttAsset *a, const char *path) {
    if (!a) return STT_ASSET_INVALID;
    memset(a,0,sizeof *a);
    if (!path) { a->status=STT_ASSET_INVALID; return a->status; }
    FILE *file=fopen(path,"rb");
    if (!file) return STT_ASSET_MISSING;
    size_t bytes=fread(a->bytes,1,sizeof a->bytes,file);
    int error=ferror(file);
    if (fclose(file)!=0) error=1;
    if (error) { a->status=STT_ASSET_INVALID; return a->status; }
    return finish(a,bytes);
}
unsigned stt_asset_clip(const SttAsset *a, int attacking) {
    return a && a->status==STT_ASSET_READY && attacking && a->pose.clips>1 ? 1u:0u;
}
