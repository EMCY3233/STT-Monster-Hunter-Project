#ifndef STT_RENDER_H
#define STT_RENDER_H
#include <stdint.h>
#include "control.h"
#include "stt_combat.h"
#include "asset.h"
#define STT_WIDTH 480
#define STT_HEIGHT 272
#define STT_PITCH 512
void stt_render(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused);
void stt_render_error(uint32_t *pixels,int error);
void stt_render_with_asset(uint32_t *pixels,float *depth,const SttCombat *combat,SttCamera camera,unsigned frame_us,unsigned dropped,int paused,SttAsset *asset);
#endif
