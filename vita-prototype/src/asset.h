#ifndef STT_ASSET_H
#define STT_ASSET_H
#include "stt_pose.h"
#define STT_ASSET_CAP 163840u
typedef enum { STT_ASSET_MISSING=0, STT_ASSET_INVALID=1, STT_ASSET_READY=2 } SttAssetStatus;
typedef struct {
    SttPose pose;
    SttPoseFrame scratch;
    unsigned char bytes[STT_ASSET_CAP+1u];
    SttAssetStatus status;
} SttAsset;
/* Asset must outlive all draws. Caller owns this fixed storage; no app heap.
   Reload only between frames. Source buffer must not alias asset. */
SttAssetStatus stt_asset_memory(SttAsset *asset, const void *data, size_t bytes);
SttAssetStatus stt_asset_file(SttAsset *asset, const char *path);
unsigned stt_asset_clip(const SttAsset *asset, int attacking);
#endif
