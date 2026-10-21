#include "stt_combat.h"
#include <string.h>
#include <limits.h>
static const int16_t sine[64] = {
0,3212,6393,9512,12539,15446,18204,20787,23170,25329,27245,28898,30273,31356,32137,32609,32767,32609,32137,31356,30273,28898,27245,25329,23170,20787,18204,15446,12539,9512,6393,3212,0,-3212,-6393,-9512,-12539,-15446,-18204,-20787,-23170,-25329,-27245,-28898,-30273,-31356,-32137,-32609,-32767,-32609,-32137,-31356,-30273,-28898,-27245,-25329,-23170,-20787,-18204,-15446,-12539,-9512,-6393,-3212};
void stt_combat_direction(uint16_t yaw,int32_t *x,int32_t *z) {
 unsigned i=yaw >> 10; *x=sine[i]; *z=sine[(i+16)&63];
}
static int32_t clamp(int32_t a,int32_t lo,int32_t hi) { return a<lo?lo:(a>hi?hi:a); }
static const uint16_t windup[3]={8,10,14}, active[3]={4,4,6}, recovery[3]={16,18,24};
static const int32_t damage[3]={10,14,22};
static void begin(SttCombat *c,unsigned combo) {
 c->hunter.state=STT_WINDUP; c->hunter.phase_tick=0; c->hunter.combo=(uint8_t)combo;
 c->hunter.attack_id++; if(!c->hunter.attack_id)c->hunter.attack_id=1;
 c->hit_latched=0; c->buffered=0;
}
void stt_combat_init(SttCombat *c) {
 if(!c) return;
 memset(c,0,sizeof(*c)); c->target.z_mm=1800; c->target.hp=100; c->target.id=1;
}
static void hit(SttCombat *c) {
 int32_t x,z; int64_t dx,dz;
 if(c->hit_latched || c->target.hp<=0) return;
 stt_combat_direction(c->hunter.yaw_turn,&x,&z);
 dx=(int64_t)c->target.x_mm-c->hunter.x_mm-(int64_t)x*900/32767;
 dz=(int64_t)c->target.z_mm-c->hunter.z_mm-(int64_t)z*900/32767;
 /* Broad bound avoids overflow for malformed external state coordinates. */
 if(dx < -1000 || dx > 1000 || dz < -1000 || dz > 1000) return;
 if(dx*dx+dz*dz>1000000) return;
 c->hit_latched=1; c->target.hp-=damage[c->hunter.combo-1];
 if(c->target.hp<0) c->target.hp=0;
 c->target.reaction_ticks=12; c->impact_count=1;
 c->impacts[0]=(SttImpact){c->hunter.attack_id,c->target.id,damage[c->hunter.combo-1],c->tick};
}
void stt_combat_step(SttCombat *c,SttCombatInput in) {
 unsigned k; SttHunter *h;
 if(!c) return;
 h=&c->hunter; c->tick++; c->impact_count=0;
 if(c->target.reaction_ticks) c->target.reaction_ticks--;
 /* Invalid state safely returns idle; opaque internal fields must not be imported. */
 if((unsigned)h->state>(unsigned)STT_RECOVERY || (h->state!=STT_IDLE && (h->combo<1 || h->combo>3))) {
  h->state=STT_IDLE; h->phase_tick=0; c->buffered=0;
 }
 if(h->state==STT_IDLE) {
  int32_t mx=clamp(in.move_x_mm,-100,100),mz=clamp(in.move_z_mm,-100,100);
  /* Bound arena coordinates; no signed overflow even on malformed input. */
  h->x_mm=(int32_t)clamp(h->x_mm,-100000,100000)+mx;
  h->z_mm=(int32_t)clamp(h->z_mm,-100000,100000)+mz;
  h->x_mm=clamp(h->x_mm,-100000,100000); h->z_mm=clamp(h->z_mm,-100000,100000);
  h->yaw_turn=in.yaw_turn;
  if(in.attack_pressed) begin(c,1);
  return;
 }
 k=h->combo-1;
 /* Last 8 recovery ticks accept one buffered press. Other presses ignored. */
 if(h->state==STT_RECOVERY && h->phase_tick>=recovery[k]-8 && in.attack_pressed && h->combo<3)
  c->buffered=1;
 if(h->state==STT_ACTIVE) hit(c);
 h->phase_tick++;
 if(h->state==STT_WINDUP && h->phase_tick>=windup[k]) {h->state=STT_ACTIVE;h->phase_tick=0;}
 else if(h->state==STT_ACTIVE && h->phase_tick>=active[k]) {h->state=STT_RECOVERY;h->phase_tick=0;}
 else if(h->state==STT_RECOVERY && h->phase_tick>=recovery[k]) {
  if(c->buffered && h->combo<3) begin(c,h->combo+1);
  else {h->state=STT_IDLE;h->phase_tick=0;h->combo=0;c->buffered=0;}
 }
}
