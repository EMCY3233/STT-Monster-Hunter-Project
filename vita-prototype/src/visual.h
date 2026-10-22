#ifndef STT_VISUAL_CAPTURE_H
#define STT_VISUAL_CAPTURE_H
#include <stdint.h>
#include <stddef.h>
#include "stt_play.h"
#include "stt_combat.h"
#define STT_VISUAL_W 240u
#define STT_VISUAL_H 136u
#define STT_VISUAL_META 1536u
#define STT_VISUAL_PIXELS (STT_VISUAL_W*STT_VISUAL_H*2u)
#define STT_VISUAL_CHUNK 1000u
#define STT_VISUAL_HEADER 28u
typedef struct {
 uint8_t data[STT_VISUAL_META+STT_VISUAL_PIXELS];
 uint32_t total,offset,frame;uint16_t meta;uint64_t stream;
} SttVisual;
/* Snapshot of prototype-owned 480x272 A8B8G8R8 buffer, never other applications. */
int stt_visual_capture(SttVisual *v,const uint32_t *pixels,size_t pitch,const SttPlaySample *scene,
 uint64_t stream,uint32_t frame,unsigned equipment,unsigned ground,const SttTarget *target);
/* At most 1028 bytes; advances one immutable image. 0 when complete. */
int stt_visual_next(SttVisual *v,uint8_t *out,size_t capacity);
#endif
