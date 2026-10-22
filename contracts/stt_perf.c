#include "stt_perf.h"
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
static const char *nullable(char out[24],int v){
 if(v<0)return "null";
 snprintf(out,24,"%d",v);return out;
}
int stt_perf_encode(char *out,size_t capacity,const SttPerfSample *s){
 if(!out||!capacity)return -1;
 out[0]=0;if(!s||!s->session||!s->frames||!s->window_us||s->equipment>3||s->ground_mode>1)return -1;
 size_t n=0;for(;n<65&&s->session[n];n++){
  char c=s->session[n];if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='-'||c=='_'))return -1;
 }
 if(!n||n>64||s->battery_pct>100||s->seq>9007199254740991ULL||s->tick>9007199254740991ULL||s->uptime_ms>9007199254740991ULL)return -1;
 char v[8][24];
 int size=snprintf(out,capacity,"{\"version\":4,\"session\":\"%s\",\"source\":\"vita\",\"seq\":%"PRIu64",\"uptime_ms\":%"PRIu64",\"battery_pct\":%s,\"perf\":{\"tick\":%"PRIu64",\"frames\":%u,\"window_us\":%u,\"update_us\":%u,\"render_us\":%u,\"present_us\":%u,\"telemetry_us\":%u,\"equipment\":%u,\"ground_mode\":%u,\"cpu_mhz\":%s,\"gpu_mhz\":%s,\"xbar_mhz\":%s,\"ram_free\":%s,\"cdram_free\":%s,\"phy_free\":%s,\"cdlg_free\":%s,\"cpu_load_pct\":null,\"gpu_load_pct\":null,\"fg_app\":null,\"vnz\":null,\"send_ok\":%u,\"send_errors\":%u}}",
 s->session,s->seq,s->uptime_ms,nullable(v[0],s->battery_pct),s->tick,s->frames,s->window_us,s->update_us,s->render_us,s->present_us,s->telemetry_us,s->equipment,s->ground_mode,
 nullable(v[1],s->cpu_mhz),nullable(v[2],s->gpu_mhz),nullable(v[3],s->xbar_mhz),nullable(v[4],s->ram_free),nullable(v[5],s->cdram_free),nullable(v[6],s->phy_free),nullable(v[7],s->cdlg_free),s->send_ok,s->send_errors);
 if(size<0||(size_t)size>=capacity||size>1024){out[0]=0;return -1;}return size;
}
