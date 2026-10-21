#include "stt_play.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 SttPlaySample s={0},t;SttPlayMailbox m={0};char out[1025];
 s.session="synthetic";s.battery_pct=-1;s.camera_distance_mm=4000;s.hp=100;
 assert(stt_play_encode(out,sizeof(out),&s)>0);puts(out);
 s.state=3;s.tick=18;s.attack_id=1;s.hit_count=1;s.hits[0]=(SttPlayHit){1,1,25,75};
 assert(stt_play_encode(out,sizeof(out),&s)>0);puts(out);
 stt_play_offer(&m,&s);stt_play_offer(&m,&s);assert(stt_play_take(&m,&t)&&t.dropped==1);assert(!stt_play_take(&m,&t));
 assert(stt_play_encode(out,5,&s)==-1&&out[0]==0);
 s.hit_count=3;assert(stt_play_encode(out,sizeof(out),&s)==-1);s.hit_count=1;
 s.session="bad\"";assert(stt_play_encode(out,sizeof(out),&s)==-1);s.session="synthetic";
 s.hit_count=2;s.hits[1]=s.hits[0];assert(stt_play_encode(out,sizeof(out),&s)==-1);
 s.hit_count=1;s.camera_pitch_mdeg=89001;assert(stt_play_encode(out,sizeof(out),&s)==-1);
 return 0;
}
