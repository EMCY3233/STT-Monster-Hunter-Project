#ifndef STT_CONTROL_H
#define STT_CONTROL_H
#include <stdint.h>
typedef struct { float yaw, pitch; } SttCamera;
typedef struct { int x_mm,z_mm; uint16_t yaw_turn; } SttMove;
float stt_axis(unsigned char value);
/* Only game buttons: exclude headphone, volume, power/intercept status bits. */
unsigned stt_game_buttons(unsigned raw);
void stt_camera_step(SttCamera *camera, unsigned char rx, unsigned char ry);
SttMove stt_camera_move(SttCamera camera, unsigned char lx, unsigned char ly, uint16_t previous);
/* Microseconds. Clamp slow frames; at most 4 ticks. Real resume resets externally. */
unsigned stt_frame_ticks(uint64_t elapsed_us, uint64_t *accumulator_us);
#endif
