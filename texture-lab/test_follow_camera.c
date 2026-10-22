#include "follow_camera.h"
#include "scene.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static float norm(const float *a){return sqrtf(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);}
static float plane(void *context,const float a[3],const float b[3],float radius){
 const float *wall=context;unsigned axis=(unsigned)wall[0];float d[3];for(unsigned i=0;i<3;i++)d[i]=b[i]-a[i];float length=norm(d),limit=wall[1]-radius;
 if(a[axis]>=limit)return 0;
 if(b[axis]<=limit)return length;
 return length*(limit-a[axis])/(b[axis]-a[axis]);
}
static float invalid(void *context,const float a[3],const float b[3],float radius){(void)context;(void)a;(void)b;(void)radius;return NAN;}
static float clear(void *context,const float a[3],const float b[3],float radius){(void)context;(void)radius;float d[3];for(unsigned i=0;i<3;i++)d[i]=b[i]-a[i];return norm(d);}
static void basis(const SttFollowView *v){
 assert(fabsf(norm(v->view.right)-1)<1e-5f&&fabsf(norm(v->view.up)-1)<1e-5f&&fabsf(norm(v->view.forward)-1)<1e-5f);
 for(unsigned i=0;i<3;i++)assert(isfinite(v->view.eye[i]));
 float dot=0;for(unsigned i=0;i<3;i++)dot+=v->view.right[i]*v->view.up[i];assert(fabsf(dot)<1e-5f);
}
int main(void){
 SttFollowConfig cfg=stt_follow_defaults();SttFollowCamera c={0};SttFollowView v;SttCamera angles={0,.4f};float hunter[3]={3,5,8};
 assert(stt_follow_step(&c,&cfg,angles,hunter,1.0f/60,0,NULL,NULL,&v));assert(fabsf(v.focus[1]-6.1f)<1e-5f);assert(v.view.right[0]>.999f);assert(!v.world_protection);basis(&v);
 float outcomes[3][3];const unsigned rates[3]={30,60,120};
 for(unsigned r=0;r<3;r++){c=(SttFollowCamera){0};float p[3]={0,0,0};assert(stt_follow_step(&c,&cfg,angles,p,1.0f/rates[r],1,NULL,NULL,&v));p[0]=2;p[1]=1;
  for(unsigned n=0;n<rates[r];n++)assert(stt_follow_step(&c,&cfg,angles,p,1.0f/rates[r],0,NULL,NULL,&v));
  memcpy(outcomes[r],v.focus,sizeof v.focus);
 }
 for(unsigned r=1;r<3;r++)for(unsigned j=0;j<3;j++)assert(fabsf(outcomes[r][j]-outcomes[0][j])<2e-5f);
 c=(SttFollowCamera){0};float p[3]={0,0,0},wall[2]={2,2};angles=(SttCamera){3.14159265359f,0};
 assert(stt_follow_step(&c,&cfg,angles,p,.01f,1,NULL,NULL,&v));assert(v.view.eye[2]>5.9f);
 assert(stt_follow_step(&c,&cfg,angles,p,.01f,0,plane,wall,&v));assert(v.collision&&v.world_protection&&v.view.eye[2]<1.8f&&v.framing_compromised);float compressed=v.distance;
 assert(stt_follow_step(&c,&cfg,angles,p,.01f,0,clear,NULL,&v));assert(v.distance>compressed&&v.distance<6);basis(&v);
 float ceiling[2]={1,2.2f};c=(SttFollowCamera){0};angles=(SttCamera){0,1.05f};assert(stt_follow_step(&c,&cfg,angles,p,.1f,1,plane,ceiling,&v));assert(v.collision&&v.view.eye[1]<2.0f);
 c=(SttFollowCamera){0};angles=(SttCamera){0,0};assert(stt_follow_step(&c,&cfg,angles,p,.01f,1,NULL,NULL,&v));angles.yaw=3.14159265359f;
 assert(stt_follow_step(&c,&cfg,angles,p,.1f,0,NULL,NULL,&v));assert(hypotf(v.view.eye[0],v.view.eye[2])>=STT_CAMERA_MIN_BOOM-.001f);
 p[0]=100;p[1]=8;p[2]=9;assert(stt_follow_step(&c,&cfg,angles,p,1,1,NULL,NULL,&v));assert(v.dt_used==.1f&&fabsf(v.focus[1]-9.1f)<1e-5f);
 SttFollowCamera before=c;assert(!stt_follow_step(&c,&cfg,angles,p,.01f,0,invalid,NULL,&v));assert(!memcmp(&before,&c,sizeof c));
 p[0]=NAN;assert(!stt_follow_step(&c,&cfg,angles,p,.01f,0,NULL,NULL,&v));p[0]=0;assert(!stt_follow_step(&c,&cfg,angles,p,0,0,NULL,NULL,&v));
 cfg.radius=-1;assert(!stt_follow_step(&c,&cfg,angles,p,.01f,0,NULL,NULL,&v));cfg=stt_follow_defaults();
 /* Trace of C implementation for an original, asset-free PC visual review. */
 puts("{\"original_fixture\":true,\"frames\":[");c=(SttFollowCamera){0};angles=(SttCamera){3.14159265359f,.2f};
 for(unsigned n=0;n<240;n++){
  p[0]=n<60?n*.015f:.9f;p[1]=n<60?0:n<120?(n-60)*.015f:.9f;p[2]=0;
  if(n==180)angles.yaw=0;
  assert(stt_follow_step(&c,&cfg,angles,p,1.0f/60,0,n>=90&&n<150?plane:clear,n>=90&&n<150?wall:NULL,&v));basis(&v);
  printf("%s{\"frame\":%u,\"hunter\":[%.6f,%.6f,%.6f],\"eye\":[%.6f,%.6f,%.6f],\"focus\":[%.6f,%.6f,%.6f],\"collision\":%u,\"compromised\":%u}",n?",\n":"",n,p[0],p[1],p[2],v.view.eye[0],v.view.eye[1],v.view.eye[2],v.focus[0],v.focus[1],v.focus[2],v.collision,v.framing_compromised);
 }
 puts("\n]}");return 0;
}
