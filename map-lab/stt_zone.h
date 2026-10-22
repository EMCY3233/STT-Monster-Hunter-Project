#ifndef STT_ZONE_H
#define STT_ZONE_H
#include <stdint.h>
typedef int (*SttZoneTriangle)(void *,const float [3][3],uint32_t);
int stt_zone_load(const char *path);
void stt_zone_close(void);
int stt_zone_active(void);
void stt_zone_reset(void);
void stt_zone_move(float dx,float dz);
void stt_zone_position(float out[3]);
float stt_zone_yaw(void);
float stt_zone_slope(void);
unsigned stt_zone_contact(void);
unsigned stt_zone_emit(int hunter,SttZoneTriangle callback,void *context);
#endif
