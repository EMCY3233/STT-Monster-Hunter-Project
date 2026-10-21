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
 puts("PASS CPU projection anchors, double-sided winding, bounded near-plane rejection and degenerate triangle");
 return 0;
}
