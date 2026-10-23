#ifndef STT_TEXTURE_GPU_H
#define STT_TEXTURE_GPU_H
#include "scene.h"
const char *stt_gpu_error(void);
int stt_gpu_init(const SttTexScene *scene);
void stt_gpu_close(void);
unsigned stt_gpu_draw(const SttTexScene *scene,int hunter,const float matrix[16],unsigned phase,int linear);
#endif
