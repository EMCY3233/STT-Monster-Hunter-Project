/* Uses libvita2d's precompiled shader objects, not a runtime shader compiler. */
#include "gpu.h"
#include <vita2d.h>
#include <stdlib.h>
#include <string.h>
extern const SceGxmProgram texture_v_gxp_start,texture_f_gxp_start;
static SceGxmShaderPatcherId vertex_id,fragment_id;
static SceGxmVertexProgram *vp;
static SceGxmFragmentProgram *fp;
static const SceGxmProgramParameter *wvp;
static vita2d_texture *images[96];
static int registered_v,registered_f;
void stt_gpu_close(void){
 SceGxmShaderPatcher *p=vita2d_get_shader_patcher();
 for(unsigned i=0;i<96;i++){if(images[i])vita2d_free_texture(images[i]);images[i]=NULL;}
 if(fp)sceGxmShaderPatcherReleaseFragmentProgram(p,fp);
 if(vp)sceGxmShaderPatcherReleaseVertexProgram(p,vp);
 if(registered_f)sceGxmShaderPatcherUnregisterProgram(p,fragment_id);
 if(registered_v)sceGxmShaderPatcherUnregisterProgram(p,vertex_id);
 fp=NULL;vp=NULL;registered_f=registered_v=0;
}
int stt_gpu_init(const SttTexScene *s){
 SceGxmShaderPatcher *p=vita2d_get_shader_patcher();
 if(sceGxmShaderPatcherRegisterProgram(p,&texture_v_gxp_start,&vertex_id)<0)return 0;
 registered_v=1;
 if(sceGxmShaderPatcherRegisterProgram(p,&texture_f_gxp_start,&fragment_id)<0)goto fail;
 registered_f=1;
 const SceGxmProgramParameter *position=sceGxmProgramFindParameterByName(&texture_v_gxp_start,"aPosition"),*uv=sceGxmProgramFindParameterByName(&texture_v_gxp_start,"aTexcoord");
 wvp=sceGxmProgramFindParameterByName(&texture_v_gxp_start,"wvp");if(!position||!uv||!wvp)goto fail;
 SceGxmVertexAttribute attr[2];memset(attr,0,sizeof attr);
 attr[0].format=attr[1].format=SCE_GXM_ATTRIBUTE_FORMAT_F32;attr[0].componentCount=3;attr[1].componentCount=2;attr[1].offset=12;
 attr[0].regIndex=sceGxmProgramParameterGetResourceIndex(position);attr[1].regIndex=sceGxmProgramParameterGetResourceIndex(uv);
 SceGxmVertexStream stream={sizeof(SttTexVertex),SCE_GXM_INDEX_SOURCE_INDEX_16BIT};
 if(sceGxmShaderPatcherCreateVertexProgram(p,vertex_id,attr,2,&stream,1,&vp)<0)goto fail;
 if(sceGxmShaderPatcherCreateFragmentProgram(p,fragment_id,SCE_GXM_OUTPUT_REGISTER_FORMAT_UCHAR4,SCE_GXM_MULTISAMPLE_NONE,NULL,&texture_v_gxp_start,&fp)<0)goto fail;
 for(unsigned i=0;i<s->nt;i++){
  const SttTexImage *t=s->textures+i;images[i]=vita2d_create_empty_texture(t->width,t->height);if(!images[i])goto fail;
  unsigned char *dst=vita2d_texture_get_datap(images[i]);unsigned stride=vita2d_texture_get_stride(images[i]);
  for(unsigned y=0;y<t->height;y++)memcpy(dst+y*stride,t->rgba+y*t->width*4,t->width*4);
  sceGxmTextureSetUAddrMode(&images[i]->gxm_tex,SCE_GXM_TEXTURE_ADDR_REPEAT);sceGxmTextureSetVAddrMode(&images[i]->gxm_tex,SCE_GXM_TEXTURE_ADDR_REPEAT);
 }
 return 1;
fail:stt_gpu_close();return 0;
}
unsigned stt_gpu_draw(const SttTexScene *s,int hunter,const float matrix[16],unsigned phase,int linear){
 SceGxmContext *ctx=vita2d_get_context();unsigned tris=0;
 sceGxmSetVertexProgram(ctx,vp);sceGxmSetFragmentProgram(ctx,fp);
 sceGxmSetCullMode(ctx,SCE_GXM_CULL_NONE);
 sceGxmSetFrontDepthFunc(ctx,SCE_GXM_DEPTH_FUNC_LESS_EQUAL);sceGxmSetBackDepthFunc(ctx,SCE_GXM_DEPTH_FUNC_LESS_EQUAL);
 sceGxmSetFrontDepthWriteEnable(ctx,SCE_GXM_DEPTH_WRITE_ENABLED);sceGxmSetBackDepthWriteEnable(ctx,SCE_GXM_DEPTH_WRITE_ENABLED);
 sceGxmSetViewport(ctx,480,480,272,-272,.5f,.5f);
 void *uniforms=NULL;if(sceGxmReserveVertexDefaultUniformBuffer(ctx,&uniforms)<0)return 0;
 sceGxmSetUniformDataF(uniforms,wvp,0,16,matrix);
 for(unsigned i=0;i<s->nm;i++){
  const SttTexMesh *m=s->meshes+i;if(m->hunter!=(unsigned)hunter)continue;
  SttTexVertex *vertices=vita2d_pool_memalign(m->nv*sizeof *vertices,16);uint16_t *indices=vita2d_pool_memalign(m->ni*2,16);if(!vertices||!indices)break;
  memcpy(indices,m->indices,m->ni*2);
  const SttTexVertex *a=m->vertices+((phase/2)%m->frames)*m->nv,*b=m->vertices+(((phase/2)+1)%m->frames)*m->nv;
  memcpy(vertices,a,m->nv*sizeof *vertices);
  if(hunter&&(phase&1))for(unsigned j=0;j<m->nv;j++){vertices[j].x=(a[j].x+b[j].x)*.5f;vertices[j].y=(a[j].y+b[j].y)*.5f;vertices[j].z=(a[j].z+b[j].z)*.5f;}
  vita2d_texture *tex=images[m->texture];vita2d_texture_set_filters(tex,linear?SCE_GXM_TEXTURE_FILTER_LINEAR:SCE_GXM_TEXTURE_FILTER_POINT,linear?SCE_GXM_TEXTURE_FILTER_LINEAR:SCE_GXM_TEXTURE_FILTER_POINT);
  sceGxmSetFragmentTexture(ctx,0,&tex->gxm_tex);sceGxmSetVertexStream(ctx,0,vertices);
  if(sceGxmDraw(ctx,SCE_GXM_PRIMITIVE_TRIANGLES,SCE_GXM_INDEX_FORMAT_U16,indices,m->ni)>=0)tris+=m->ni/3;
 }
 return tris;
}
