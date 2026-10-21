#include "weapon.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static SttAssetStatus finish(SttWeapon *w,size_t bytes) {
    if(!bytes||bytes>STT_WEAPON_CAP||!stt_pose_open(&w->pose,w->bytes,bytes)||
       w->pose.bones!=1||w->pose.clips!=1||w->pose.frames!=1||
       !stt_pose_frame(&w->pose,0,0,&w->frame)) {
        memset(&w->pose,0,sizeof w->pose);memset(&w->frame,0,sizeof w->frame);
        w->status=STT_ASSET_INVALID;
    }else w->status=STT_ASSET_READY;
    return w->status;
}
SttAssetStatus stt_weapon_memory(SttWeapon *w,const void *data,size_t bytes) {
    if(!w)return STT_ASSET_INVALID;
    memset(w,0,sizeof *w);
    if(!data||!bytes||bytes>STT_WEAPON_CAP){w->status=STT_ASSET_INVALID;return w->status;}
    memcpy(w->bytes,data,bytes);return finish(w,bytes);
}
SttAssetStatus stt_weapon_file(SttWeapon *w,const char *path) {
    if(!w)return STT_ASSET_INVALID;
    memset(w,0,sizeof *w);
    if(!path){w->status=STT_ASSET_INVALID;return w->status;}
    FILE *file=fopen(path,"rb");if(!file)return STT_ASSET_MISSING;
    size_t bytes=fread(w->bytes,1,sizeof w->bytes,file);int error=ferror(file);
    if(fclose(file)!=0)error=1;
    if(error){w->status=STT_ASSET_INVALID;return w->status;}
    return finish(w,bytes);
}
typedef struct {float hx,hy,hz,dx,dy,s,c,x,z;} Mount;
static int mount_prepare(const SttPoseFrame *body,int32_t x,int32_t z,uint16_t yaw,Mount *m) {
    if(!body||x<-1000000||x>1000000||z<-1000000||z>1000000)return 0;
    for(unsigned j=0;j<3;j++)if(body->joints[2][j]<-1000000||body->joints[2][j]>1000000||body->joints[3][j]<-1000000||body->joints[3][j]>1000000)return 0;
    float dx=(float)body->joints[3][0]-body->joints[2][0];
    float dy=(float)body->joints[3][1]-body->joints[2][1];
    float dz=(float)body->joints[3][2]-body->joints[2][2];
    float length=sqrtf(dx*dx+dy*dy);
    if(length<100||length>2000||fabsf(dz)>1)return 0;
    m->dx=dx/length;m->dy=dy/length;
    m->hx=(float)body->joints[3][0];m->hy=(float)body->joints[3][1];m->hz=(float)body->joints[3][2];
    float angle=(float)yaw*(6.283185307179586f/65536.0f);
    m->s=sinf(angle);m->c=cosf(angle);m->x=(float)x;m->z=(float)z;return 1;
}
static int place(const Mount *m,const int32_t p[3],float out[3]) {
    if(!p||!out)return 0;
    for(unsigned j=0;j<3;j++)if(p[j]<-1000000||p[j]>1000000)return 0;
    /* Transverse=(dy,-dx,0), longitudinal=(dx,dy,0), normal=(0,0,1).
       Determinant +1, no reflection. Grip maps exactly to the hand joint. */
    float longitudinal=(float)p[1]-STT_WEAPON_GRIP_MM;
    float mx=m->hx+m->dy*p[0]+m->dx*longitudinal;
    float my=m->hy-m->dx*p[0]+m->dy*longitudinal;
    float mz=m->hz+p[2];
    out[0]=(m->x+mx*m->c+mz*m->s)*.001f;out[1]=my*.001f;out[2]=(m->z+mz*m->c-mx*m->s)*.001f;
    return 1;
}
int stt_weapon_vertex(const SttPoseFrame *body,const int32_t p[3],int32_t x,int32_t z,uint16_t yaw,float out[3]) {
    Mount mount;return mount_prepare(body,x,z,yaw,&mount)&&place(&mount,p,out);
}
int stt_weapon_emit(const SttWeapon *w,const SttPoseFrame *body,int32_t x,int32_t z,uint16_t yaw,SttPoseTriangleSink sink,void *context) {
    static const int32_t fallback[8][3]={{-40,180,-25},{40,180,-25},{40,1400,-25},{-40,1400,-25},{-40,180,25},{40,180,25},{40,1400,25},{-40,1400,25}};
    static const uint16_t faces[12][3]={{0,1,2},{0,2,3},{4,6,5},{4,7,6},{0,4,5},{0,5,1},{1,5,6},{1,6,2},{2,6,7},{2,7,3},{3,7,4},{3,4,0}};
    Mount mount;
    if(!body||!sink||!mount_prepare(body,x,z,yaw,&mount))return 0;
    int ready=w&&w->status==STT_ASSET_READY;
    unsigned count=ready?w->pose.triangle_count:12;
    if(!count||count>STT_POSE_TRIANGLES||(ready&&(!w->pose.vertices||w->pose.vertices>STT_POSE_VERTICES)))return 0;
    for(unsigned i=0;i<count;i++){
        float tri[3][3];
        for(unsigned j=0;j<3;j++){
            unsigned index=ready?w->pose.triangles[i][j]:faces[i][j];
            if(ready&&index>=w->pose.vertices)return 0;
            const int32_t *p=ready?w->frame.vertices[index]:fallback[index];
            if(!place(&mount,p,tri[j]))return 0;
        }
        if(!sink(context,(const float (*)[3])tri))return 0;
    }
    return 1;
}
