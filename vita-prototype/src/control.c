#include "control.h"
#include <math.h>
#define PI 3.14159265358979323846f
unsigned stt_game_buttons(unsigned raw) { return raw&0x0000ffffu; }
float stt_axis(unsigned char value) {
    float x=((float)value-127.5f)/127.5f;
    if (fabsf(x)<0.18f) return 0;
    return copysignf((fabsf(x)-0.18f)/0.82f,x);
}
void stt_camera_step(SttCamera *c,unsigned char rx,unsigned char ry) {
    c->yaw+=stt_axis(rx)*0.035f;
    c->pitch+=stt_axis(ry)*0.025f;
    if(c->pitch<0.12f)c->pitch=0.12f;
    if(c->pitch>1.05f)c->pitch=1.05f;
    if(c->yaw>PI)c->yaw-=2*PI;
    if(c->yaw<-PI)c->yaw+=2*PI;
}
SttMove stt_camera_move(SttCamera c,unsigned char lx,unsigned char ly,uint16_t previous) {
    float side=stt_axis(lx),forward=-stt_axis(ly),length=sqrtf(side*side+forward*forward);
    SttMove m={0,0,previous};
    if(length>1){side/=length;forward/=length;}
    float x=side*cosf(c.yaw)+forward*sinf(c.yaw);
    float z=forward*cosf(c.yaw)-side*sinf(c.yaw);
    m.x_mm=(int)lroundf(x*50); m.z_mm=(int)lroundf(z*50);
    if(m.x_mm||m.z_mm) m.yaw_turn=(uint16_t)(int)(atan2f(x,z)*65536/(2*PI));
    return m;
}
unsigned stt_frame_ticks(uint64_t elapsed,uint64_t *acc) {
    if(elapsed>100000){elapsed=100000;*acc=0;}
    *acc+=elapsed;unsigned n=(unsigned)(*acc/16667);
    if(n>4){n=4;*acc=0;}else *acc-=n*16667;
    return n;
}
