#include "visual.h"
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
static void put16(uint8_t *p,uint16_t n){p[0]=(uint8_t)(n>>8);p[1]=(uint8_t)n;}
static void put32(uint8_t *p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(24-8*i));}
int stt_visual_capture(SttVisual *v,const uint32_t *pixels,size_t pitch,const SttPlaySample *s,
 uint64_t stream,uint32_t frame,unsigned equipment,unsigned ground,const SttTarget *target){
 if(!v||!pixels||pitch<480||!s||!target||equipment>3||ground>1)return -1;
 v->total=v->offset=0;
 char scene[1025];if(stt_play_encode(scene,sizeof scene,s)<0)return -1;
 int n=snprintf((char*)v->data,STT_VISUAL_META,
 "{\"version\":1,\"width\":240,\"height\":136,\"format\":\"rgb565le\",\"frame\":%"PRIu32",\"equipment\":%u,\"ground_mode\":%u,\"target\":{\"id\":%"PRIu32",\"pos_mm\":[%"PRId32",0,%"PRId32"],\"hp\":%"PRId32",\"reaction_ticks\":%u},\"scene\":%s}",frame,equipment,ground,target->id,target->x_mm,target->z_mm,target->hp,(unsigned)target->reaction_ticks,scene);
 if(n<0||n>=(int)STT_VISUAL_META)return -1;
 v->meta=(uint16_t)n;v->stream=stream;v->frame=frame;
 for(unsigned y=0;y<STT_VISUAL_H;y++)for(unsigned x=0;x<STT_VISUAL_W;x++){
  uint32_t pixel=pixels[(size_t)(y*2)*pitch+x*2];
  uint16_t r=(uint16_t)((pixel&255u)>>3),g=(uint16_t)(((pixel>>8)&255u)>>2),b=(uint16_t)(((pixel>>16)&255u)>>3);
  uint16_t color=(uint16_t)((r<<11)|(g<<5)|b);
  size_t at=(size_t)n+2*(y*STT_VISUAL_W+x);v->data[at]=(uint8_t)color;v->data[at+1]=(uint8_t)(color>>8);
 }
 v->total=(uint32_t)n+STT_VISUAL_PIXELS;return 0;
}
int stt_visual_next(SttVisual *v,uint8_t *out,size_t cap){
 if(!v||!out||v->offset>v->total||v->total>sizeof v->data)return -1;
 if(v->offset==v->total)return 0;
 uint32_t count=v->total-v->offset;if(count>STT_VISUAL_CHUNK)count=STT_VISUAL_CHUNK;
 if(cap<STT_VISUAL_HEADER+count)return -1;
 memcpy(out,"STV1",4);put32(out+4,(uint32_t)(v->stream>>32));put32(out+8,(uint32_t)v->stream);
 put32(out+12,v->frame);put32(out+16,v->total);put32(out+20,v->offset);put16(out+24,(uint16_t)count);put16(out+26,v->meta);
 memcpy(out+STT_VISUAL_HEADER,v->data+v->offset,count);v->offset+=count;return (int)(STT_VISUAL_HEADER+count);
}
