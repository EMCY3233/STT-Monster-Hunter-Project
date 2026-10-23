#ifndef STT_TEXTURE_SCENE_H
#define STT_TEXTURE_SCENE_H
#include <stdint.h>
#include "control.h"
typedef struct {float x,y,z,u,v;} SttTexVertex;
typedef struct {unsigned width,height;unsigned char *rgba;} SttTexImage;
typedef struct {unsigned hunter,nv,ni,texture,frames;SttTexVertex *vertices;uint16_t *indices;} SttTexMesh;
typedef struct {unsigned nt,nm;SttTexImage *textures;SttTexMesh *meshes;} SttTexScene;
const char *stt_tex_error(void);
int stt_tex_load(SttTexScene *scene,const char *path);
void stt_tex_close(SttTexScene *scene);
/* Column-major matrix: positive view Z, near/far mapped to -1/+1. */
void stt_tex_matrix(float out[16],const SttCameraView *view,const float position[3],float yaw,int hunter);
#endif
