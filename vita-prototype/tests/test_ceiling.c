/* Compare spans against per-pixel rays and independently reconstruct the plane. */
#include "../src/render.c"
#include <assert.h>
#include <stdlib.h>
static uint32_t a[STT_PITCH*STT_HEIGHT],b[STT_PITCH*STT_HEIGHT];
static float da[STT_WIDTH*STT_HEIGHT],db[STT_WIDTH*STT_HEIGHT];
static SttAsset body;
static SttWeapon sword;
static void clear_plane(uint32_t *pixels,float *depth){
 fb=pixels;zb=depth;memset(pixels,0,sizeof a);memset(depth,0,sizeof da);
}
static void camera_at(float yaw,float pitch,int32_t x,int32_t z){
 SttCameraView v;assert(stt_camera_view((SttCamera){yaw,pitch},x,z,&v));
 eye=(V){v.eye[0],v.eye[1],v.eye[2]};right=(V){v.right[0],v.right[1],v.right[2]};
 up=(V){v.up[0],v.up[1],v.up[2]};forward=(V){v.forward[0],v.forward[1],v.forward[2]};
 assert(eye.y>0&&eye.y<STT_CEILING_HEIGHT);
}
static V from_camera(float x,float y,float z){
 return(V){eye.x+x*right.x+y*up.x+z*forward.x,eye.y+x*right.y+y*up.y+z*forward.y,eye.z+x*right.z+y*up.z+z*forward.z};
}
static void ppm(const char *prefix,const char *name){
 char path[512];int n=snprintf(path,sizeof path,"%s-%s.ppm",prefix,name);assert(n>0&&(size_t)n<sizeof path);
 FILE *f=fopen(path,"wb");assert(f);fprintf(f,"P6\n%d %d\n255\n",STT_WIDTH,STT_HEIGHT);
 for(int y=0;y<STT_HEIGHT;y++)for(int x=0;x<STT_WIDTH;x++){
  uint32_t c=a[y*STT_PITCH+x];unsigned char rgb[3]={c&255,(c>>8)&255,(c>>16)&255};assert(fwrite(rgb,1,3,f)==3);
 }
 assert(fclose(f)==0);
}
int main(int argc,char **argv){
 assert(argc==4);unsigned long checked=0,visible=0;
 for(unsigned n=0;n<120;n++){
  float pitch=STT_CAMERA_MIN_PITCH+(n%7)*.25f;
  int32_t hx=((int)(n%9)-4)*24713,hz=((int)(n%5)-2)*48719;
  int cx=(int)floorf(hx*.001f/2),cz=(int)floorf(hz*.001f/2);
  camera_at(n*.3926990817f,pitch,hx,hz);
  clear_plane(a,da);ground_spans(cx,cz);
  plane_scanline(cx,cz,STT_CEILING_HEIGHT,RGB(78,76,108),RGB(94,91,129));
  clear_plane(b,db);ground_spans(cx,cz);
  plane_spans(cx,cz,STT_CEILING_HEIGHT,RGB(78,76,108),RGB(94,91,129));
  assert(!memcmp(a,b,sizeof a)&&!memcmp(da,db,sizeof da));
  checked+=STT_WIDTH*STT_HEIGHT;
  for(int y=0;y<STT_HEIGHT;y+=7)for(int x=0;x<STT_WIDTH;x+=11){
   uint32_t color=a[y*STT_PITCH+x];if(color!=RGB(78,76,108)&&color!=RGB(94,91,129))continue;
   float d=1/da[y*STT_WIDTH+x],sx=(x+.5f-240)/250,sy=(142-y-.5f)/250;
   V p=from_camera(sx*d,sy*d,d);assert(fabsf(p.y-STT_CEILING_HEIGHT)<.0001f);
   V screen=project(p);assert(fabsf(screen.x-x-.5f)<.005f&&fabsf(screen.y-y-.5f)<.005f);
   int gx=(int)floorf(p.x*.5f),gz=(int)floorf(p.z*.5f);
   assert(gx>=cx-8&&gx<cx+8&&gz>=cz-8&&gz<cz+8);visible++;
  }
 }
 assert(visible>1000);
 /* A nearer triangle must cover the ceiling through the shared depth buffer. */
 camera_at(.45f,STT_CAMERA_MIN_PITCH,0,0);clear_plane(a,da);
 plane_spans(0,0,STT_CEILING_HEIGHT,RGB(78,76,108),RGB(94,91,129));
 assert(da[142*STT_WIDTH+240]>0);
 tri(from_camera(-.5f,-.5f,2),from_camera(.5f,-.5f,2),from_camera(0,.5f,2),0xff123456u);
 assert(a[142*STT_PITCH+240]==0xff123456u&&da[142*STT_WIDTH+240]>.49f);
 assert(stt_asset_file(&body,argv[1])==STT_ASSET_READY);assert(stt_weapon_file(&sword,argv[2])==STT_ASSET_READY);
 SttCombat combat;stt_combat_init(&combat);SttEquipment equipment;stt_equipment_init(&equipment);
 stt_render_set_ground(2);stt_render_set_raster(1);
 for(unsigned mode=0;mode<3;mode++){
  stt_render_set_ceiling(mode);assert(stt_render_get_ceiling()==mode);
  stt_render_equipment(a,da,&combat,(SttCamera){.45f,STT_CAMERA_MIN_PITCH},22222,0,0,&body,&sword,&equipment);
  ppm(argv[3],mode==0?"off":mode==1?"reference":"spans");
  if(mode==1){memcpy(b,a,sizeof a);memcpy(db,da,sizeof da);}
  if(mode==2){
   /* The HUD labels differ; the scene must be exactly identical. */
   for(int y=60;y<239;y++)assert(!memcmp(a+y*STT_PITCH,b+y*STT_PITCH,STT_WIDTH*sizeof(uint32_t)));
   assert(!memcmp(da,db,sizeof da));
  }
 }
 stt_render_set_ceiling(99);assert(stt_render_get_ceiling()==0);
 printf("{\"camera_cases\":120,\"color_depth_comparisons\":%lu,\"independent_plane_samples\":%lu,\"height_m\":8,\"physical_measurement\":false}\n",checked,visible);
 return 0;
}
