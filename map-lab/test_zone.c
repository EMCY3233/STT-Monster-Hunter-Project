#include "stt_zone.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static int triangle(void *ctx,const float p[3][3],uint32_t color){(void)ctx;assert(color);for(unsigned j=0;j<3;j++)for(unsigned k=0;k<3;k++)assert(isfinite(p[j][k]));return 1;}
int main(int argc,char **argv){
 assert(argc==6);
 for(unsigned i=2;i<6;i++){assert(!stt_zone_load(argv[i]));assert(!stt_zone_active());}
 assert(stt_zone_load(argv[1]));assert(stt_zone_active());
 assert(stt_zone_emit(0,triangle,NULL)==2);assert(stt_zone_emit(1,triangle,NULL)==1);
 float p[3];for(unsigned i=0;i<20;i++)stt_zone_move(.05f,0);stt_zone_position(p);assert(fabsf(p[0]-1)<.0001f&&p[1]==0&&stt_zone_contact()==0);
 stt_zone_move(NAN,0);stt_zone_position(p);assert(fabsf(p[0]-1)<.0001f);
 for(unsigned i=0;i<100;i++)stt_zone_move(.05f,0);
 stt_zone_position(p);assert(p[0]<3.8f&&p[0]>3.6f&&stt_zone_contact()==1);
 stt_zone_reset();stt_zone_position(p);assert(p[0]==0&&p[1]==0&&p[2]==0);
 stt_zone_close();stt_zone_close();assert(!stt_zone_active());
 puts("PASS bounded loader, malformed streams, geometry callback, ground contact, edge and reset");return 0;
}
