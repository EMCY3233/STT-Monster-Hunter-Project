#include "asset.h"
#include "render.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static struct { uint32_t before; SttAsset asset; uint32_t after; } owned;
static uint32_t pixels[STT_PITCH*STT_HEIGHT+2];
static float depth[STT_WIDTH*STT_HEIGHT+2];
static unsigned char copy[STT_ASSET_CAP+1];
static const char anchor[]="{\"format\":\"STT Pose\",\"version\":1,\"hz\":60,\"basis\":\"RH_Xright_Yup_Zforward_mm\",\"parents\":[-1,0],\"triangles\":[[0,1,2]],\"clips\":[{\"name\":\"Anchor\",\"frames\":[{\"joints\":[[1000,2000,3000],[1000,2250,3000]],\"vertices\":[[1000,2250,3000],[1000,3250,3000],[0,2250,3000]]}]}]}";
static unsigned emitted;
static int anchor_sink(void *context,const float p[3][3]) {
    (void)context;
    const float expected[3][3]={{7,2.25f,4},{7,3.25f,4},{7,2.25f,5}};
    for(unsigned i=0;i<3;i++)for(unsigned j=0;j<3;j++)assert(fabsf(p[i][j]-expected[i][j])<.00001f);
    emitted++;return 1;
}
static uint64_t render(SttCombat *combat,SttCamera camera) {
    pixels[0]=0x12345678;pixels[STT_PITCH*STT_HEIGHT+1]=0x87654321;
    depth[0]=12345;depth[STT_WIDTH*STT_HEIGHT+1]=54321;
    stt_render_with_asset(pixels+1,depth+1,combat,camera,33333,0,0,&owned.asset);
    assert(pixels[0]==0x12345678&&pixels[STT_PITCH*STT_HEIGHT+1]==0x87654321);
    assert(depth[0]==12345&&depth[STT_WIDTH*STT_HEIGHT+1]==54321);
    assert(owned.before==0x11223344&&owned.after==0x55667788);
    uint64_t hash=1469598103934665603ull;
    /* Exclude HUD/status text: compare actual scene pixels only. */
    for(unsigned y=50;y<239;y++)for(unsigned x=0;x<STT_WIDTH;x++) {
        hash^=pixels[1+y*STT_PITCH+x];hash*=1099511628211ull;
    }
    return hash;
}
static void write_frame(const char *path) {
    FILE *out=fopen(path,"wb");assert(out);
    fprintf(out,"P6\n%d %d\n255\n",STT_WIDTH,STT_HEIGHT);
    for(unsigned y=0;y<STT_HEIGHT;y++)for(unsigned x=0;x<STT_WIDTH;x++) {
        uint32_t p=pixels[1+y*STT_PITCH+x];unsigned char rgb[3]={(unsigned char)p,(unsigned char)(p>>8),(unsigned char)(p>>16)};
        assert(fwrite(rgb,1,3,out)==3);
    }
    assert(fclose(out)==0);
}
int main(int argc,char **argv) {
    assert(argc==4);
    owned.before=0x11223344;owned.after=0x55667788;
    SttAsset *a=&owned.asset;
    assert(stt_asset_memory(a,anchor,sizeof anchor-1)==STT_ASSET_READY);
    assert(stt_pose_emit(&a->pose,0,UINT64_MAX,4000,5000,16384,&a->scratch,anchor_sink,NULL));
    assert(emitted==1);
    assert(stt_asset_memory(a,"{}",2)==STT_ASSET_INVALID&&!a->pose.json);
    assert(stt_asset_memory(a,copy,sizeof copy)==STT_ASSET_INVALID);
    assert(stt_asset_memory(a,NULL,1)==STT_ASSET_INVALID);
    assert(stt_asset_file(a,"stt-no-such-folder/no-such-sample.json")==STT_ASSET_MISSING);
    SttCombat combat;stt_combat_init(&combat);SttCamera cam={.45f,.4f};
    uint64_t missing=render(&combat,cam);
    assert(stt_asset_memory(a,"bad",3)==STT_ASSET_INVALID);
    assert(render(&combat,cam)==missing);
    assert(stt_asset_file(a,argv[1])==STT_ASSET_READY);
    assert(a->pose.bytes==149293&&a->pose.bones==4&&a->pose.vertices==48&&a->pose.triangle_count==72);
    assert(a->pose.clips==2&&a->pose.clip_frames[0]==120&&a->pose.clip_frames[1]==72);
    memcpy(copy,a->bytes,a->pose.bytes);
    assert(stt_asset_clip(a,0)==0&&stt_asset_clip(a,1)==1);
    assert(stt_pose_frame(&a->pose,0,0,&a->scratch));
    SttPoseFrame first=a->scratch;
    assert(stt_pose_frame(&a->pose,0,120,&a->scratch)&&!memcmp(&first,&a->scratch,sizeof first));
    uint64_t sample=render(&combat,cam);assert(sample!=missing);
    write_frame(argv[2]); /* Sample reference pose: clip0/tick0, fixed camera. */
    combat.tick=60;uint64_t later=render(&combat,cam);assert(later!=sample);
    assert(!memcmp(copy,a->bytes,a->pose.bytes));
    combat.hunter.state=STT_ACTIVE;combat.tick=18;
    assert(stt_pose_frame(&a->pose,1,18,&a->scratch));
    first=a->scratch;
    assert(stt_pose_frame(&a->pose,1,90,&a->scratch)&&!memcmp(&first,&a->scratch,sizeof first));
    for(unsigned i=0;i<16;i++) {
        cam.yaw=(float)i*.3926990817f-3.1415926536f;cam.pitch=i&1?.12f:1.05f;
        combat.hunter.yaw_turn=(uint16_t)(i*4096u);render(&combat,cam);
    }
    cam=(SttCamera){.45f,.4f};combat.hunter.yaw_turn=0;render(&combat,cam);
    write_frame(argv[3]); /* Same camera: clip1/tick18 after camera stress tests. */
    printf("{\"sizeof_asset_pc\":%zu,\"input_bytes\":%zu,\"pose_index_pc\":%zu,\"pose_scratch_pc\":%zu,\"camera_cases\":16,\"scope\":\"PC raster only, not Vita hardware\"}\n",sizeof *a,a->pose.bytes,sizeof a->pose,sizeof a->scratch);
    return 0;
}
