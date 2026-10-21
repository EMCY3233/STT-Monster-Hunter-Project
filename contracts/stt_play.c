#include "stt_play.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <inttypes.h>
static const char *states[]={"idle","move","windup","active","recovery","stunned"};
int stt_play_encode(char *out,size_t cap,const SttPlaySample *s) {
 char hits[256]="", battery[8]; size_t n; unsigned i; int used=0,r;
 if(!out||!s||!s->session||cap==0) return -1;
 out[0]=0; for(n=0;n<65&&s->session[n];n++) {}
 if(n<1||n>64||s->state>5||s->hit_count>2||s->vita<0||s->vita>1||
 s->seq>9007199254740991ULL||s->tick>9007199254740991ULL||s->uptime_ms>9007199254740991ULL||
 s->battery_pct < -1||s->battery_pct>100||s->hp>1000000||
 s->yaw_mdeg < -180000||s->yaw_mdeg>180000||s->camera_yaw_mdeg < -180000||s->camera_yaw_mdeg>180000||
 s->camera_pitch_mdeg < -89000||s->camera_pitch_mdeg>89000||!s->camera_distance_mm||s->camera_distance_mm>1000000||
 s->phase_tick>65535||s->frame_us>10000000||s->update_us>10000000) return -1;
 for(i=0;i<n;i++) if(!((s->session[i]>='A'&&s->session[i]<='Z')||(s->session[i]>='a'&&s->session[i]<='z')||(s->session[i]>='0'&&s->session[i]<='9')||s->session[i]=='_'||s->session[i]=='-')) return -1;
 for(i=0;i<3;i++) if(s->pos_mm[i]<-100000000||s->pos_mm[i]>100000000) return -1;
 for(i=0;i<s->hit_count;i++) {
 const SttPlayHit *h=&s->hits[i];
 if(!h->attack||!h->target||h->damage>1000000||h->hp>1000000) return -1;
 if(i&&h->attack==s->hits[0].attack&&h->target==s->hits[0].target) return -1;
 r=snprintf(hits+used,sizeof(hits)-(size_t)used,"%s{\"attack\":%"PRIu32",\"target\":%"PRIu32",\"damage\":%"PRIu32",\"hp\":%"PRIu32"}",i?",":"",h->attack,h->target,h->damage,h->hp);
 if(r<0||(size_t)r>=sizeof(hits)-(size_t)used) return -1;
 used+=r;
 }
 if(s->battery_pct==-1) strcpy(battery,"null"); else snprintf(battery,sizeof(battery),"%d",s->battery_pct);
 r=snprintf(out,cap,"{\"version\":3,\"session\":\"%s\",\"source\":\"%s\",\"seq\":%"PRIu64",\"uptime_ms\":%"PRIu64",\"battery_pct\":%s,\"play\":{\"version\":1,\"tick\":%"PRIu64",\"origin\":\"original-prototype\",\"hunter\":{\"state\":\"%s\",\"pos_mm\":[%"PRId32",%"PRId32",%"PRId32"],\"yaw_mdeg\":%"PRId32",\"hp\":%"PRIu32"},\"camera\":{\"yaw_mdeg\":%"PRId32",\"pitch_mdeg\":%"PRId32",\"distance_mm\":%"PRIu32"},\"attack\":{\"id\":%"PRIu32",\"phase_tick\":%"PRIu32"},\"hits\":[%s],\"perf\":{\"frame_us\":%"PRIu32",\"update_us\":%"PRIu32",\"dropped\":%"PRIu32"},\"aquatic\":null}}",
 s->session,s->vita?"vita":"simulator",s->seq,s->uptime_ms,battery,s->tick,states[s->state],s->pos_mm[0],s->pos_mm[1],s->pos_mm[2],s->yaw_mdeg,s->hp,s->camera_yaw_mdeg,s->camera_pitch_mdeg,s->camera_distance_mm,s->attack_id,s->phase_tick,hits,s->frame_us,s->update_us,s->dropped);
 if(r<0||(size_t)r>=cap||r>STT_PLAY_MAX_BYTES){out[0]=0;return -1;} return r;
}
void stt_play_offer(SttPlayMailbox *m,const SttPlaySample *s) {
 if(!m||!s)return;
 if(m->ready&&m->dropped<UINT32_MAX)m->dropped++;
 m->latest=*s;m->latest.dropped=m->dropped;m->ready=1;
}
int stt_play_take(SttPlayMailbox *m,SttPlaySample *s) {
 if(!m||!s||!m->ready)return 0;
 *s=m->latest;m->ready=0;return 1;
}
