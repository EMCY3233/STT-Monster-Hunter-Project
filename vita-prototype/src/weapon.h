#ifndef STT_WEAPON_H
#define STT_WEAPON_H
#include "asset.h"
#define STT_WEAPON_CAP 8192u
#define STT_WEAPON_GRIP_MM 180
typedef struct {
    SttPose pose;
    SttPoseFrame frame;
    unsigned char bytes[STT_WEAPON_CAP+1u];
    SttAssetStatus status;
} SttWeapon;
SttAssetStatus stt_weapon_file(SttWeapon *weapon,const char *path);
SttAssetStatus stt_weapon_memory(SttWeapon *weapon,const void *data,size_t bytes);
/* Specific planar sample rig: elbow=joint2, hand=joint3, normal=+Z.
   Model Y at 180mm is the provisional grip. Bounds checked before float math. */
int stt_weapon_vertex(const SttPoseFrame *body,const int32_t p[3],int32_t x,int32_t z,uint16_t yaw,float world[3]);
/* Missing/invalid weapon emits original attached box geometry, not CC0 data. */
int stt_weapon_emit(const SttWeapon *weapon,const SttPoseFrame *body,int32_t x,int32_t z,uint16_t yaw,SttPoseTriangleSink sink,void *context);
#endif
