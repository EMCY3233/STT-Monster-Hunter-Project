/* Headless PC review using the same native loader/controller/renderer as Vita. */
#include "stt_zone.h"
#include "../vita-prototype/src/render.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
static uint32_t pixels[STT_PITCH*STT_HEIGHT];static float depth[STT_WIDTH*STT_HEIGHT];
int main(int argc,char **argv){
 if(argc!=3||!stt_zone_load(argv[1])){fprintf(stderr,"valid local stream and PPM output required\n");return 1;}
 SttCombat combat;stt_combat_init(&combat);stt_zone_move(0,0);float p[3];stt_zone_position(p);combat.hunter.x_mm=(int32_t)(p[0]*1000);combat.hunter.z_mm=(int32_t)(p[2]*1000);
 stt_render(pixels,depth,&combat,(SttCamera){.7f,.2f},33333,0,0);
 FILE *f=fopen(argv[2],"wb");if(!f)return 2;fprintf(f,"P6\n%d %d\n255\n",STT_WIDTH,STT_HEIGHT);
 for(unsigned y=0;y<STT_HEIGHT;y++)for(unsigned x=0;x<STT_WIDTH;x++){uint32_t c=pixels[y*STT_PITCH+x];unsigned char rgb[3]={c&255,(c>>8)&255,(c>>16)&255};if(fwrite(rgb,1,3,f)!=3)return 3;}
 if(fclose(f))return 4;
 unsigned accepted=0,blocked=0;for(unsigned n=0;n<600;n++){stt_zone_move(.025f,.025f);if(stt_zone_contact())blocked++;else accepted++;stt_zone_position(p);if(!isfinite(p[0])||!isfinite(p[1])||!isfinite(p[2]))return 5;}
 printf("{\"native_stream_valid\":true,\"steps_accepted\":%u,\"steps_blocked\":%u,\"final_position\":[%.5f,%.5f,%.5f],\"physical_vita_execution\":false}\n",accepted,blocked,p[0],p[1],p[2]);stt_zone_close();return 0;
}
