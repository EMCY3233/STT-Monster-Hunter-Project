#include "scene.h"
#include <assert.h>
#include <stdio.h>
#include <math.h>
static void transform(const float m[16],const float p[3],float q[4]){for(unsigned j=0;j<4;j++)q[j]=m[j]*p[0]+m[4+j]*p[1]+m[8+j]*p[2]+m[12+j];}
int main(int argc,char **argv){
 assert(argc>=2);SttTexScene s={0};assert(stt_tex_load(&s,argv[1]));unsigned map=0,hunter=0;
 for(unsigned i=0;i<s.nm;i++){if(s.meshes[i].hunter)hunter+=s.meshes[i].ni/3;else map+=s.meshes[i].ni/3;}
 printf("VALID textures=%u meshes=%u map_triangles=%u hunter_triangles=%u\n",s.nt,s.nm,map,hunter);
 for(int i=2;i<argc;i++){assert(!stt_tex_load(&s,argv[i]));assert(s.nt>0);}
 SttCameraView v={{0,0,0},{1,0,0},{0,0,1},{0,1,0}};float m[16],origin[3]={0,0,0},q[4],near[3]={0,0,.15f},far[3]={0,0,80};
 stt_tex_matrix(m,&v,origin,0,0);transform(m,near,q);assert(fabsf(q[2]/q[3]+1)<.0001f);transform(m,far,q);assert(fabsf(q[2]/q[3]-1)<.0001f);
 float pos[3]={2,3,4},p[3]={1,0,0};stt_tex_matrix(m,&v,pos,1.57079632679f,1);transform(m,p,q);assert(fabsf(q[3]-3)<.0001f);assert(fabsf(q[0]/(500.0f/480)-2)<.0001f);assert(fabsf(q[1]/(500.0f/272)-3)<.0001f);
 stt_tex_close(&s);stt_tex_close(&s);puts("PASS bounded texture scene and projection");return 0;
}
