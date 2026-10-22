#ifndef STT_RENDER_H
#define STT_RENDER_H
#include <stdint.h>
#include "control.h"
#include "stt_combat.h"
#include "asset.h"
#include "weapon.h"
#include "equipment.h"
#define STT_WIDTH 480
#define STT_HEIGHT 272
#define STT_PITCH 512
void stt_render(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused);
void stt_render_error(uint32_t *pixels,int error);
void stt_render_with_asset(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *asset);
void stt_render_equipped(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *body,SttWeapon *weapon);
void stt_render_equipment(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *body,SttWeapon *weapon,const SttEquipment *equipment);
#endif
