#include "pacer.h"
#include <assert.h>
#include <stdio.h>
static void cadence(unsigned fps,unsigned work){
 SttPacer p;stt_pacer_reset(&p,0,fps);uint64_t now=0;
 for(unsigned i=0;i<fps*20;i++){
  now+=work;
  /* Present at the next 60 Hz boundary, as the Vita loop does. */
  uint64_t vblank=now*60/1000000+1;
  now=(vblank*1000000+59)/60;
  now+=stt_pacer_wait(&p,now);
 }
 assert(now>=19999999&&now<=20016667);
 assert(p.deadline==20000000&&p.remainder==0);
}
int main(void){
 cadence(45,12000);cadence(45,15000);cadence(30,12000);
 SttPacer p;stt_pacer_reset(&p,0,45);
 assert(stt_pacer_wait(&p,50000)==0); /* overload never waits */
 assert(stt_pacer_wait(&p,5000000)==0&&p.deadline==5000000);
 assert(stt_pacer_wait(&p,1)==0&&p.deadline==1); /* clock reset */
 stt_pacer_reset(&p,1000000,30);
 assert(stt_pacer_wait(&p,1010000)==23333); /* target switch resets phase */
 stt_pacer_reset(&p,UINT64_MAX-10,45);
 assert(stt_pacer_wait(&p,UINT64_MAX-5)==0); /* no unsigned wrap */
 puts("absolute 30/45 FPS pacing, vblank, overload and reset checks passed");
 return 0;
}
