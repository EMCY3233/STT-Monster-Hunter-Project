#include "stt_combat.h"
#include <stdio.h>
int main(void) {
 SttCombat c; unsigned i; stt_combat_init(&c);
 puts("Original synthetic STT Combat Lab: fixed60, no commercial game data");
 for(i=0;i<110;i++) {
  int attack=i==0 || (c.hunter.state==STT_RECOVERY && c.hunter.phase_tick==12 && c.hunter.combo<3);
  stt_combat_step(&c,(SttCombatInput){0,0,0,attack});
  if(c.impact_count) printf("tick=%llu attack=%u target=%u damage=%d hp=%d\n",
   (unsigned long long)c.tick,c.impacts[0].attack_id,c.impacts[0].target_id,c.impacts[0].damage,c.target.hp);
 }
 return c.target.hp==54?0:1;
}
