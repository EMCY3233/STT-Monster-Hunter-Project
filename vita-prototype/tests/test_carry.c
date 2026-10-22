#include "render.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static SttAsset body;
static SttWeapon sword;
static uint32_t pixels[STT_PITCH*STT_HEIGHT];
static float depth[STT_WIDTH*STT_HEIGHT];
static const SttCombatInput none={0,0,0,0};
static void finish(SttEquipment *e,SttCombat *c,unsigned ticks){
 for(unsigned i=0;i<ticks;i++)stt_equipment_step(e,c,(SttCombatInput){100,100,16384,1},1);
}
static void capture(const char *path,SttEquipment *e,SttCombat *c){
 SttCombat before=*c;SttEquipment previous=*e;
 stt_render_equipment(pixels,depth,c,(SttCamera){.45f,.4f},33333,0,0,&body,&sword,e);
 assert(!memcmp(&before,c,sizeof before)&&!memcmp(&previous,e,sizeof previous));
 FILE *f=fopen(path,"wb");assert(f);fprintf(f,"P6\n480 272\n255\n");
 for(unsigned y=0;y<STT_HEIGHT;y++)for(unsigned x=0;x<STT_WIDTH;x++){
  uint32_t p=pixels[y*STT_PITCH+x];unsigned char rgb[3]={(unsigned char)p,(unsigned char)(p>>8),(unsigned char)(p>>16)};
  assert(fwrite(rgb,1,3,f)==3);
 }assert(fclose(f)==0);
}
int main(int argc,char **argv){
 assert(argc==7);SttCombat c;SttEquipment e;stt_combat_init(&c);stt_equipment_init(&e);
 assert(stt_asset_file(&body,argv[1])==STT_ASSET_READY);
 assert(stt_weapon_file(&sword,argv[2])==STT_ASSET_READY);
 capture(argv[3],&e,&c);
 stt_equipment_step(&e,&c,(SttCombatInput){100,100,16384,1},0);
 assert(e.mode==STT_DRAWING&&c.hunter.attack_id==0&&c.hunter.x_mm==0&&!stt_equipment_in_hand(&e));
 finish(&e,&c,11);assert(!stt_equipment_in_hand(&e));
 finish(&e,&c,1);assert(stt_equipment_in_hand(&e));capture(argv[4],&e,&c);
 finish(&e,&c,12);assert(e.mode==STT_DRAWN&&c.hunter.attack_id==0&&c.target.hp==100);
 assert(c.hunter.x_mm==0&&c.hunter.z_mm==0&&c.hunter.yaw_turn==0);
 capture(argv[5],&e,&c);
 stt_equipment_step(&e,&c,(SttCombatInput){0,0,0,1},0);
 assert(c.hunter.state==STT_WINDUP);
 stt_equipment_step(&e,&c,none,1);assert(e.mode==STT_DRAWN);
 unsigned hits=0;for(unsigned i=0;i<30;i++){stt_equipment_step(&e,&c,none,0);hits+=c.impact_count;}
 assert(hits==1&&c.target.hp==90&&c.hunter.state==STT_IDLE);
 stt_equipment_step(&e,&c,none,1);assert(e.mode==STT_SHEATHING&&stt_equipment_in_hand(&e));
 finish(&e,&c,14);assert(stt_equipment_in_hand(&e));
 finish(&e,&c,1);assert(!stt_equipment_in_hand(&e));capture(argv[6],&e,&c);
 finish(&e,&c,15);assert(e.mode==STT_SHEATHED&&c.hunter.attack_id==1&&c.target.hp==90);
 stt_equipment_step(&e,&c,(SttCombatInput){100,0,16384,0},0);assert(c.hunter.x_mm==100);
 e.mode=(SttEquipmentMode)99;stt_equipment_step(&e,&c,none,0);assert(e.mode==STT_SHEATHED);
 puts("PASS carry states, midpoint sockets, transition locks, ignored repeated inputs, one impact, render purity; physical_execution=false");
 return 0;
}
