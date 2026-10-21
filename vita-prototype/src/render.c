#include "render.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#define RGB(r,g,b) (0xff000000u | (unsigned)(b)<<16 | (unsigned)(g)<<8 | (r))
typedef struct{float x,y,z;} V;
static uint32_t *fb;static float *zb;static V eye,right,up,forward;
static V sub(V a,V b){return(V){a.x-b.x,a.y-b.y,a.z-b.z};}
static float dot(V a,V b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static V project(V p){V r=sub(p,eye);float z=dot(r,forward);return(V){240+250*dot(r,right)/z,142-250*dot(r,up)/z,z};}
static float edge(V a,V b,float x,float y){return(x-a.x)*(b.y-a.y)-(y-a.y)*(b.x-a.x);}
static int clamp(int x,int a,int b){return x<a?a:x>b?b:x;}
static void tri(V a,V b,V c,uint32_t color){
 a=project(a);b=project(b);c=project(c);
 /* Bounded near-plane rejection; ground is tiled so no huge near triangles. */
 if(a.z<.15f||b.z<.15f||c.z<.15f)return;
 int x0=clamp((int)fminf(a.x,fminf(b.x,c.x)),0,STT_WIDTH-1);
 int x1=clamp((int)fmaxf(a.x,fmaxf(b.x,c.x)),0,STT_WIDTH-1);
 int y0=clamp((int)fminf(a.y,fminf(b.y,c.y)),0,STT_HEIGHT-1);
 int y1=clamp((int)fmaxf(a.y,fmaxf(b.y,c.y)),0,STT_HEIGHT-1);
 float area=edge(a,b,c.x,c.y);if(fabsf(area)<.001f)return;
 for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
   float u=edge(b,c,x+.5f,y+.5f)/area,v=edge(c,a,x+.5f,y+.5f)/area,w=1-u-v;
   if(u>=0&&v>=0&&w>=0){float inv=u/a.z+v/b.z+w/c.z;int at=y*STT_WIDTH+x;
     if(inv>zb[at]){zb[at]=inv;fb[y*STT_PITCH+x]=color;}}
 }
}
static void box(float x,float y,float z,float sx,float sy,float sz,float yaw,uint32_t color){
 V p[8];float s=sinf(yaw),c=cosf(yaw);
 for(int i=0;i<8;i++){float dx=(i&1?1:-1)*sx/2,dz=(i&4?1:-1)*sz/2;
 p[i]=(V){x+dx*c+dz*s,y+(i&2?1:-1)*sy/2,z+dz*c-dx*s};}
 static const unsigned char faces[12][3]={{0,1,3},{0,3,2},{4,6,7},{4,7,5},{0,4,5},{0,5,1},{2,3,7},{2,7,6},{0,2,6},{0,6,4},{1,5,7},{1,7,3}};
 for(int i=0;i<12;i++){unsigned shade=(unsigned)(i/2)*7;uint32_t col=color;
 if(shade)col=RGB(((color&255)* (100-shade))/100,(((color>>8)&255)*(100-shade))/100,(((color>>16)&255)*(100-shade))/100);
 tri(p[faces[i][0]],p[faces[i][1]],p[faces[i][2]],col);}
}
/* Original compact bitmap alphabet; columns, low bit at top. */
static const unsigned char glyph[38][5]={
 {0x3e,0x51,0x49,0x45,0x3e},{0,0x42,0x7f,0x40,0},{0x62,0x51,0x49,0x49,0x46},{0x22,0x49,0x49,0x49,0x36},{0x18,0x14,0x12,0x7f,0x10},{0x27,0x45,0x45,0x45,0x39},{0x3c,0x4a,0x49,0x49,0x30},{1,0x71,9,5,3},{0x36,0x49,0x49,0x49,0x36},{6,0x49,0x49,0x29,0x1e},
 {0x7e,9,9,9,0x7e},{0x7f,0x49,0x49,0x49,0x36},{0x3e,0x41,0x41,0x41,0x22},{0x7f,0x41,0x41,0x22,0x1c},{0x7f,0x49,0x49,0x49,0x41},{0x7f,9,9,9,1},{0x3e,0x41,0x49,0x49,0x7a},{0x7f,8,8,8,0x7f},{0,0x41,0x7f,0x41,0},{0x20,0x40,0x41,0x3f,1},{0x7f,8,0x14,0x22,0x41},{0x7f,0x40,0x40,0x40,0x40},{0x7f,2,0xc,2,0x7f},{0x7f,4,8,0x10,0x7f},{0x3e,0x41,0x41,0x41,0x3e},{0x7f,9,9,9,6},{0x3e,0x41,0x51,0x21,0x5e},{0x7f,9,0x19,0x29,0x46},{0x46,0x49,0x49,0x49,0x31},{1,1,0x7f,1,1},{0x3f,0x40,0x40,0x40,0x3f},{0x1f,0x20,0x40,0x20,0x1f},{0x3f,0x40,0x38,0x40,0x3f},{0x63,0x14,8,0x14,0x63},{3,4,0x78,4,3},{0x61,0x51,0x49,0x45,0x43},{0,0x36,0x36,0,0},{8,8,8,8,8}};
static void rect(int x,int y,int w,int h,uint32_t color){for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++)if(i>=0&&i<STT_WIDTH&&j>=0&&j<STT_HEIGHT)fb[j*STT_PITCH+i]=color;}
static void text(int x,int y,const char*s,uint32_t color){for(;*s;s++,x+=6){int n=*s>='0'&&*s<='9'?*s-'0':*s>='A'&&*s<='Z'?*s-'A'+10:*s==':'?36:*s=='-'?37:-1;
 if(n<0){continue;}for(int i=0;i<5;i++)for(int j=0;j<7;j++)if(glyph[n][i]&(1<<j))rect(x+i,y+j,1,1,color);}}
static int pose_triangle(void *context,const float p[3][3]){
 (void)context;
 tri((V){p[0][0],p[0][1],p[0][2]},(V){p[1][0],p[1][1],p[1][2]},(V){p[2][0],p[2][1],p[2][2]},RGB(42,168,213));return 1;
}
void stt_render_with_asset(uint32_t *pixels,float *depth,const SttCombat*c,SttCamera cam,unsigned frame_us,unsigned dropped,int paused,SttAsset *asset){
 fb=pixels;zb=depth;memset(zb,0,sizeof(float)*STT_WIDTH*STT_HEIGHT);
 for(int y=0;y<STT_HEIGHT;y++)for(int x=0;x<STT_WIDTH;x++)fb[y*STT_PITCH+x]=RGB(18+y/12,27+y/10,47+y/8);
 float hx=c->hunter.x_mm*.001f,hz=c->hunter.z_mm*.001f,sy=sinf(cam.yaw),cy=cosf(cam.yaw),sp=sinf(cam.pitch),cp=cosf(cam.pitch);
 eye=(V){hx-sy*6*cp,1.1f+sp*6,hz-cy*6*cp};right=(V){cy,0,-sy};forward=(V){sy*cp,-sp,cy*cp};up=(V){sy*sp,cp,cy*sp};
 int center_x=(int)floorf(hx/2),center_z=(int)floorf(hz/2);
 for(int z=center_z-8;z<center_z+8;z++)for(int x=center_x-8;x<center_x+8;x++){
  uint32_t col=(x+z)&1?RGB(49,67,69):RGB(57,77,78);V a={x*2,0,z*2},b={x*2+2,0,z*2},d={x*2,0,z*2+2},e={x*2+2,0,z*2+2};tri(a,b,e,col);tri(a,e,d,col);
 }
 float yaw=c->hunter.yaw_turn*(6.28318530718f/65536);
 int posed=asset&&asset->status==STT_ASSET_READY&&stt_pose_emit(&asset->pose,stt_asset_clip(asset,c->hunter.state!=STT_IDLE),c->tick,c->hunter.x_mm,c->hunter.z_mm,c->hunter.yaw_turn,&asset->scratch,pose_triangle,NULL);
 if(!posed){
  if(asset&&asset->status==STT_ASSET_READY)asset->status=STT_ASSET_INVALID;
  box(hx,.8f,hz,.55f,.8f,.32f,yaw,RGB(42,168,213));box(hx,1.45f,hz,.38f,.4f,.38f,yaw,RGB(245,207,161));
  box(hx-.17f,.25f,hz,.20f,.5f,.23f,yaw,RGB(30,66,101));box(hx+.17f,.25f,hz,.20f,.5f,.23f,yaw,RGB(30,66,101));
 }
 float blade_yaw=yaw+(c->hunter.state==STT_ACTIVE?.5f:0);float reach=c->hunter.state==STT_ACTIVE?1.0f:.65f;
 box(hx+sinf(blade_yaw)*reach+cosf(yaw)*.4f,.85f,hz+cosf(blade_yaw)*reach-sinf(yaw)*.4f,.10f,.10f,1.6f,blade_yaw,c->hunter.state==STT_ACTIVE?RGB(255,234,125):RGB(172,205,220));
 float tx=c->target.x_mm*.001f,tz=c->target.z_mm*.001f;
 if(c->target.hp>0)box(tx,.7f,tz,.65f,1.4f,.65f,0,c->target.reaction_ticks?RGB(255,231,108):RGB(230,94,76));
 else box(tx,.12f,tz,.85f,.24f,.85f,0,RGB(88,70,70));
 rect(0,0,480,32,RGB(9,17,27));text(8,5,"STT VITA PROTOTYPE 0-11 ORIGINAL SCENE",RGB(119,223,235));
 char line[100];snprintf(line,sizeof line,"TARGET HP %d   COMBO %u   TICK %u",c->target.hp,(unsigned)c->hunter.combo,(unsigned)c->tick);text(8,18,line,RGB(238,239,223));
 rect(0,239,480,33,RGB(9,17,27));text(8,244,"LEFT MOVE  RIGHT CAMERA  CROSS ATTACK  START EXIT",RGB(238,239,223));
 snprintf(line,sizeof line,"TRIANGLE RESET  FRAME US %u  DROPPED %u",frame_us,dropped);text(8,257,line,RGB(153,185,191));
 if(paused){rect(85,115,310,34,RGB(9,17,27));text(102,128,"RESUMED - RELEASE STICKS AND BUTTONS",RGB(255,234,125));}
 if(asset)text(8,36,asset->status==STT_ASSET_READY?"ASSET READY":asset->status==STT_ASSET_MISSING?"ASSET MISSING - SIMPLE HUNTER":"ASSET INVALID - SIMPLE HUNTER",RGB(255,234,125));
}
void stt_render(uint32_t *pixels,float *depth,const SttCombat*c,SttCamera cam,unsigned frame_us,unsigned dropped,int paused){
 stt_render_with_asset(pixels,depth,c,cam,frame_us,dropped,paused,NULL);
}

void stt_render_error(uint32_t *pixels,int error){
 fb=pixels;rect(0,0,STT_WIDTH,STT_HEIGHT,RGB(24,12,18));
 text(24,70,"STT PROTOTYPE ERROR - CLOSING",RGB(255,210,190));
 char code[64];snprintf(code,sizeof code,"CODE %08X",(unsigned)error);text(24,90,code,RGB(255,240,230));
 text(24,110,"RECORD CODE - NO SAVE DATA WAS WRITTEN",RGB(210,210,220));
}
