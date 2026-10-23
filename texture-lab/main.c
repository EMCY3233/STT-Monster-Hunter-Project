#include <psp2/ctrl.h>
#include <psp2/kernel/processmgr.h>
#include <psp2/kernel/threadmgr.h>
#include <psp2/power.h>
#include <vita2d.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "gpu.h"
#include "follow_camera.h"
#include "monitor.h"
#include "pacer.h"
#include "../map-lab/stt_zone.h"
static volatile int resync;
static int power_event(int id,int count,int flags,void *user){
 (void)id;(void)count;(void)user;
 if((unsigned)flags&(SCE_POWER_CB_SYSTEM_SUSPEND|SCE_POWER_CB_SYSTEM_RESUMING|SCE_POWER_CB_SYSTEM_RESUME|SCE_POWER_CB_APP_RESUME|SCE_POWER_CB_APP_SUSPEND))resync=1;
 return 0;
}
int main(void){
 SttTexScene scene={0};SttPrototypeMonitor monitor;stt_monitor_init(&monitor);
 int gpu_ready=0,result=0,registered=0;SceUID callback=-1;vita2d_pgf *font=NULL;
 if(!vita2d_init_advanced(4*1024*1024)){sceKernelExitProcess(1);return 1;}
 vita2d_set_vblank_wait(1);vita2d_set_clear_color(RGBA8(105,132,135,255));font=vita2d_load_default_pgf();
 int map_ok=stt_zone_load("ux0:/data/STTP00001/map-zone.bin");
 int texture_ok=map_ok?stt_tex_load(&scene,"ux0:/data/STTP00001/texture-zone.bin"):0;
 int gpu_ok=texture_ok?stt_gpu_init(&scene):0;
 FILE *startup=fopen("ux0:/data/STTP00001/startup-report.txt","w");
 const char *stage=!map_ok?"MAP":!texture_ok?"TEXTURE":!gpu_ok?"GPU":"READY";
 const char *detail=!map_ok?"map stream rejected":!texture_ok?stt_tex_error():stt_gpu_error();
 if(startup){fprintf(startup,"STT00.25 stage=%s map=%d texture=%d gpu=%d nt=%u nm=%u\n%s\n",stage,map_ok,texture_ok,gpu_ok,scene.nt,scene.nm,detail);fclose(startup);}
 if(!gpu_ok){
  char error_line[256];snprintf(error_line,sizeof error_line,"STT00.25 %s FAILED: %s",stage,detail);
  for(;;){SceCtrlData error_pad;memset(&error_pad,0,sizeof error_pad);sceCtrlPeekBufferPositive(0,&error_pad,1);if(error_pad.buttons&SCE_CTRL_START)break;vita2d_start_drawing();vita2d_clear_screen();if(font){vita2d_pgf_draw_text(font,20,100,0xffffffff,.7f,error_line);vita2d_pgf_draw_text(font,20,140,0xffffffff,.7f,"startup-report.txt saved | START exits");}vita2d_end_drawing();vita2d_swap_buffers();vita2d_wait_rendering_done();}result=1;goto cleanup;
 }
 gpu_ready=1;sceCtrlSetSamplingMode(SCE_CTRL_MODE_ANALOG);
 callback=sceKernelCreateCallback("stt-texture-power",0,power_event,NULL);if(callback<0){result=1;goto cleanup;}
 if(scePowerRegisterCallback(callback)<0){result=1;goto cleanup;}registered=1;
 SttFollowCamera tracking={0};SttFollowConfig tracking_config=stt_follow_defaults();
 SttCamera camera={.45f,.4f};unsigned gait_tick=0,gait_mode=0;unsigned previous=0,target=30,linear=1,frame_us=0,telemetry_us=0,paused=0;uint64_t tick=0,acc=0,last=sceKernelGetProcessTimeWide();SttPacer pacer;stt_pacer_reset(&pacer,last,target);
 for(;;){
  uint64_t start=sceKernelGetProcessTimeWide();sceKernelCheckCallback();SceCtrlData pad;memset(&pad,0,sizeof pad);int read=sceCtrlPeekBufferPositive(0,&pad,1);if(read<0){result=1;break;}if(!read){sceKernelDelayThreadCB(1000);continue;}
  pad.buttons=stt_game_buttons(pad.buttons);unsigned pressed=pad.buttons&~previous;previous=pad.buttons;
  uint64_t elapsed=start>=last?start-last:0;last=start;
  if(resync){resync=0;paused=1;tracking=(SttFollowCamera){0};elapsed=acc=0;stt_pacer_reset(&pacer,start,target);}
  if(paused&&!pad.buttons&&!stt_axis(pad.lx)&&!stt_axis(pad.ly)&&!stt_axis(pad.rx)&&!stt_axis(pad.ry))paused=0;
  if(pressed&SCE_CTRL_START)break;
  if(pressed&SCE_CTRL_CIRCLE){target=target==30?45:30;stt_pacer_reset(&pacer,start,target);}
  if(pressed&SCE_CTRL_LTRIGGER)camera.yaw=stt_zone_yaw();
  if(pressed&SCE_CTRL_SQUARE)linear=!linear;
  if(pressed&SCE_CTRL_SELECT)stt_monitor_toggle(&monitor,start);
  if(pressed&SCE_CTRL_TRIANGLE){stt_zone_reset();camera=(SttCamera){.45f,.4f};tracking=(SttFollowCamera){0};paused=0;acc=0;}
  uint64_t stamp=sceKernelGetProcessTimeWide();unsigned ticks=stt_frame_ticks(elapsed,&acc);
  for(unsigned i=0;i<ticks&&!paused;i++){
   stt_camera_step(&camera,pad.rx,pad.ry);SttMove move=stt_camera_move(camera,pad.lx,pad.ly,0);float p[3];stt_zone_position(p);
   /* Ground and walls from the supplied scene define the movement bounds. */
   float speed=(pad.buttons&SCE_CTRL_RTRIGGER)?1.1f:.7f;move.x_mm=(int)(move.x_mm*speed);move.z_mm=(int)(move.z_mm*speed);
   stt_zone_move(move.x_mm*.001f,move.z_mm*.001f);tick++;
  }
  unsigned update_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);stamp=sceKernelGetProcessTimeWide();
  SttRenderProfile profile={0};vita2d_start_drawing();
  SceGxmContext *ctx=vita2d_get_context();sceGxmSetFrontDepthFunc(ctx,SCE_GXM_DEPTH_FUNC_ALWAYS);sceGxmSetBackDepthFunc(ctx,SCE_GXM_DEPTH_FUNC_ALWAYS);sceGxmSetFrontDepthWriteEnable(ctx,SCE_GXM_DEPTH_WRITE_ENABLED);sceGxmSetBackDepthWriteEnable(ctx,SCE_GXM_DEPTH_WRITE_ENABLED);
  /* Clear shader writes clip Z=1, initializing depth to its far value. */
  sceGxmSetViewport(ctx,480,480,272,-272,.5f,.5f);vita2d_clear_screen();
  profile.clear_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);stamp=sceKernelGetProcessTimeWide();
  float position[3],matrix[16];stt_zone_position(position);SttCameraView view;SttFollowView followed;
  if(stt_follow_step(&tracking,&tracking_config,camera,position,elapsed?elapsed*.000001f:1.0f/60,0,NULL,NULL,&followed))view=followed.view;
  else{stt_camera_view(camera,(int32_t)(position[0]*1000),(int32_t)(position[2]*1000),&view);view.eye[1]+=position[1];}
  stt_tex_matrix(matrix,&view,position,stt_zone_yaw(),0);unsigned terrain=stt_gpu_draw(&scene,0,matrix,0,linear);profile.ground_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);stamp=sceKernelGetProcessTimeWide();
  unsigned pose_phase=stt_zone_phase();
  if(scene.meshes[scene.nm-1].frames==33){
   unsigned mode=(!paused&&!stt_zone_contact()&&(stt_axis(pad.lx)||stt_axis(pad.ly)))?((pad.buttons&SCE_CTRL_RTRIGGER)?2u:1u):0u;
   unsigned period=mode==2?102u:274u;gait_tick=mode==gait_mode?(gait_tick+ticks)%period:0;gait_mode=mode;
   pose_phase=mode?(mode==2?34u:2u)+(gait_tick*32u/period):0;
  }
  stt_tex_matrix(matrix,&view,position,stt_zone_yaw(),1);unsigned hunter=stt_gpu_draw(&scene,1,matrix,pose_phase,linear);profile.body_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);stamp=sceKernelGetProcessTimeWide();
  sceGxmSetFrontDepthFunc(ctx,SCE_GXM_DEPTH_FUNC_ALWAYS);sceGxmSetBackDepthFunc(ctx,SCE_GXM_DEPTH_FUNC_ALWAYS);sceGxmSetFrontDepthWriteEnable(ctx,SCE_GXM_DEPTH_WRITE_DISABLED);sceGxmSetBackDepthWriteEnable(ctx,SCE_GXM_DEPTH_WRITE_DISABLED);
  char text[180];snprintf(text,sizeof text,"STT 00.25 GPU | %.1f FPS | CAP %u | %s | MAP %u HUNTER %u",frame_us?1000000.0f/frame_us:0,target,linear?"LINEAR":"POINT",terrain,hunter);
  if(font){vita2d_pgf_draw_text(font,16,26,0xffffffff,.7f,text);vita2d_pgf_draw_text(font,16,530,0xffffffff,.65f,paused?"Release sticks/buttons | Triangle reset":"L recenter | R run | Square filter | Circle 30/45 | Select metrics | Triangle reset | Start exit");}
  profile.hud_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);vita2d_end_drawing();unsigned render_us=profile.clear_us+profile.ground_us+profile.body_us+profile.hud_us;
  stamp=sceKernelGetProcessTimeWide();vita2d_swap_buffers();vita2d_wait_rendering_done();unsigned present_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);
  stamp=sceKernelGetProcessTimeWide();stt_monitor_frame(&monitor,"gpu",stamp,tick,0,2,linear,0,target,&profile,update_us,render_us,present_us,telemetry_us);telemetry_us=(unsigned)(sceKernelGetProcessTimeWide()-stamp);
  unsigned wait=stt_pacer_wait(&pacer,sceKernelGetProcessTimeWide());if(wait)sceKernelDelayThreadCB(wait);frame_us=(unsigned)(sceKernelGetProcessTimeWide()-start);
 }
cleanup:
 vita2d_wait_rendering_done();stt_monitor_close(&monitor);if(registered)scePowerUnregisterCallback(callback);if(callback>=0)sceKernelDeleteCallback(callback);
 if(gpu_ready)stt_gpu_close();
 if(font)vita2d_free_pgf(font);
 stt_tex_close(&scene);stt_zone_close();vita2d_fini();sceKernelExitProcess(result);return result;
}
