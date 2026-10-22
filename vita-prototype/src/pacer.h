#ifndef STT_PACER_H
#define STT_PACER_H
#include <stdint.h>
/* Absolute deadlines avoid adding vblank phase error to every frame. */
typedef struct {uint64_t deadline,last;unsigned fps,remainder;} SttPacer;
static inline void stt_pacer_reset(SttPacer *p,uint64_t now,unsigned fps){
 p->deadline=p->last=now;p->fps=fps==30?30:45;p->remainder=0;
}
static inline unsigned stt_pacer_wait(SttPacer *p,uint64_t now){
 unsigned step=1000000/p->fps;
 p->remainder+=1000000%p->fps;
 if(p->remainder>=p->fps){p->remainder-=p->fps;step++;}
 if(now<p->last||p->deadline>UINT64_MAX-step||
    (now>p->deadline&&now-p->deadline>200000)){
  stt_pacer_reset(p,now,p->fps);return 0;
 }
 p->last=now;p->deadline+=step;
 return p->deadline>now?(unsigned)(p->deadline-now):0;
}
#endif
