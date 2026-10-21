#include "snapshot.h"
#include <math.h>
#include <string.h>
void stt_vita_snapshot(SttPlaySample*s,const SttCombat*c,SttCamera cam,const char*session,uint64_t seq,uint64_t uptime_ms,unsigned frame_us,unsigned update_us,unsigned dropped){
 memset(s,0,sizeof *s);s->session=session;s->vita=1;s->seq=seq;s->uptime_ms=uptime_ms;s->tick=c->tick;s->battery_pct=-1;
 static const unsigned states[]={0,2,3,4};s->state=states[c->hunter.state];
 s->pos_mm[0]=c->hunter.x_mm;s->pos_mm[2]=c->hunter.z_mm;
 s->yaw_mdeg=(int32_t)((uint32_t)c->hunter.yaw_turn*360000ULL/65536);if(s->yaw_mdeg>180000)s->yaw_mdeg-=360000;
 s->camera_yaw_mdeg=(int32_t)lroundf(cam.yaw*57295.779513f);s->camera_pitch_mdeg=(int32_t)lroundf(cam.pitch*57295.779513f);
 s->hp=100;s->camera_distance_mm=6000;s->attack_id=c->hunter.attack_id;s->phase_tick=c->hunter.phase_tick;
 s->hit_count=c->impact_count;
 if(s->hit_count){s->hits[0]=(SttPlayHit){c->impacts[0].attack_id,c->impacts[0].target_id,(uint32_t)c->impacts[0].damage,(uint32_t)c->target.hp};}
 s->frame_us=frame_us;s->update_us=update_us;s->dropped=dropped;
}
