#include "control.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 assert(stt_axis(127)==0&&stt_axis(128)==0);assert(stt_axis(0)==-1&&stt_axis(255)==1);
 SttCamera c={0,.4f};SttMove m=stt_camera_move(c,128,0,5);assert(m.x_mm==0&&m.z_mm==50&&m.yaw_turn==0);
 c.yaw=1.5707963268f;m=stt_camera_move(c,128,0,5);assert(m.x_mm==50&&m.z_mm==0&&m.yaw_turn==16384);
 m=stt_camera_move(c,255,0,5);assert(m.x_mm*m.x_mm+m.z_mm*m.z_mm<=2600);
 m=stt_camera_move(c,128,128,1234);assert(!m.x_mm&&!m.z_mm&&m.yaw_turn==1234);
 for(int i=0;i<1000;i++){stt_camera_step(&c,255,255);}assert(c.pitch<=1.05f&&fabsf(c.yaw)<=3.141593f);
 for(int i=0;i<1000;i++){stt_camera_step(&c,0,0);}assert(c.pitch>=.12f);
 uint64_t acc=0;assert(stt_frame_ticks(16667,&acc)==1);assert(stt_frame_ticks(100000,&acc)==4);
 assert(stt_frame_ticks(300000000,&acc)==0&&acc==0);puts("control/camera/fixed-step tests passed");return 0;
}
