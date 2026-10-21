#include "stt_combat.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
static SttCombatInput input={0,0,0,0};
static void ticks(SttCombat*c,unsigned n) { while(n--) stt_combat_step(c,input); }
int main(void) {
 SttCombat c,d; int32_t x,z; unsigned i,total=0;
 stt_combat_init(&c); assert(c.target.hp==100 && c.hunter.state==STT_IDLE);
 stt_combat_direction(0,&x,&z); assert(x==0 && z==32767);
 stt_combat_direction(16384,&x,&z); assert(x==32767 && z==0);
 stt_combat_step(&c,(SttCombatInput){INT_MAX,INT_MIN,16384,0});
 assert(c.hunter.x_mm==100 && c.hunter.z_mm==-100 && c.hunter.yaw_turn==16384);
 stt_combat_init(&c); stt_combat_step(&c,(SttCombatInput){0,0,0,1});
 assert(c.hunter.state==STT_WINDUP && c.hunter.phase_tick==0 && c.hunter.attack_id==1);
 ticks(&c,7); assert(c.hunter.state==STT_WINDUP && c.target.hp==100);
 ticks(&c,1); assert(c.hunter.state==STT_ACTIVE && c.target.hp==100);
 ticks(&c,1); assert(c.impact_count==1 && c.target.hp==90 && c.target.reaction_ticks==12);
 assert(c.impacts[0].tick==10 && c.impacts[0].attack_id==1 && c.impacts[0].target_id==1);
 ticks(&c,3); assert(c.hunter.state==STT_RECOVERY && c.target.hp==90 && !c.impact_count);
 /* Early recovery press ignored. */
 stt_combat_step(&c,(SttCombatInput){100,100,16384,1}); ticks(&c,15);
 assert(c.hunter.state==STT_IDLE && c.hunter.x_mm==0 && c.hunter.yaw_turn==0);
 stt_combat_init(&c);
 for(i=0;i<110;i++) {
  int press=i==0 || (c.hunter.state==STT_RECOVERY && c.hunter.phase_tick==12 && c.hunter.combo<3);
  stt_combat_step(&c,(SttCombatInput){0,0,0,press}); total+=c.impact_count;
 }
 /* Third attack recovery opens at tick16, no further chain. */
 assert(total==3 && c.target.hp==54 && c.hunter.attack_id==3 && c.hunter.state==STT_IDLE);
 /* Recovery buffer boundaries: phase7 rejected, phase8 and phase15 accepted. */
 for(i=7;i<=15;i+=(i==7?1:7)) {
  stt_combat_init(&c); stt_combat_step(&c,(SttCombatInput){0,0,0,1});
  ticks(&c,12+i); assert(c.hunter.state==STT_RECOVERY && c.hunter.phase_tick==i);
  stt_combat_step(&c,(SttCombatInput){0,0,0,1}); ticks(&c,15-i);
  assert(c.hunter.state==(i==7?STT_IDLE:STT_WINDUP));
  if(i!=7) assert(c.hunter.combo==2 && c.hunter.attack_id==2);
 }
 stt_combat_init(&c); c.target.hp=1;
 stt_combat_step(&c,(SttCombatInput){0,0,0,1}); ticks(&c,9);
 assert(c.target.hp==0 && c.target.reaction_ticks==12);
 ticks(&c,12); assert(c.target.reaction_ticks==0);
 c.hunter.state=(SttHunterState)-1;
 stt_combat_step(&c,input); assert(c.hunter.state==STT_IDLE);
 c.hunter.state=(SttHunterState)99; c.hunter.combo=255;
 stt_combat_step(&c,input); assert(c.hunter.state==STT_IDLE);
 /* Facing opposite target must miss. */
 stt_combat_init(&c); stt_combat_step(&c,(SttCombatInput){0,0,32768,1}); ticks(&c,28);
 assert(c.target.hp==100);
 /* Inclusive collision boundary and one millimetre outside. */
 stt_combat_init(&c); c.target.z_mm=1900;
 stt_combat_step(&c,(SttCombatInput){0,0,0,1}); ticks(&c,12); assert(c.target.hp==90);
 stt_combat_init(&c); c.target.z_mm=1901;
 stt_combat_step(&c,(SttCombatInput){0,0,0,1}); ticks(&c,12); assert(c.target.hp==100);
 /* Dead targets never emit hits; arena input cannot overflow. */
 stt_combat_init(&c); c.target.hp=0; c.target.x_mm=INT_MIN;
 stt_combat_step(&c,(SttCombatInput){0,0,0,1}); ticks(&c,12); assert(!c.impact_count);
 stt_combat_init(&c); c.hunter.x_mm=INT_MAX;
 stt_combat_step(&c,(SttCombatInput){INT_MAX,INT_MAX,0,0}); assert(c.hunter.x_mm==100000);
 /* Zero is reserved by the telemetry contract, including counter rollover. */
 stt_combat_init(&c); c.hunter.attack_id=UINT32_MAX;
 stt_combat_step(&c,(SttCombatInput){0,0,0,1}); ticks(&c,9);
 assert(c.hunter.attack_id==1 && c.impact_count==1 && c.impacts[0].attack_id==1);
 /* Repeat identical 10000-tick command stream and compare full initialized state. */
 stt_combat_init(&c); stt_combat_init(&d);
 for(i=0;i<10000;i++) {
  SttCombatInput in={(int)(i%37)-18,(int)(i%43)-21,(uint16_t)(i*79),i%29==0};
  stt_combat_step(&c,in); stt_combat_step(&d,in); assert(!memcmp(&c,&d,sizeof(c)));
 }
 puts("combat: boundary, combo, hit dedup, malformed input and 10000-tick replay passed");
 return 0;
}
