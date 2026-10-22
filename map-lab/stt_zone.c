/* Bounded local scene stream. No commercial data embedded or downloaded. */
#include "stt_zone.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef struct {float p[3];uint32_t color;} Vertex;
typedef struct {float p[3][3],normal[3];} Face;
static Vertex *map_vertices;static uint16_t *map_faces,*hunter_faces;
static float *poses;static uint32_t *hunter_colors;static Face *ground,*walls;
static unsigned mv,mf,hv,hf,frames,ng,nw,phase,contact;static float spawn[3],position[3],yaw,normal_y=1;
static int active;
static int read_block(FILE *f,void *out,size_t n){return fread(out,1,n,f)==n;}
static int finite_values(const float *v,size_t n){for(size_t i=0;i<n;i++)if(!isfinite(v[i])||fabsf(v[i])>5000)return 0;return 1;}
void stt_zone_close(void){free(map_vertices);free(map_faces);free(hunter_faces);free(poses);free(hunter_colors);free(ground);free(walls);map_vertices=NULL;map_faces=hunter_faces=NULL;poses=NULL;hunter_colors=NULL;ground=walls=NULL;active=0;}
int stt_zone_active(void){return active;}
void stt_zone_reset(void){memcpy(position,spawn,sizeof position);phase=contact=0;yaw=0;normal_y=1;}
int stt_zone_load(const char *path){
 stt_zone_close();FILE *f=fopen(path,"rb");if(!f)return 0;char magic[8];uint32_t count[7];int ok=0;
 if(!read_block(f,magic,8)||memcmp(magic,"STTZONE1",8)||!read_block(f,count,sizeof count))goto done;
 mv=count[0];mf=count[1];hv=count[2];hf=count[3];frames=count[4];ng=count[5];nw=count[6];
 if(!mv||mv>32768||mf>32768||!hv||hv>8192||hf>16384||frames!=16||!ng||ng>4096||nw>4096)goto done;
 if(!read_block(f,spawn,sizeof spawn)||!finite_values(spawn,3))goto done;
 map_vertices=malloc(mv*sizeof *map_vertices);map_faces=malloc(mf*3*sizeof *map_faces);hunter_faces=malloc(hf*3*sizeof *hunter_faces);poses=malloc((size_t)frames*hv*3*sizeof *poses);hunter_colors=malloc(hv*sizeof *hunter_colors);ground=malloc(ng*sizeof *ground);walls=malloc(nw*sizeof *walls);
 if(!map_vertices||!map_faces||!hunter_faces||!poses||!hunter_colors||!ground||(nw&&!walls))goto done;
 if(!read_block(f,map_vertices,mv*sizeof *map_vertices)||!read_block(f,map_faces,mf*3*sizeof *map_faces)||!read_block(f,poses,(size_t)frames*hv*3*sizeof *poses)||!read_block(f,hunter_colors,hv*sizeof *hunter_colors)||!read_block(f,hunter_faces,hf*3*sizeof *hunter_faces)||!read_block(f,ground,ng*sizeof *ground)||!read_block(f,walls,nw*sizeof *walls)||fgetc(f)!=EOF)goto done;
 for(unsigned i=0;i<mv;i++)if(!finite_values(map_vertices[i].p,3))goto done;
 if(!finite_values(poses,(size_t)frames*hv*3))goto done;
 for(unsigned i=0;i<mf*3;i++)if(map_faces[i]>=mv)goto done;
 for(unsigned i=0;i<hf*3;i++)if(hunter_faces[i]>=hv)goto done;
 for(unsigned i=0;i<ng+nw;i++){Face *a=i<ng?ground+i:walls+i-ng;if(!finite_values(&a->p[0][0],9)||!finite_values(a->normal,3))goto done;float n=a->normal[0]*a->normal[0]+a->normal[1]*a->normal[1]+a->normal[2]*a->normal[2];if(fabsf(n-1)>.001f)goto done;}
 active=1;stt_zone_reset();ok=1;
done:fclose(f);if(!ok)stt_zone_close();return ok;
}
static int height_at(float x,float z,float ref,float *height,float *ny){
 int found=0;float best=-5001;
 for(unsigned i=0;i<ng;i++){
  const Face *f=ground+i;if(f->normal[1]<.00001f)continue;
  float ax=f->p[0][0],az=f->p[0][2],ux=f->p[1][0]-ax,uz=f->p[1][2]-az,vx=f->p[2][0]-ax,vz=f->p[2][2]-az,d=ux*vz-uz*vx;if(fabsf(d)<1e-9f)continue;
  float s=((x-ax)*vz-(z-az)*vx)/d,t=(ux*(z-az)-uz*(x-ax))/d;if(s<-.00001f||t<-.00001f||s+t>1.00001f)continue;
  float y=f->p[0][1]+s*(f->p[1][1]-f->p[0][1])+t*(f->p[2][1]-f->p[0][1]);if(y>ref+.28f||y<ref-.55f)continue;
  if(y>best){best=y;*ny=f->normal[1];found=1;}
 }
 if(found)*height=best;
 return found;
}
/* Segment/triangle crossing for swept capsule offsets; conservative wall margin. */
static int wall_cross(float x,float y,float z,float nx,float nz){
 for(unsigned i=0;i<nw;i++){
  const Face *f=walls+i;
  for(unsigned h=0;h<5;h++)for(unsigned side=0;side<5;side++){
   static const float offset[5][2]={{0,0},{.25f,0},{-.25f,0},{0,.25f},{0,-.25f}};
   float p[3]={x+offset[side][0],y+.25f+h*.305f,z+offset[side][1]},q[3]={nx+offset[side][0],p[1],nz+offset[side][1]},a=0,b=0;
   for(unsigned k=0;k<3;k++){a+=(p[k]-f->p[0][k])*f->normal[k];b+=(q[k]-f->p[0][k])*f->normal[k];}
   if(a*b>0||fabsf(a-b)<1e-8f)continue;
   float t=a/(a-b),hit[3];for(unsigned k=0;k<3;k++)hit[k]=p[k]+t*(q[k]-p[k]);
   int inside=1;
   for(unsigned e=0;e<3;e++){unsigned j=(e+1)%3;float u[3],v[3];for(unsigned k=0;k<3;k++){u[k]=f->p[j][k]-f->p[e][k];v[k]=hit[k]-f->p[e][k];}float d=(u[1]*v[2]-u[2]*v[1])*f->normal[0]+(u[2]*v[0]-u[0]*v[2])*f->normal[1]+(u[0]*v[1]-u[1]*v[0])*f->normal[2];if(d<-.0001f){inside=0;break;}}
   if(inside)return 1;
  }
 }return 0;
}
void stt_zone_move(float dx,float dz){
 if(!active||!isfinite(dx)||!isfinite(dz))return;
 float d=sqrtf(dx*dx+dz*dz);if(d>.06f){dx*=.06f/d;dz*=.06f/d;d=.06f;}
 float x=position[0]+dx,z=position[2]+dz,y=-5000,ny=1;
 static const float offsets[5][2]={{0,0},{.25f,0},{-.25f,0},{0,.25f},{0,-.25f}};
 for(unsigned i=0;i<5;i++){float h,n;if(!height_at(x+offsets[i][0],z+offsets[i][1],position[1],&h,&n)){contact=1;return;}if(n<.6691306f){contact=2;return;}if(h>y){y=h;ny=n;}}
 if(d>.000001f&&wall_cross(position[0],position[1],position[2],x,z)){contact=3;return;}
 position[0]=x;position[1]=y;position[2]=z;normal_y=ny;contact=0;if(d>.000001f){yaw=atan2f(dx,dz);phase=(phase+1)%32;}else phase=0;
}
void stt_zone_position(float out[3]){memcpy(out,position,sizeof position);}
float stt_zone_yaw(void){return yaw;}
float stt_zone_slope(void){return acosf(fmaxf(-1,fminf(1,normal_y)))*57.2957795f;}
unsigned stt_zone_contact(void){return contact;}
unsigned stt_zone_phase(void){return phase;}
unsigned stt_zone_emit(int hunter,SttZoneTriangle callback,void *context){
 if(!active||!callback)return 0;
 unsigned emitted=0,n=hunter?hf:mf;const uint16_t *indices=hunter?hunter_faces:map_faces;float sy=sinf(yaw),cy=cosf(yaw);
 for(unsigned i=0;i<n;i++){
  float p[3][3];uint32_t color=0;unsigned sum[3]={0};
  for(unsigned j=0;j<3;j++){
   unsigned index=indices[i*3+j];uint32_t col=hunter?hunter_colors[index]:map_vertices[index].color;
   if(hunter){unsigned frame=phase/2;const float *a=poses+((size_t)frame*hv+index)*3;const float *b=poses+((size_t)((frame+1)%frames)*hv+index)*3;float t=(phase&1)*.5f,x=a[0]+t*(b[0]-a[0]),y=a[1]+t*(b[1]-a[1]),z=a[2]+t*(b[2]-a[2]);p[j][0]=position[0]+x*cy+z*sy;p[j][1]=position[1]+y;p[j][2]=position[2]+z*cy-x*sy;}
   else memcpy(p[j],map_vertices[index].p,sizeof p[j]);
   for(unsigned k=0;k<3;k++)sum[k]+=(col>>(k*8))&255;
  }
  if(!hunter){float minx=fminf(p[0][0],fminf(p[1][0],p[2][0])),maxx=fmaxf(p[0][0],fmaxf(p[1][0],p[2][0])),minz=fminf(p[0][2],fminf(p[1][2],p[2][2])),maxz=fmaxf(p[0][2],fmaxf(p[1][2],p[2][2]));if(minx>position[0]+22||maxx<position[0]-22||minz>position[2]+22||maxz<position[2]-22)continue;}
  color=0xff000000u|(sum[0]/3)|((sum[1]/3)<<8)|((sum[2]/3)<<16);if(callback(context,p,color))emitted++;
 }return emitted;
}
