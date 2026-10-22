/* Test TU exposes the renderer's private math without adding production API. */
#include "../src/render.c"
#include <assert.h>
#include <stdlib.h>

static uint32_t image_a[STT_PITCH*STT_HEIGHT];
static uint32_t image_b[STT_PITCH*STT_HEIGHT];
static float test_depth[STT_WIDTH*STT_HEIGHT];
static void clear(uint32_t *image){
 fb=image;zb=test_depth;memset(image,0,sizeof image_a);memset(test_depth,0,sizeof test_depth);
}
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
 puts("PASS CPU projection anchors, double-sided winding, bounded near-plane rejection and degenerate triangle");
 return 0;
}
