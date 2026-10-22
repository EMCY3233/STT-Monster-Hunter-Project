/* Original STT adaptation of local camera_follow.py; no game code or assets. */
#include "follow_camera.h"
#include <math.h>
#include <string.h>
static float dot(const float *a,const float *b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
static float distance(const float *a,const float *b){float d[3];for(unsigned i=0;i<3;i++)d[i]=a[i]-b[i];return sqrtf(dot(d,d));}
static int finite3(const float *v){return isfinite(v[0])&&isfinite(v[1])&&isfinite(v[2]);}
static int constrain(const SttFollowConfig *c,SttCameraSweep sweep,void *context,const float *start,float *end,unsigned *hit){
 float length=distance(start,end);if(!sweep||length<1e-7f)return 1;
 float allowed=sweep(context,start,end,c->radius);if(!isfinite(allowed)||allowed<0||allowed>length+1e-5f)return 0;
 if(allowed<length){*hit=1;float t=fmaxf(0,allowed-c->skin)/length;for(unsigned i=0;i<3;i++)end[i]=start[i]+(end[i]-start[i])*t;}
 return 1;
}
SttFollowConfig stt_follow_defaults(void){return (SttFollowConfig){6,1.1f,10,4,.2f,.03f,.35f};}
int stt_follow_step(SttFollowCamera *state,const SttFollowConfig *c,SttCamera angles,const float hunter[3],float dt,int snap,SttCameraSweep sweep,void *context,SttFollowView *out){
 if(!state||!c||!hunter||!out||!finite3(hunter)||!isfinite(dt)||dt<=0||!isfinite(angles.yaw)||!isfinite(angles.pitch))return 0;
 if(!isfinite(c->distance)||!isfinite(c->focus_height)||!isfinite(c->follow_rate)||!isfinite(c->recovery_rate)||!isfinite(c->radius)||!isfinite(c->skin)||!isfinite(c->min_height)||c->distance<=0||c->follow_rate<=0||c->recovery_rate<=0||c->radius<=0||c->skin<0||c->min_height<0)return 0;
 if(state->ready&&(!finite3(state->eye)||!finite3(state->focus)))return 0;
 SttFollowView v;memset(&v,0,sizeof v);dt=fminf(dt,.1f);v.dt_used=dt;v.world_protection=sweep!=NULL;
 float pitch=fmaxf(STT_CAMERA_MIN_PITCH,fminf(STT_CAMERA_MAX_PITCH,angles.pitch));float sy=sinf(angles.yaw),cy=cosf(angles.yaw),sp=sinf(pitch),cp=cosf(pitch);
 float direction[3]={-sy*cp,sp,-cy*cp},target[3]={hunter[0],hunter[1]+c->focus_height,hunter[2]},safe[3];
 float alpha=-expm1f(-c->follow_rate*dt);
 for(unsigned i=0;i<3;i++)v.focus[i]=!state->ready||snap?target[i]:state->focus[i]+(target[i]-state->focus[i])*alpha;
 if(!constrain(c,sweep,context,target,v.focus,&v.collision))return 0;
 for(unsigned i=0;i<3;i++)safe[i]=v.focus[i]+direction[i]*c->distance;
 /* Preserve the existing below-focus camera floor and horizontal body gap.
    This is relative to the hunter anchor, not a world-terrain collision query. */
 safe[1]=fmaxf(safe[1],hunter[1]+c->min_height);
 if(!constrain(c,sweep,context,v.focus,safe,&v.collision))return 0;
 float previous[3];memcpy(previous,state->eye,sizeof previous);
 if(state->ready&&!snap){if(!constrain(c,sweep,context,v.focus,previous,&v.collision))return 0;}
 if(!state->ready||snap||distance(previous,state->eye)>1e-6f)memcpy(v.view.eye,safe,sizeof safe);
 else{
  alpha=-expm1f(-c->recovery_rate*dt);
  for(unsigned i=0;i<3;i++)v.view.eye[i]=state->eye[i]+(safe[i]-state->eye[i])*alpha;
  if(!constrain(c,sweep,context,v.focus,v.view.eye,&v.collision))return 0;
  float length=distance(v.view.eye,v.focus),limit=distance(safe,v.focus);
  if(length>limit&&length>1e-7f)for(unsigned i=0;i<3;i++)v.view.eye[i]=v.focus[i]+(v.view.eye[i]-v.focus[i])*limit/length;
  if(!constrain(c,sweep,context,state->eye,v.view.eye,&v.collision)||!constrain(c,sweep,context,v.focus,v.view.eye,&v.collision))return 0;
 }
 /* Smooth recovery may cut the orbit inside the hunter on a large recenter.
    Without world constraints, snap to the safe boom rather than enter it. */
 float dx=v.view.eye[0]-hunter[0],dz=v.view.eye[2]-hunter[2];
 float old_dx=state->eye[0]-hunter[0],old_dz=state->eye[2]-hunter[2];
 int entering_body=state->ready&&old_dx*old_dx+old_dz*old_dz>=STT_CAMERA_MIN_BOOM*STT_CAMERA_MIN_BOOM&&dx*dx+dz*dz<STT_CAMERA_MIN_BOOM*STT_CAMERA_MIN_BOOM;
 /* A previously compressed boom must still recover gradually. Only prevent
    a new shortcut into the body, rather than snapping outward from a wall. */
 if(entering_body||v.view.eye[1]<hunter[1]+c->min_height){
  float cut[3];memcpy(cut,safe,sizeof cut);
  if(sweep&&state->ready&&!snap&&!constrain(c,sweep,context,state->eye,cut,&v.collision))return 0;
  /* A body-avoiding cut is allowed only when the world sweep permits it. */
  if(!sweep||distance(cut,safe)<1e-6f)memcpy(v.view.eye,safe,sizeof safe);
 }
 dx=v.view.eye[0]-hunter[0];dz=v.view.eye[2]-hunter[2];
 v.distance=distance(v.view.eye,v.focus);v.framing_compromised=v.distance<STT_CAMERA_MIN_BOOM||v.distance<c->radius*2||dx*dx+dz*dz<STT_CAMERA_MIN_BOOM*STT_CAMERA_MIN_BOOM;
 for(unsigned i=0;i<3;i++)v.view.forward[i]=v.distance>1e-7f?(v.focus[i]-v.view.eye[i])/v.distance:-direction[i];
 /* Existing renderer convention: +Z forward has +X screen-right. The Python
    reference's cross(forward,Y) has the opposite handedness; do not port it. */
 float horizontal=hypotf(v.view.forward[0],v.view.forward[2]);if(horizontal<1e-7f)return 0;
 v.view.right[0]=v.view.forward[2]/horizontal;v.view.right[1]=0;v.view.right[2]=-v.view.forward[0]/horizontal;
 v.view.up[0]=v.view.forward[1]*v.view.right[2];v.view.up[1]=v.view.forward[2]*v.view.right[0]-v.view.forward[0]*v.view.right[2];v.view.up[2]=-v.view.forward[1]*v.view.right[0];
 if(!finite3(v.view.eye)||!finite3(v.focus)||!finite3(v.view.up))return 0;
 memcpy(state->eye,v.view.eye,sizeof state->eye);memcpy(state->focus,v.focus,sizeof state->focus);state->ready=1;*out=v;return 1;
}

