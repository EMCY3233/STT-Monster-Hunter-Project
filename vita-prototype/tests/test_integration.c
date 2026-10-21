#include "control.h"
#include "render.h"
#include "snapshot.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char**argv){
 SttCombat c;stt_combat_init(&c);SttCamera cam={0,.4f};
 SttMove m=stt_camera_move(cam,128,0,0);
 for(int i=0;i<10;i++)stt_combat_step(&c,(SttCombatInput){m.x_mm,m.z_mm,m.yaw_turn,0});
 assert(c.hunter.z_mm==500);stt_combat_step(&c,(SttCombatInput){0,0,0,1});
 int hits=0;char packet[STT_PLAY_MAX_BYTES];SttPlaySample s;
 for(int i=0;i<15;i++){
  stt_combat_step(&c,(SttCombatInput){0,0,0,0});hits+=c.impact_count;
  stt_vita_snapshot(&s,&c,cam,"pc-adapter-test",i,1000,33333,100,0);s.vita=0;
  int n=stt_play_encode(packet,sizeof packet,&s);assert(n>0&&n<STT_PLAY_MAX_BYTES);
  if(c.impact_count)puts(packet);
 }
 assert(hits==1&&c.target.hp==90);
 size_t count=STT_PITCH*STT_HEIGHT;uint32_t *pixels=malloc((count+2)*sizeof *pixels);float *depth=malloc(STT_WIDTH*STT_HEIGHT*sizeof *depth);assert(pixels&&depth);
 pixels[0]=0x12345678;pixels[count+1]=0x87654321;
 for(int k=0;k<16;k++){cam.yaw=k*.3926990817f-3.1415926536f;cam.pitch=k&1?.12f:1.05f;
  stt_render(pixels+1,depth,&c,cam,33333,0,0);assert(pixels[0]==0x12345678&&pixels[count+1]==0x87654321);}
 cam=(SttCamera){.45f,.4f};stt_render(pixels+1,depth,&c,cam,33333,0,0);
 if(argc>1){FILE*f=fopen(argv[1],"wb");assert(f);fprintf(f,"P6\n%d %d\n255\n",STT_WIDTH,STT_HEIGHT);
 for(int y=0;y<STT_HEIGHT;y++){for(int x=0;x<STT_WIDTH;x++){uint32_t p=pixels[1+y*STT_PITCH+x];unsigned char rgb[3]={p&255,(p>>8)&255,(p>>16)&255};assert(fwrite(rgb,1,3,f)==3);}}assert(fclose(f)==0);}
 free(pixels);free(depth);return 0;
}
