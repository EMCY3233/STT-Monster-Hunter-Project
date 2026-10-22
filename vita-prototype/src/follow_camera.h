#ifndef STT_FOLLOW_CAMERA_H
#define STT_FOLLOW_CAMERA_H
#include "control.h"
/* Metres, radians, Y up. Sweep returns free segment distance including radius;
   it must handle initial overlap. NULL explicitly means no world protection. */
typedef float (*SttCameraSweep)(void *,const float[3],const float[3],float);
typedef struct {float distance,focus_height,follow_rate,recovery_rate,radius,skin,min_height;} SttFollowConfig;
typedef struct {float focus[3],eye[3];int ready;} SttFollowCamera;
typedef struct {SttCameraView view;float focus[3],distance,dt_used;unsigned collision,world_protection,framing_compromised;} SttFollowView;
SttFollowConfig stt_follow_defaults(void);
/* Angles/input remain owned by SttCamera and the existing 60 Hz controller.
   This updates tracking once per rendered frame. Failure leaves state intact. */
int stt_follow_step(SttFollowCamera *,const SttFollowConfig *,SttCamera,const float[3],float,int,SttCameraSweep,void *,SttFollowView *);
#endif
