#include "scene.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static int block(FILE *f,void *out,size_t n){return fread(out,1,n,f)==n;}
void stt_tex_close(SttTexScene *s){
 if(!s)return;
 for(unsigned i=0;i<s->nt;i++)free(s->textures[i].rgba);
 for(unsigned i=0;i<s->nm;i++){free(s->meshes[i].vertices);free(s->meshes[i].indices);}
 free(s->textures);free(s->meshes);memset(s,0,sizeof *s);
}
int stt_tex_load(SttTexScene *s,const char *path){
 SttTexScene tmp={0};FILE *f=fopen(path,"rb");if(!f)return 0;
 int ok=0;char magic[8];uint32_t counts[2];size_t budget=0;
 if(!block(f,magic,8)||memcmp(magic,"STTTEX01",8)||!block(f,counts,8)||!counts[0]||counts[0]>96||!counts[1]||counts[1]>128)goto done;
 tmp.textures=calloc(counts[0],sizeof *tmp.textures);tmp.meshes=calloc(counts[1],sizeof *tmp.meshes);
 if(!tmp.textures||!tmp.meshes)goto done;
 tmp.nt=counts[0];tmp.nm=counts[1];
 for(unsigned i=0;i<tmp.nt;i++){
  uint32_t dim[2];if(!block(f,dim,8)||dim[0]<8||dim[1]<8||dim[0]>512||dim[1]>512||(dim[0]&(dim[0]-1))||(dim[1]&(dim[1]-1)))goto done;
  SttTexImage *t=tmp.textures+i;t->width=dim[0];t->height=dim[1];size_t bytes=(size_t)dim[0]*dim[1]*4;budget+=bytes;if(budget>32*1024*1024)goto done;
  t->rgba=malloc(bytes);if(!t->rgba||!block(f,t->rgba,bytes))goto done;
 }
 for(unsigned i=0;i<tmp.nm;i++){
  uint32_t a[5];if(!block(f,a,20)||a[0]>1||!a[1]||a[1]>8192||!a[2]||a[2]>49152||a[2]%3||a[3]>=tmp.nt||a[4]!=(a[0]?16u:1u))goto done;
  SttTexMesh *m=tmp.meshes+i;m->hunter=a[0];m->nv=a[1];m->ni=a[2];m->texture=a[3];m->frames=a[4];
  size_t nv=(size_t)m->nv*m->frames,bytes=nv*sizeof *m->vertices;budget+=bytes+m->ni*2;if(budget>32*1024*1024)goto done;
  m->vertices=malloc(bytes);m->indices=malloc(m->ni*2);if(!m->vertices||!m->indices||!block(f,m->vertices,bytes)||!block(f,m->indices,m->ni*2))goto done;
  for(size_t j=0;j<nv;j++){const SttTexVertex *v=m->vertices+j;if(!isfinite(v->x)||!isfinite(v->y)||!isfinite(v->z)||fabsf(v->x)>5000||fabsf(v->y)>5000||fabsf(v->z)>5000||!isfinite(v->u)||!isfinite(v->v)||fabsf(v->u)>4096||fabsf(v->v)>4096)goto done;}
  for(unsigned j=0;j<m->ni;j++)if(m->indices[j]>=m->nv)goto done;
 }
 if(fgetc(f)!=EOF)goto done;
 stt_tex_close(s);*s=tmp;memset(&tmp,0,sizeof tmp);ok=1;
done:fclose(f);stt_tex_close(&tmp);return ok;
}
static float dot(const float a[3],const float b[3]){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
void stt_tex_matrix(float out[16],const SttCameraView *v,const float p[3],float yaw,int hunter){
 float sy=hunter?sinf(yaw):0,cy=hunter?cosf(yaw):1;
 float axes[3][3]={{cy,0,-sy},{0,1,0},{sy,0,cy}},delta[3];
 for(unsigned i=0;i<3;i++)delta[i]=(hunter?p[i]:0)-v->eye[i];
 const float fx=500.0f/480.0f,fy=500.0f/272.0f,n=.15f,f=80.0f,a=(f+n)/(f-n),b=-2*f*n/(f-n);
 for(unsigned i=0;i<4;i++){
  const float *axis=i<3?axes[i]:delta;float z=dot(axis,v->forward);
  out[i*4]=fx*dot(axis,v->right);out[i*4+1]=fy*dot(axis,v->up);out[i*4+2]=a*z+(i==3?b:0);out[i*4+3]=z;
 }
}
