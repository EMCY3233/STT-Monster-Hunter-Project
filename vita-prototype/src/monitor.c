#include "monitor.h"
#include <psp2/net/net.h>
#include <psp2/sysmodule.h>
#include <psp2/power.h>
#include <psp2/kernel/sysmem.h>
#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
void stt_monitor_init(SttPrototypeMonitor *m){memset(m,0,sizeof *m);m->socket=-1;}
void stt_monitor_close(SttPrototypeMonitor *m){
 if(m->socket>=0)sceNetSocketClose(m->socket);
 if(m->network)sceNetTerm();
 free(m->visual);m->visual=NULL;
 free(m->memory);
 if(m->module)sceSysmoduleUnloadModule(SCE_SYSMODULE_NET);
 m->socket=-1;m->memory=NULL;m->network=m->module=m->active=0;
}
void stt_monitor_toggle(SttPrototypeMonitor *m,uint64_t now){
 if(m->active){stt_monitor_close(m);return;}
 stt_monitor_close(m);m->last_result=-1;
 char ip[64],extra;unsigned a,b,c,d;FILE *f=fopen("ux0:/data/STTP00001/monitor-ip.txt","rb");
 if(!f)return;
 char *read=fgets(ip,sizeof ip,f);fclose(f);if(!read)return;
 ip[strcspn(ip,"\r\n")]=0;
 if(sscanf(ip,"%u.%u.%u.%u%c",&a,&b,&c,&d,&extra)!=4||a>255||b>255||c>255||d<1||d>254||
    !(a==10||(a==172&&b>=16&&b<=31)||(a==192&&b==168)))return;
 m->last_result=sceSysmoduleLoadModule(SCE_SYSMODULE_NET);if(m->last_result<0)return;m->module=1;
 m->memory=malloc(1024*1024);if(!m->memory){m->last_result=-2;goto fail;}
 SceNetInitParam init={m->memory,1024*1024,0};
 m->last_result=sceNetInit(&init);if(m->last_result<0)goto fail;m->network=1;
 m->socket=sceNetSocket("stt-prototype-perf",SCE_NET_AF_INET,SCE_NET_SOCK_DGRAM,0);
 if(m->socket<0){m->last_result=m->socket;goto fail;}
 int enabled=1;m->last_result=sceNetSetsockopt(m->socket,SCE_NET_SOL_SOCKET,SCE_NET_SO_NBIO,&enabled,sizeof enabled);
 if(m->last_result<0)goto fail;
 SceNetSockaddrIn address;memset(&address,0,sizeof address);
 address.sin_len=sizeof address;address.sin_family=SCE_NET_AF_INET;address.sin_port=sceNetHtons(32100);
 m->last_result=sceNetInetPton(SCE_NET_AF_INET,ip,&address.sin_addr);if(m->last_result!=1)goto fail;
 if(sizeof address>sizeof m->address){m->last_result=-3;goto fail;}
 memcpy(m->address,&address,sizeof address);
 snprintf(m->session,sizeof m->session,"vita-perf-%"PRIx64,now);
 m->started=m->window_start=now;m->next=now+1000000;m->seq=0;m->sent=m->errors=m->frames=0;
 m->update_sum=m->render_sum=m->present_sum=m->telemetry_sum=0;m->last_ground=2;m->active=1;
 m->visual=calloc(1,sizeof *m->visual);m->visual_next=now;m->visual_errors=m->visual_frame=0;
 if(!m->visual){m->last_result=-5;goto fail;}return;
fail:
 stt_monitor_close(m);
}
void stt_monitor_frame(SttPrototypeMonitor *m,const char *session,uint64_t now,uint64_t tick,
 unsigned equipment,unsigned ground_mode,unsigned update_us,unsigned render_us,unsigned present_us,unsigned telemetry_us){
 (void)session;
 if(!m->active)return;
 if(now<m->started||now-m->started>=180000000ULL){stt_monitor_close(m);return;}
 if(m->last_ground!=ground_mode){m->last_ground=ground_mode;m->window_start=now;m->next=now+1000000;m->frames=0;m->update_sum=m->render_sum=m->present_sum=m->telemetry_sum=0;return;}
 m->frames++;m->update_sum+=update_us;m->render_sum+=render_us;m->present_sum+=present_us;m->telemetry_sum+=telemetry_us;
 if(now<m->next)return;
 SttPerfSample s;memset(&s,0,sizeof s);s.session=m->session;s.seq=m->seq++;s.uptime_ms=(now-m->started)/1000;s.tick=tick;
 s.frames=m->frames;s.window_us=(unsigned)(now-m->window_start);s.equipment=equipment;s.ground_mode=ground_mode;
 s.update_us=(unsigned)(m->update_sum/m->frames);s.render_us=(unsigned)(m->render_sum/m->frames);
 s.present_us=(unsigned)(m->present_sum/m->frames);s.telemetry_us=(unsigned)(m->telemetry_sum/m->frames);
 s.cpu_mhz=scePowerGetArmClockFrequency();s.gpu_mhz=scePowerGetGpuClockFrequency();s.xbar_mhz=scePowerGetGpuXbarClockFrequency();
 s.battery_pct=scePowerGetBatteryLifePercent();s.ram_free=s.cdram_free=s.phy_free=s.cdlg_free=-1;
 SceKernelFreeMemorySizeInfo free_mem;memset(&free_mem,0,sizeof free_mem);free_mem.size=sizeof free_mem;
 if(sceKernelGetFreeMemorySize(&free_mem)>=0){s.ram_free=free_mem.size_user;s.cdram_free=free_mem.size_cdram;s.phy_free=free_mem.size_phycont;}
 /* Pinned SDK lacks the CDLG subbudget API; keep explicit unavailable. */
 s.send_ok=m->sent;s.send_errors=m->errors;
 char payload[1025];int bytes=stt_perf_encode(payload,sizeof payload,&s);
 SceNetSockaddrIn destination;memcpy(&destination,m->address,sizeof destination);
 m->last_result=bytes<0?-4:sceNetSendto(m->socket,payload,bytes,SCE_NET_MSG_DONTWAIT,(SceNetSockaddr*)&destination,sizeof destination);
 if(m->last_result==bytes&&bytes>0)m->sent++;else m->errors++;
 m->window_start=now;m->next=now+1000000;m->frames=0;m->update_sum=m->render_sum=m->present_sum=m->telemetry_sum=0;
 if(m->errors>=5)stt_monitor_close(m);
}

void stt_monitor_visual(SttPrototypeMonitor *m,uint64_t now,const uint32_t *pixels,size_t pitch,
 SttPlaySample *scene,unsigned equipment,unsigned ground,const SttTarget *target){
 if(!m->active||!m->visual||m->visual_errors>=5)return;
 if(now<m->started||now-m->started>=180000000ULL){stt_monitor_close(m);return;}
 SttVisual *v=m->visual;
 if(v->offset==v->total&&now>=m->visual_next){
  scene->session=m->session;scene->seq=m->visual_frame;scene->uptime_ms=(now-m->started)/1000;
  if(stt_visual_capture(v,pixels,pitch,scene,m->started,m->visual_frame++,equipment,ground,target)<0){m->visual_errors++;return;}
  m->visual_next=now+2000000;
 }
 SceNetSockaddrIn destination;memcpy(&destination,m->address,sizeof destination);destination.sin_port=sceNetHtons(32101);
 for(unsigned i=0;i<4;i++){
  uint8_t payload[STT_VISUAL_HEADER+STT_VISUAL_CHUNK];int bytes=stt_visual_next(v,payload,sizeof payload);
  if(bytes==0)break;
  int sent=bytes<0?-1:sceNetSendto(m->socket,payload,bytes,SCE_NET_MSG_DONTWAIT,(SceNetSockaddr*)&destination,sizeof destination);
  if(bytes<0||sent!=bytes){m->visual_errors++;v->offset=v->total;break;}
 }
}
