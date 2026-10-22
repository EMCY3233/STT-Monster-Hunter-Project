#include <psp2/ctrl.h>
#include <psp2/display.h>
#include <psp2/kernel/processmgr.h>
#include <psp2/kernel/threadmgr.h>
#include <psp2/kernel/sysmem.h>
#include <psp2/power.h>
#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "control.h"
#include "render.h"
#include "snapshot.h"
#include "monitor.h"
static volatile int resync_requested;
static SttAsset original_asset;
static SttWeapon equipped_sword;
static int power_callback(int id,int count,int flags,void *user){
 (void)id;(void)count;(void)user;
 if((unsigned)flags&(SCE_POWER_CB_SYSTEM_SUSPEND|SCE_POWER_CB_SYSTEM_RESUMING|SCE_POWER_CB_SYSTEM_RESUME|SCE_POWER_CB_APP_RESUME|SCE_POWER_CB_APP_SUSPEND))resync_requested=1;
 return 0;
}
int main(void){
 SceUID memory[2]={-1,-1},callback=-1;uint32_t *buffers[2]={NULL,NULL};float *depth=NULL;uint32_t *cached_pixels=NULL;
 int result=0,registered=0,shown=0,front=0,need_release=0;unsigned previous=0,pending_attack=0,pending_toggle=0,frame_us=0,dropped=0,update_us=0;
 uint64_t previous_time=0,accumulator=0,seq=0,next_sample=0,start=sceKernelGetProcessTimeWide();
 char session[65];snprintf(session,sizeof session,"vita-play-%" PRIx64,start);
 SttPrototypeMonitor monitor;stt_monitor_init(&monitor);unsigned render_us=0,present_us=0,telemetry_us=0;
 SttCombat combat;stt_combat_init(&combat);SttEquipment equipment;stt_equipment_init(&equipment);SttCamera camera={.45f,.40f};SttPlayMailbox mailbox={0};
 stt_asset_file(&original_asset,"app0:/assets/hunter-body.pose.json");
 stt_weapon_file(&equipped_sword,"app0:/assets/quaternius-sword.pose.json");
 /* Two CDRAM buffers, each 512*272*4 rounded to 256 KiB. Original asset packaged in app0. */
 for(int i=0;i<2;i++){
  memory[i]=sceKernelAllocMemBlock("stt-prototype-fb",SCE_KERNEL_MEMBLOCK_TYPE_USER_CDRAM_RW,0xC0000,NULL);
  if(memory[i]<0){result=memory[i];goto cleanup;}
  result=sceKernelGetMemBlockBase(memory[i],(void**)&buffers[i]);if(result<0)goto cleanup;
  memset(buffers[i],0,0xC0000);
 }
 cached_pixels=calloc(STT_PITCH*STT_HEIGHT,sizeof(uint32_t));
 depth=malloc(sizeof(float)*STT_WIDTH*STT_HEIGHT);if(!depth||!cached_pixels){result=-1;goto cleanup;}
 result=sceCtrlSetSamplingMode(SCE_CTRL_MODE_ANALOG);if(result<0)goto cleanup;
 callback=sceKernelCreateCallback("stt-prototype-power",0,power_callback,NULL);if(callback<0){result=callback;goto cleanup;}
 result=scePowerRegisterCallback(callback);if(result<0)goto cleanup;registered=1;
 previous_time=sceKernelGetProcessTimeWide();
 for(;;){
  uint64_t frame_start=sceKernelGetProcessTimeWide();sceKernelCheckCallback();
  SceCtrlData controls;memset(&controls,0,sizeof controls);
  result=sceCtrlPeekBufferPositive(0,&controls,1);if(result<0)break;
  if(result==0){sceKernelDelayThreadCB(1000);continue;}
  controls.buttons=stt_game_buttons(controls.buttons);
  int clock_reset=frame_start<previous_time;
  uint64_t elapsed=clock_reset?0:frame_start-previous_time;previous_time=frame_start;
  if(resync_requested||clock_reset){stt_monitor_close(&monitor);resync_requested=0;accumulator=0;elapsed=0;previous=controls.buttons;pending_attack=0;pending_toggle=0;need_release=1;dropped++;}
  if(elapsed>100000)dropped++; /* Slow rendering is not a power/resume event. */
  unsigned pressed=controls.buttons&~previous;previous=controls.buttons;
  if(pressed&SCE_CTRL_SELECT)stt_monitor_toggle(&monitor,frame_start);
  if(pressed&SCE_CTRL_LTRIGGER)stt_render_set_ground(!stt_render_get_ground());
  if(pressed&SCE_CTRL_START){result=0;break;}
  if(need_release&&controls.buttons==0&&stt_axis(controls.lx)==0&&stt_axis(controls.ly)==0&&stt_axis(controls.rx)==0&&stt_axis(controls.ry)==0)need_release=0;
  if(pressed&SCE_CTRL_TRIANGLE){need_release=0;pressed&=~(SCE_CTRL_CROSS|SCE_CTRL_SQUARE);stt_combat_init(&combat);stt_equipment_init(&equipment);pending_toggle=0;camera=(SttCamera){.45f,.40f};accumulator=0;pending_attack=0;
   start=frame_start;seq=0;next_sample=0;memset(&mailbox,0,sizeof mailbox);snprintf(session,sizeof session,"vita-play-%" PRIx64,start);}
  if(!need_release&&(pressed&SCE_CTRL_CROSS))pending_attack=1;
  if(!need_release&&(pressed&SCE_CTRL_SQUARE))pending_toggle=1;
  unsigned ticks=stt_frame_ticks(elapsed,&accumulator);uint64_t update_start=sceKernelGetProcessTimeWide();
  for(unsigned i=0;i<ticks;i++){
   if(need_release)break;
   stt_camera_step(&camera,controls.rx,controls.ry);
   SttMove move=stt_camera_move(camera,controls.lx,controls.ly,combat.hunter.yaw_turn);
   SttCombatInput input={move.x_mm,move.z_mm,move.yaw_turn,pending_attack!=0};
   stt_equipment_step(&equipment,&combat,input,pending_toggle!=0);pending_attack=0;pending_toggle=0;
   /* A latest-only snapshot at 10 Hz and immediately on impact. No network operations. */
   if(combat.impact_count||combat.tick>=next_sample){
    SttPlaySample sample;stt_vita_snapshot(&sample,&combat,camera,session,seq++,(frame_start-start)/1000,frame_us,update_us,dropped);
    if(combat.hunter.state==STT_IDLE&&(move.x_mm||move.z_mm))sample.state=1;
    sample.battery_pct=scePowerGetBatteryLifePercent();stt_play_offer(&mailbox,&sample);next_sample=combat.tick+6;
   }
  }
  update_us=(unsigned)(sceKernelGetProcessTimeWide()-update_start);
  stt_render_monitor_status(monitor.active,monitor.sent,monitor.last_result);
  stt_render_visual_status(monitor.visual_frame,monitor.visual_errors);
  uint64_t render_start=sceKernelGetProcessTimeWide();
  stt_render_equipment(cached_pixels,depth,&combat,camera,frame_us,dropped,need_release,&original_asset,&equipped_sword,&equipment);
  render_us=(unsigned)(sceKernelGetProcessTimeWide()-render_start);
  uint64_t present_start=sceKernelGetProcessTimeWide();
  memcpy(buffers[front],cached_pixels,sizeof(uint32_t)*STT_PITCH*STT_HEIGHT);
  SceDisplayFrameBuf fb={sizeof fb,buffers[front],STT_PITCH,SCE_DISPLAY_PIXELFORMAT_A8B8G8R8,STT_WIDTH,STT_HEIGHT};
  result=sceDisplaySetFrameBuf(&fb,SCE_DISPLAY_SETBUF_NEXTFRAME);if(result<0)break;shown=1;
  result=sceDisplayWaitVblankStartCB();if(result<0)break;front^=1;
  present_us=(unsigned)(sceKernelGetProcessTimeWide()-present_start);
  uint64_t telemetry_start=sceKernelGetProcessTimeWide();
  stt_monitor_frame(&monitor,session,telemetry_start,combat.tick,(unsigned)equipment.mode,stt_render_get_ground(),update_us,render_us,present_us,telemetry_us);
  if(monitor.active){
  SttPlaySample visual_scene;
  stt_vita_snapshot(&visual_scene,&combat,camera,session,0,0,frame_us,update_us,dropped);
  if(combat.hunter.state==STT_IDLE&&(equipment.mode==STT_SHEATHED||equipment.mode==STT_DRAWN)&&
     (stt_axis(controls.lx)!=0||stt_axis(controls.ly)!=0)&&!need_release)visual_scene.state=1;
  visual_scene.battery_pct=scePowerGetBatteryLifePercent();
  stt_monitor_visual(&monitor,sceKernelGetProcessTimeWide(),cached_pixels,STT_PITCH,&visual_scene,(unsigned)equipment.mode,stt_render_get_ground(),&combat.target);
  }
  telemetry_us=(unsigned)(sceKernelGetProcessTimeWide()-telemetry_start);
  unsigned work_us=(unsigned)(sceKernelGetProcessTimeWide()-frame_start);
  if(work_us>33333)dropped++;
  else sceKernelDelayThreadCB(33333-work_us);
  frame_us=(unsigned)(sceKernelGetProcessTimeWide()-frame_start); /* 30 render FPS cap; simulation stays 60 Hz. */
 }
cleanup:
 stt_monitor_close(&monitor);
 if(result<0){
  fprintf(stderr,"STT Vita Prototype failed: 0x%08X\n",(unsigned)result);
  if(buffers[front]){
   stt_render_error(buffers[front],result);
   SceDisplayFrameBuf error_fb={sizeof error_fb,buffers[front],STT_PITCH,SCE_DISPLAY_PIXELFORMAT_A8B8G8R8,STT_WIDTH,STT_HEIGHT};
   if(sceDisplaySetFrameBuf(&error_fb,SCE_DISPLAY_SETBUF_NEXTFRAME)>=0){shown=1;sceDisplayWaitVblankStart();sceKernelDelayThread(3000000);}
  }
 }
 if(shown){sceDisplaySetFrameBuf(NULL,SCE_DISPLAY_SETBUF_NEXTFRAME);sceDisplayWaitVblankStart();}
 if(registered)scePowerUnregisterCallback(callback);
 if(callback>=0)sceKernelDeleteCallback(callback);
 free(cached_pixels);free(depth);for(int i=0;i<2;i++)if(memory[i]>=0)sceKernelFreeMemBlock(memory[i]);
 sceKernelExitProcess(result<0?1:0);return result<0?1:0;
}
