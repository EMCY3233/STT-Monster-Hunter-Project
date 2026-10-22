#ifndef STT_CONTROL_H
#define STT_CONTROL_H
#include <stdint.h>
typedef struct { float yaw, pitch; } SttCamera;
#define STT_CAMERA_MIN_PITCH (-0.45f)
#define STT_CAMERA_MAX_PITCH 1.05f
#define STT_CAMERA_MIN_HEIGHT 0.35f
#define STT_CAMERA_MIN_BOOM 2.75f
typedef struct {float eye[3],right[3],forward[3],up[3];} SttCameraView;
/* Six-metre orbit, floor clearance and horizontal exclusion around the hunter.
   Looking up can move the hunter down the screen as the eye stops at the floor. */
int stt_camera_view(SttCamera camera,int32_t x_mm,int32_t z_mm,SttCameraView *view);
typedef struct { int x_mm,z_mm; uint16_t yaw_turn; } SttMove;
float stt_axis(unsigned char value);
/* Only game buttons: exclude headphone, volume, power/intercept status bits. */
unsigned stt_game_buttons(unsigned raw);
void stt_camera_step(SttCamera *camera, unsigned char rx, unsigned char ry);
SttMove stt_camera_move(SttCamera camera, unsigned char lx, unsigned char ly, uint16_t previous);
/* Microseconds. Clamp slow frames; at most 4 ticks. Real resume resets externally. */
unsigned stt_frame_ticks(uint64_t elapsed_us, uint64_t *accumulator_us);
#endif
