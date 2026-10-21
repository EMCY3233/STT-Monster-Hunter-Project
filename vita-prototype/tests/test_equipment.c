#include "render.h"
#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static struct {uint32_t before;SttAsset body;uint32_t middle;SttWeapon sword;uint32_t after;} owned;
static uint32_t pixels[STT_PITCH*STT_HEIGHT+2];
static float depth[STT_WIDTH*STT_HEIGHT+2];
static unsigned triangles;
static unsigned char saved_weapon[STT_WEAPON_CAP+1];
static int count_triangle(void *context,const float p[3][3]){
 (void)context;for(unsigned i=0;i<3;i++)for(unsigned j=0;j<3;j++)assert(isfinite(p[i][j]));
 triangles++;return 1;
}
static void close3(const float a[3],const float b[3]){for(unsigned j=0;j<3;j++)assert(fabsf(a[j]-b[j])<.00001f);}
static uint64_t render(SttCombat *combat){
 SttCombat before=*combat;SttCamera cam={.45f,.4f};
 pixels[0]=0x11223344;pixels[STT_PITCH*STT_HEIGHT+1]=0x55667788;
 depth[0]=12345;depth[STT_WIDTH*STT_HEIGHT+1]=54321;
 stt_render_equipped(pixels+1,depth+1,combat,cam,33333,0,0,&owned.body,&owned.sword);
 assert(!memcmp(&before,combat,sizeof before));
 assert(pixels[0]==0x11223344&&pixels[STT_PITCH*STT_HEIGHT+1]==0x55667788);
 assert(depth[0]==12345&&depth[STT_WIDTH*STT_HEIGHT+1]==54321);
 assert(owned.before==1&&owned.middle==2&&owned.after==3);
 uint64_t hash=1469598103934665603ull;
 for(unsigned y=55;y<239;y++)for(unsigned x=0;x<STT_WIDTH;x++){hash^=pixels[1+y*STT_PITCH+x];hash*=1099511628211ull;}
 return hash;
}
static void capture(const char *path){
 FILE *f=fopen(path,"wb");assert(f);fprintf(f,"P6\n480 272\n255\n");
 for(unsigned y=0;y<STT_HEIGHT;y++)for(unsigned x=0;x<STT_WIDTH;x++){
  uint32_t p=pixels[1+y*STT_PITCH+x];unsigned char rgb[3]={(unsigned char)p,(unsigned char)(p>>8),(unsigned char)(p>>16)};
  assert(fwrite(rgb,1,3,f)==3);
 }assert(fclose(f)==0);
}
int main(int argc,char **argv){
 assert(argc==6);owned.before=1;owned.middle=2;owned.after=3;
 SttPoseFrame anchor={0};anchor.joints[2][0]=350;anchor.joints[2][1]=1500;anchor.joints[3][0]=1000;anchor.joints[3][1]=1500;
 int32_t grip[3]={0,180,0},tip[3]={0,1400,0};float out[3];
 assert(stt_weapon_vertex(&anchor,grip,0,0,0,out));close3(out,(float[3]){1,1.5f,0});
 assert(stt_weapon_vertex(&anchor,tip,4000,5000,16384,out));close3(out,(float[3]){4,1.5f,2.78f});
 assert(!stt_weapon_vertex(&anchor,tip,INT_MAX,0,0,out));
 anchor.joints[3][2]=2;assert(!stt_weapon_vertex(&anchor,tip,0,0,0,out));anchor.joints[3][2]=0;
 anchor.joints[3][0]=350;assert(!stt_weapon_vertex(&anchor,tip,0,0,0,out));anchor.joints[3][0]=1000;
 assert(stt_asset_file(&owned.body,argv[1])==STT_ASSET_READY);
 assert(owned.body.pose.bones==4&&owned.body.pose.vertices==40&&owned.body.pose.triangle_count==60);
 assert(stt_weapon_file(&owned.sword,"stt-no-such-folder/missing-sword.json")==STT_ASSET_MISSING);
 triangles=0;assert(stt_weapon_emit(&owned.sword,&anchor,0,0,0,count_triangle,NULL)&&triangles==12);
 assert(stt_weapon_memory(&owned.sword,"{}",2)==STT_ASSET_INVALID&&!owned.sword.pose.json);
 assert(stt_weapon_memory(&owned.sword,owned.body.bytes,STT_WEAPON_CAP+1)==STT_ASSET_INVALID);
 assert(stt_weapon_file(&owned.sword,argv[1])==STT_ASSET_INVALID);
 assert(stt_weapon_file(&owned.sword,argv[2])==STT_ASSET_READY);
 assert(owned.sword.pose.bytes==7474&&owned.sword.pose.vertices==199&&owned.sword.pose.triangle_count==394);
 memcpy(saved_weapon,owned.sword.bytes,owned.sword.pose.bytes);
 char *version=strstr((char*)saved_weapon,"\"version\":1");assert(version);version[10]='2';
 assert(stt_weapon_memory(&owned.sword,saved_weapon,7474)==STT_ASSET_INVALID);
 assert(stt_weapon_file(&owned.sword,argv[2])==STT_ASSET_READY);
 owned.sword.pose.triangles[0][0]=UINT16_MAX;
 assert(!stt_weapon_emit(&owned.sword,&anchor,0,0,0,count_triangle,NULL));
 assert(stt_weapon_file(&owned.sword,argv[2])==STT_ASSET_READY);
 triangles=0;assert(stt_weapon_emit(&owned.sword,&anchor,0,0,0,count_triangle,NULL)&&triangles==394);
 unsigned anchors=0;
 for(unsigned clip=0;clip<owned.body.pose.clips;clip++)for(unsigned t=0;t<owned.body.pose.clip_frames[clip];t++){
  assert(stt_pose_frame(&owned.body.pose,clip,t,&owned.body.scratch));
  for(unsigned yaw=0;yaw<2;yaw++){
   float expected[3];assert(stt_pose_transform(owned.body.scratch.joints[3],4000,5000,(uint16_t)(yaw*16384),expected));
   assert(stt_weapon_vertex(&owned.body.scratch,grip,4000,5000,(uint16_t)(yaw*16384),out));close3(out,expected);anchors++;
  }
 }
 SttCombat combat;stt_combat_init(&combat);
 uint64_t idle=render(&combat);capture(argv[3]);
 combat.hunter.state=STT_ACTIVE;combat.tick=18;
 uint64_t swing=render(&combat);capture(argv[4]);assert(swing!=idle);
 assert(stt_weapon_memory(&owned.sword,"corrupt",7)==STT_ASSET_INVALID);
 uint64_t fallback=render(&combat);capture(argv[5]);assert(fallback!=swing);
 assert(stt_weapon_file(&owned.sword,argv[2])==STT_ASSET_READY);
 for(unsigned i=0;i<16;i++){
  combat.hunter.yaw_turn=(uint16_t)(i*4096);SttCamera cam={(float)i*.3926990817f-3.1415926536f,i&1?.12f:1.05f};
  stt_render_equipped(pixels+1,depth+1,&combat,cam,33333,0,0,&owned.body,&owned.sword);
  assert(pixels[0]==0x11223344&&pixels[STT_PITCH*STT_HEIGHT+1]==0x55667788);
  assert(depth[0]==12345&&depth[STT_WIDTH*STT_HEIGHT+1]==54321);
  assert(owned.before==1&&owned.middle==2&&owned.after==3);
 }
 stt_combat_init(&combat);for(unsigned i=0;i<10;i++)stt_combat_step(&combat,(SttCombatInput){0,50,0,0});
 stt_combat_step(&combat,(SttCombatInput){0,0,0,1});unsigned hits=0;
 for(unsigned i=0;i<15;i++){stt_combat_step(&combat,(SttCombatInput){0,0,0,0});hits+=combat.impact_count;render(&combat);}
 assert(hits==1&&combat.target.hp==90);
 printf("{\"socket_anchor_checks\":%u,\"body_sizeof_pc\":%zu,\"weapon_sizeof_pc\":%zu,\"weapon_json_bytes\":%zu,\"triangles\":394,\"combat_hits\":%u,\"target_hp\":%d,\"physical_execution\":false}\n",anchors,sizeof owned.body,sizeof owned.sword,owned.sword.pose.bytes,hits,(int)combat.target.hp);
 return 0;
}
