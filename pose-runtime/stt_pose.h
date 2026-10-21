#ifndef STT_POSE_H
#define STT_POSE_H
#include <stddef.h>
#include <stdint.h>
#define STT_POSE_BYTES 2097152u
#define STT_POSE_FRAMES 600u
#define STT_POSE_VERTICES 256u
#define STT_POSE_BONES 32u
#define STT_POSE_TRIANGLES 512u
/* Borrowed immutable JSON. Do not mutate input or this index after open succeeds. */
typedef struct {
    const unsigned char *json;
    size_t bytes;
    uint32_t frame_offset[STT_POSE_FRAMES];
    uint16_t clip_start[8], clip_frames[8];
    int16_t parents[STT_POSE_BONES];
    uint16_t triangles[STT_POSE_TRIANGLES][3];
    uint16_t bones, vertices, triangle_count, frames, clips;
} SttPose;
typedef struct {
    int32_t joints[STT_POSE_BONES][3];
    int32_t vertices[STT_POSE_VERTICES][3];
} SttPoseFrame;
/* Returns 1 on success; 0 clears output. No allocation, no file I/O. */
int stt_pose_open(SttPose *out, const void *json, size_t bytes);
/* Nonnegative simulation tick wraps. Output is cleared on failure. */
int stt_pose_frame(const SttPose *pose, unsigned clip, uint64_t tick, SttPoseFrame *out);
/* Same handedness and yaw as PR11: yaw 0 faces +Z. No combat/hitbox binding. */
int stt_pose_transform(const int32_t model_mm[3], int32_t x_mm, int32_t z_mm,
                       uint16_t yaw_turn, float world_m[3]);
typedef int (*SttPoseTriangleSink)(void *context, const float triangle_m[3][3]);
/* Adapter seam for renderer tri(): reuses caller's one-frame scratch buffer.
   Sink must consume/copy each triangle immediately. Failure may emit a prefix. */
int stt_pose_emit(const SttPose *pose, unsigned clip, uint64_t tick,
                  int32_t x_mm, int32_t z_mm, uint16_t yaw_turn,
                  SttPoseFrame *scratch, SttPoseTriangleSink sink, void *context);
#endif
