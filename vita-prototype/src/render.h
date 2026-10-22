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
typedef uint64_t (*SttRenderClock)(void);
typedef struct {unsigned clear_us,ground_us,ceiling_us,body_us,weapon_us,target_us,hud_us;} SttRenderProfile;
void stt_render_set_target(unsigned fps);
void stt_render_set_clock(SttRenderClock clock);
const SttRenderProfile *stt_render_profile(void);
void stt_render_set_raster(unsigned mode);
unsigned stt_render_get_raster(void);
void stt_render(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused);
void stt_render_error(uint32_t *pixels,int error);
void stt_render_with_asset(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *asset);
void stt_render_equipped(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *body,SttWeapon *weapon);
void stt_render_equipment(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *body,SttWeapon *weapon,const SttEquipment *equipment);
#define STT_CEILING_HEIGHT 8.0f
void stt_render_set_ceiling(unsigned mode);
unsigned stt_render_get_ceiling(void);
void stt_render_set_ground(unsigned mode);
unsigned stt_render_get_ground(void);
void stt_render_monitor_status(int active,unsigned sent,int result);
#endif
