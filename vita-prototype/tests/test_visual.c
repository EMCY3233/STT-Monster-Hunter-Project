#include "visual.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv){
 assert(argc==3);
 uint32_t *pixels=calloc(512*272,sizeof *pixels);SttVisual *v=calloc(1,sizeof *v);assert(pixels&&v);
 for(unsigned y=0;y<272;y++)for(unsigned x=0;x<480;x++)pixels[y*512+x]=x<240?0xff0000ffu:0xff00ff00u;
 SttTarget target={0};target.id=1;target.hp=100;
 SttPlaySample s={0};s.session="vita-perf-1234";s.camera_distance_mm=6000;s.battery_pct=-1;s.hp=100;
 assert(stt_visual_capture(v,pixels,512,&s,0x1234,0,0,1,&target)==0);
 assert(v->data[v->meta]==0&&v->data[v->meta+1]==0xf8);
 assert(v->data[v->meta+240]==0xe0&&v->data[v->meta+241]==7);
 assert(stt_visual_next(v,(uint8_t[1]){0},1)==-1&&v->offset==0);
 FILE *file=fopen(argv[1],"wb");assert(file);unsigned packets=0;
 for(;;){uint8_t raw[STT_VISUAL_HEADER+STT_VISUAL_CHUNK];int n=stt_visual_next(v,raw,sizeof raw);assert(n>=0);if(!n)break;
  uint8_t length[2]={(uint8_t)(n>>8),(uint8_t)n};assert(fwrite(length,1,2,file)==2);assert(fwrite(raw,1,(size_t)n,file)==(size_t)n);packets++;}
 assert(packets>65&&packets<68);assert(fclose(file)==0);
 assert(stt_visual_capture(v,pixels,479,&s,0x1234,0,0,1,&target)==-1);
 free(pixels);pixels=calloc(960*544,sizeof *pixels);assert(pixels);
 for(unsigned y=0;y<544;y++)for(unsigned x=0;x<960;x++)pixels[y*960+x]=x<480?0xff0000ffu:0xff00ff00u;
 SttGpuVisualScene gpu={0};gpu.target_fps=30;gpu.filter_linear=1;gpu.tick=42;
 gpu.right_ppm[0]=gpu.up_ppm[1]=gpu.forward_ppm[2]=1000000;
 assert(stt_visual_capture_gpu(v,pixels,960,&gpu,0x1234,1,"vita-0024-f30-c0-1234")==0);
 assert(stt_visual_capture_gpu(v,pixels,512,&gpu,0x1234,1,"vita-0024-f30-c0-1234")==-1);
 file=fopen(argv[2],"wb");assert(file);
 for(;;){uint8_t raw[STT_VISUAL_HEADER+STT_VISUAL_CHUNK];int n=stt_visual_next(v,raw,sizeof raw);assert(n>=0);if(!n)break;
  uint8_t length[2]={(uint8_t)(n>>8),(uint8_t)n};assert(fwrite(length,1,2,file)==2);assert(fwrite(raw,1,(size_t)n,file)==(size_t)n);}
 assert(fclose(file)==0);
 free(pixels);free(v);puts("PASS: immutable downsample, RGB565 order, bounded chunks, C wire fixture");return 0;
}
