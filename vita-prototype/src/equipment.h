#ifndef STT_EQUIPMENT_H
#define STT_EQUIPMENT_H
#include "stt_combat.h"
/* STT-authored study timings at 60 Hz, not measured Frontier timings. */
#define STT_DRAW_TICKS 24u
#define STT_SHEATHE_TICKS 30u
typedef enum { STT_SHEATHED, STT_DRAWING, STT_DRAWN, STT_SHEATHING } SttEquipmentMode;
typedef struct { SttEquipmentMode mode; unsigned tick; } SttEquipment;
static inline void stt_equipment_init(SttEquipment *e) {
 e->mode=STT_SHEATHED;e->tick=0;
}
static inline int stt_equipment_in_hand(const SttEquipment *e) {
 return e->mode==STT_DRAWN || (e->mode==STT_DRAWING && e->tick>=12u) ||
        (e->mode==STT_SHEATHING && e->tick<15u);
}
/* Toggle is ignored during attacks/transitions. Attack from sheathed draws only.
   All movement/heading is locked during transitions; camera remains independent. */
static inline void stt_equipment_step(SttEquipment *e,SttCombat *c,SttCombatInput in,int toggle) {
 if((unsigned)e->mode>STT_SHEATHING)stt_equipment_init(e);
 if(e->mode==STT_DRAWING || e->mode==STT_SHEATHING) {
  unsigned limit=e->mode==STT_DRAWING?STT_DRAW_TICKS:STT_SHEATHE_TICKS;
  if(++e->tick>=limit){e->mode=e->mode==STT_DRAWING?STT_DRAWN:STT_SHEATHED;e->tick=0;}
  stt_combat_step(c,(SttCombatInput){0,0,c->hunter.yaw_turn,0});return;
 }
 if(c->hunter.state==STT_IDLE && (toggle || (in.attack_pressed && e->mode==STT_SHEATHED))) {
  e->mode=e->mode==STT_SHEATHED?STT_DRAWING:STT_SHEATHING;e->tick=0;
  stt_combat_step(c,(SttCombatInput){0,0,c->hunter.yaw_turn,0});return;
 }
 if(e->mode!=STT_DRAWN)in.attack_pressed=0;
 stt_combat_step(c,in);
}
#endif
