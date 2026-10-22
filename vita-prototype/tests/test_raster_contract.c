/* Test TU exposes the renderer's private math without adding production API. */
#include "../src/render.c"
#include <assert.h>
#include <stdlib.h>

static uint32_t image_a[STT_PITCH*STT_HEIGHT];
static uint32_t image_b[STT_PITCH*STT_HEIGHT];
static float test_depth[STT_WIDTH*STT_HEIGHT];
static float reference_depth[STT_WIDTH*STT_HEIGHT];
static void clear(uint32_t *image){
 fb=image;zb=test_depth;memset(image,0,sizeof image_a);memset(test_depth,0,sizeof test_depth);
}
static uint64_t fake_clock(void){static uint64_t t;t+=10;return t;}
int main(void){
 eye=(V){0,0,0};right=(V){1,0,0};up=(V){0,1,0};forward=(V){0,0,1};
 V a=project((V){0,0,2}),b=project((V){.8f,.4f,2});
 assert(a.x==240&&a.y==142&&a.z==2);
 assert(fabsf(b.x-340)<.0001f&&fabsf(b.y-92)<.0001f);
 clear(image_a);tri((V){-.5f,-.5f,2},(V){.5f,-.5f,2},(V){0,.5f,2},0xff123456u);
 unsigned painted=0;for(unsigned i=0;i<STT_PITCH*STT_HEIGHT;i++)painted+=image_a[i]!=0;
 assert(painted>100);
 clear(image_b);tri((V){0,.5f,2},(V){.5f,-.5f,2},(V){-.5f,-.5f,2},0xff123456u);
 assert(!memcmp(image_a,image_b,sizeof image_a)); /* Explicitly double-sided. */
 clear(image_b);tri((V){-.5f,-.5f,.1f},(V){.5f,-.5f,2},(V){0,.5f,2},0xffffffffu);
 for(unsigned i=0;i<STT_PITCH*STT_HEIGHT;i++)assert(image_b[i]==0);
 clear(image_b);tri((V){-.5f,-.5f,-1},(V){.5f,-.5f,-1},(V){0,.5f,-1},0xffffffffu);
 for(unsigned i=0;i<STT_PITCH*STT_HEIGHT;i++)assert(image_b[i]==0);
 clear(image_b);tri((V){0,0,2},(V){0,0,2},(V){0,0,2},0xffffffffu);
 for(unsigned i=0;i<STT_PITCH*STT_HEIGHT;i++)assert(image_b[i]==0);
 /* Compare the specialized plane to independent projected world samples. */
 for(unsigned a=0;a<4;a++)for(unsigned b=0;b<3;b++){
  float yaw=a*1.5707963268f,pitch=.12f+b*.4f,sy=sinf(yaw),cy=cosf(yaw),sp=sinf(pitch),cp=cosf(pitch);
  eye=(V){-sy*6*cp,1.1f+sp*6,-cy*6*cp};right=(V){cy,0,-sy};forward=(V){sy*cp,-sp,cy*cp};up=(V){sy*sp,cp,cy*sp};
  clear(image_a);ground_scanline(0,0);unsigned checked=0;
  for(int y=60;y<239;y+=13)for(int x=3;x<STT_WIDTH;x+=31){
   float inv=test_depth[y*STT_WIDTH+x];if(inv==0)continue;
   float z=1/inv,sx=((x+.5f)-240)/250,uy=(142-(y+.5f))/250;
   V world={eye.x+z*(forward.x+sx*right.x+uy*up.x),eye.y+z*(forward.y+sx*right.y+uy*up.y),eye.z+z*(forward.z+sx*right.z+uy*up.z)};
   assert(fabsf(world.y)<.00001f);V pixel=project(world);
   assert(fabsf(pixel.x-(x+.5f))<.0003f&&fabsf(pixel.y-(y+.5f))<.0003f);
   int gx=(int)floorf(world.x*.5f),gz=(int)floorf(world.z*.5f);
   assert(gx>=-8&&gx<8&&gz>=-8&&gz<8);checked++;
  }
  assert(checked>25);
 }
 /* Span ground must match the unmodified scanline ground bit for bit. */
 unsigned long compared=0;
 for(unsigned n=0;n<120;n++){
  float yaw=n*.3926990817f,pitch=STT_CAMERA_MIN_PITCH+(n%5)*.375f;
  float hx=((int)(n%7)-3)*.37f,hz=((int)(n%9)-4)*.43f;
  if(n>=80){hx=n&1?99.37f:-99.37f;hz=n&2?98.71f:-98.71f;}
  SttCameraView view;assert(stt_camera_view((SttCamera){yaw,pitch},(int32_t)lroundf(hx*1000),(int32_t)lroundf(hz*1000),&view));
  eye=(V){view.eye[0],view.eye[1],view.eye[2]};right=(V){view.right[0],view.right[1],view.right[2]};
  forward=(V){view.forward[0],view.forward[1],view.forward[2]};up=(V){view.up[0],view.up[1],view.up[2]};
  int cx=(int)floorf(hx/2),cz=(int)floorf(hz/2);
  clear(image_a);ground_scanline(cx,cz);memcpy(reference_depth,test_depth,sizeof reference_depth);
  clear(image_b);ground_spans(cx,cz);
  assert(!memcmp(image_a,image_b,sizeof image_a));
  assert(!memcmp(reference_depth,test_depth,sizeof reference_depth));
  compared+=STT_WIDTH*STT_HEIGHT;
 }
 printf("PASS span ground matches %lu pixels and inverse depths across 120 cameras/positions\n",compared);
 /* New raster is checked against the preserved implementation, not its own math. */
 eye=(V){0,0,0};right=(V){1,0,0};up=(V){0,1,0};forward=(V){0,0,1};
 for(unsigned n=0;n<24;n++){
  V a={-.9f+n*.015f,-.6f,1.7f},b={.8f,.15f+n*.01f,2.8f},c={-.1f,.7f,2.1f};
  clear(image_a);tri_reference(a,b,c,0xff123456u);float old_depth[STT_WIDTH*STT_HEIGHT];memcpy(old_depth,test_depth,sizeof old_depth);
  clear(image_b);tri_incremental(a,b,c,0xff123456u);
  unsigned shared=0;
  for(int y=1;y<STT_HEIGHT-1;y++)for(int x=1;x<STT_WIDTH-1;x++){
   int at=y*STT_PITCH+x;int pa=image_a[at]!=0,pb=image_b[at]!=0;
   if(pa&&pb){assert(fabsf(old_depth[y*STT_WIDTH+x]-test_depth[y*STT_WIDTH+x])<.002f);shared++;}
   if(pa!=pb){
    const uint32_t *other=pa?image_b:image_a;int neighbor=0;
    for(int j=-1;j<=1;j++)for(int k=-1;k<=1;k++)neighbor|=other[(y+j)*STT_PITCH+x+k]!=0;
    assert(neighbor);
   }
  }
  assert(shared>2000);
 }
 stt_render_set_clock(fake_clock);SttCombat combat;stt_combat_init(&combat);
 stt_render(image_a,test_depth,&combat,(SttCamera){.45f,.4f},33333,0,0);
 const SttRenderProfile *profile=stt_render_profile();
 assert(profile->clear_us==10&&profile->ground_us==10&&profile->body_us==10&&profile->weapon_us==10&&profile->target_us==10&&profile->hud_us==10);
 stt_render_set_clock(NULL);
 puts("PASS CPU projection anchors, double-sided winding, bounded near-plane rejection and degenerate triangle");
 return 0;
}
