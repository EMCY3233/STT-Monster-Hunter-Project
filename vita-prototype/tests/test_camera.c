#include "render.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static SttAsset body;
static SttWeapon sword;
static uint32_t pixels[STT_PITCH*STT_HEIGHT];
static float depth[STT_WIDTH*STT_HEIGHT];
static SttCameraView views[40];
static unsigned long checked;
static float min_depth=1000,max_radius;
static void point(const float p[3]){
 float x=p[0]-4,z=p[2]-5,r=sqrtf(x*x+z*z);
 assert(r<STT_CAMERA_MIN_BOOM-.25f);if(r>max_radius)max_radius=r;
 for(unsigned i=0;i<40;i++){
  SttCameraView *v=&views[i];float d=0;
  for(unsigned j=0;j<3;j++)d+=(p[j]-v->eye[j])*v->forward[j];
  assert(d>.15f);if(d<min_depth)min_depth=d;checked++;
 }
}
static int triangle(void *unused,const float p[3][3]){
 (void)unused;for(unsigned i=0;i<3;i++)point(p[i]);return 1;
}
static void capture(const char *name,SttCamera camera){
 SttCombat c;stt_combat_init(&c);c.hunter.state=STT_ACTIVE;c.tick=18;
 SttEquipment e;stt_equipment_init(&e);e.mode=STT_DRAWN;
 stt_render_equipment(pixels,depth,&c,camera,33333,0,0,&body,&sword,&e);
 FILE *f=fopen(name,"wb");assert(f);fprintf(f,"P6\n480 272\n255\n");
 for(unsigned y=0;y<STT_HEIGHT;y++)for(unsigned x=0;x<STT_WIDTH;x++){
  uint32_t p=pixels[y*STT_PITCH+x];unsigned char rgb[3]={(unsigned char)p,(unsigned char)(p>>8),(unsigned char)(p>>16)};
  assert(fwrite(rgb,1,3,f)==3);
 }assert(fclose(f)==0);
}
int main(int argc,char **argv){
 assert(argc==6);assert(stt_asset_file(&body,argv[1])==STT_ASSET_READY);
 assert(stt_weapon_file(&sword,argv[2])==STT_ASSET_READY);
 unsigned at=0;const float pitches[5]={STT_CAMERA_MIN_PITCH,-.2f,0,.4f,STT_CAMERA_MAX_PITCH};
 for(unsigned yaw=0;yaw<8;yaw++)for(unsigned pitch=0;pitch<5;pitch++)
  assert(stt_camera_view((SttCamera){yaw*.7853981634f,pitches[pitch]},4000,5000,&views[at++]));
 unsigned poses=0;
 for(unsigned clip=0;clip<body.pose.clips;clip++)for(unsigned t=0;t<body.pose.clip_frames[clip];t++){
  assert(stt_pose_frame(&body.pose,clip,t,&body.scratch));
  for(unsigned i=0;i<body.pose.vertices;i++){
   float p[3];assert(stt_pose_transform(body.scratch.vertices[i],4000,5000,0,p));point(p);
  }
  assert(stt_weapon_emit(&sword,&body.scratch,4000,5000,0,triangle,NULL));poses++;
 }
 SttPoseFrame carry={0};carry.joints[2][0]=750;carry.joints[2][1]=2100;carry.joints[2][2]=-280;
 carry.joints[3][0]=300;carry.joints[3][1]=1500;carry.joints[3][2]=-280;
 assert(stt_weapon_emit(&sword,&carry,4000,5000,0,triangle,NULL));
 assert(stt_weapon_emit(NULL,&carry,4000,5000,0,triangle,NULL));
 capture(argv[3],(SttCamera){.45f,STT_CAMERA_MIN_PITCH});
 capture(argv[4],(SttCamera){.45f,0});capture(argv[5],(SttCamera){.45f,.8f});
 printf("{\"poses\":%u,\"camera_views\":40,\"point_depth_checks\":%lu,\"max_mesh_radius_m\":%.6f,\"min_forward_depth_m\":%.6f,\"physical_execution\":false}\n",poses,checked,max_radius,min_depth);
 return 0;
}
