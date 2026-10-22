#include "stt_perf.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 char out[1025];SttPerfSample s={0};s.session="synthetic-contract-test";s.frames=12;s.window_us=1000000;
 s.cpu_mhz=333;s.gpu_mhz=111;s.xbar_mhz=111;s.battery_pct=70;s.ram_free=1000000;s.cdram_free=2000000;s.phy_free=-1;s.cdlg_free=-1;
 s.render_us=70000;s.update_us=500;s.present_us=12000;s.equipment=2;s.ground_mode=1;s.target_fps=45;s.ceiling_mode=2;s.ceiling_us=2300;
 int n=stt_perf_encode(out,sizeof out,&s);assert(n>0&&n<=1024);
 assert(strstr(out,"\"phy_free\":null")&&strstr(out,"\"cpu_load_pct\":null"));puts(out);
 assert(strstr(out,"\"ceiling_us\":2300")&&strstr(out,"\"target_fps\":45"));
 assert(stt_perf_encode(out,20,&s)==-1&&out[0]==0);
 s.session="bad\"session";assert(stt_perf_encode(out,sizeof out,&s)==-1);
 s.session="good";s.frames=0;assert(stt_perf_encode(out,sizeof out,&s)==-1);
 s.frames=1;s.equipment=4;assert(stt_perf_encode(out,sizeof out,&s)==-1);
 s.equipment=2;s.ceiling_mode=3;assert(stt_perf_encode(out,sizeof out,&s)==-1);
 s.ceiling_mode=2;s.target_fps=44;assert(stt_perf_encode(out,sizeof out,&s)==-1);
 return 0;
}
