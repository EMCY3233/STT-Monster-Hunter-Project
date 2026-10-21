#ifndef STT_COMBAT_H
#define STT_COMBAT_H
#include <stdint.h>
#define STT_COMBAT_HZ 60
#define STT_COMBAT_MAX_MOVE_MM 100
/* X right, Y up (ground plane y=0), Z forward. Yaw 0=+Z, 16384=+X. */
typedef enum { STT_IDLE, STT_WINDUP, STT_ACTIVE, STT_RECOVERY } SttHunterState;
typedef struct { int32_t x_mm,z_mm; uint16_t yaw_turn; SttHunterState state;
 uint32_t attack_id; uint16_t phase_tick; uint8_t combo; } SttHunter;
typedef struct { int32_t x_mm,z_mm; int32_t hp; uint16_t reaction_ticks; uint32_t id; } SttTarget;
typedef struct { uint32_t attack_id,target_id; int32_t damage; uint64_t tick; } SttImpact;
typedef struct { int32_t move_x_mm,move_z_mm; uint16_t yaw_turn; int attack_pressed; } SttCombatInput;
typedef struct { uint64_t tick; SttHunter hunter; SttTarget target;
 SttImpact impacts[1]; uint8_t impact_count, hit_latched, buffered; } SttCombat;
void stt_combat_init(SttCombat *c);
void stt_combat_step(SttCombat *c, SttCombatInput input);
/* Deterministic, quantized 64 heading direction, scale 32767. */
void stt_combat_direction(uint16_t yaw, int32_t *x, int32_t *z);
#endif
