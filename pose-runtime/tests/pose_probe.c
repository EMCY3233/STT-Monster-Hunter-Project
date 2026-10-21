#include "stt_pose.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct { unsigned count; double sum[3]; } Mesh;
static int sink(void *context, const float triangle[3][3]) {
    Mesh *mesh=context;
    for (unsigned i=0;i<3;++i) for (unsigned j=0;j<3;++j) {
        assert(isfinite(triangle[i][j]));
        mesh->sum[j]+=triangle[i][j];
    }
    ++mesh->count; return 1;
}
static int cancel(void *context, const float triangle[3][3]) {
    (void)context; (void)triangle; return 0;
}

int main(int argc, char **argv) {
    static SttPose pose;
    static SttPoseFrame result, first;
    float world[3]; int32_t anchor[3]={1000,2000,3000};
    assert(stt_pose_transform(anchor,4000,5000,0,world));
    assert(world[0]>4.999f && world[0]<5.001f && world[1]>1.999f && world[1]<2.001f && world[2]>7.999f && world[2]<8.001f);
    assert(stt_pose_transform(anchor,4000,5000,16384,world));
    assert(world[0]>6.999f && world[0]<7.001f && world[2]>3.999f && world[2]<4.001f);
    assert(!stt_pose_transform(anchor,INT_MAX,0,0,world));
    assert(!stt_pose_open(&pose,NULL,0));
    assert(!stt_pose_open(NULL,"x",1));
    if (argc!=2) return 3;
    FILE *file=fopen(argv[1],"rb");
    if (!file) return 3;
    if (fseek(file,0,SEEK_END)!=0) { fclose(file); return 3; }
    long length=ftell(file);
    if (length<=0 || length>(long)STT_POSE_BYTES || fseek(file,0,SEEK_SET)!=0) { fclose(file); return 2; }
    unsigned char *raw=malloc((size_t)length);
    if (!raw) { fclose(file); return 3; }
    if (fread(raw,1,(size_t)length,file)!=(size_t)length) { fclose(file); free(raw); return 3; }
    fclose(file);
    if (!stt_pose_open(&pose,raw,(size_t)length)) {
        assert(!pose.json && !pose.frames && !pose.bytes);
        free(raw); return 2;
    }
    printf("%zu %zu %u %u %u %u %u\n",sizeof pose,sizeof result,(unsigned)pose.bones,(unsigned)pose.vertices,
           (unsigned)pose.triangle_count,(unsigned)pose.clips,(unsigned)pose.frames);
    assert(!stt_pose_frame(&pose,8,0,&result));
    for (unsigned c=0;c<pose.clips;++c) {
        assert(stt_pose_frame(&pose,c,0,&first));
        assert(stt_pose_frame(&pose,c,pose.clip_frames[c],&result));
        assert(!memcmp(&first,&result,sizeof first));
        assert(stt_pose_frame(&pose,c,UINT64_MAX,&result));
        for (unsigned t=0;t<pose.clip_frames[c];++t) {
            assert(stt_pose_frame(&pose,c,t,&result));
            for (unsigned i=0;i<pose.bones;++i) for (unsigned j=0;j<3;++j) printf("%d ",(int)result.joints[i][j]);
            for (unsigned i=0;i<pose.vertices;++i) for (unsigned j=0;j<3;++j) printf("%d ",(int)result.vertices[i][j]);
            puts("");
        }
    }
    for (unsigned c=0;c<pose.clips;++c) {
        Mesh mesh={0,{0,0,0}};
        assert(stt_pose_emit(&pose,c,0,4000,5000,16384,&result,sink,&mesh));
        assert(mesh.count==pose.triangle_count);
        printf("mesh %u %u %.9f %.9f %.9f\n",c,mesh.count,mesh.sum[0],mesh.sum[1],mesh.sum[2]);
    }
    assert(!stt_pose_emit(&pose,0,0,0,0,0,&result,cancel,NULL));
    assert(!stt_pose_emit(&pose,0,0,0,0,0,&result,NULL,NULL));
    assert(!stt_pose_emit(&pose,0,0,INT_MAX,0,0,&result,sink,NULL));
    /* Validate offset guards even for accidentally damaged public index. */
    pose.frame_offset[0]=UINT32_MAX;
    assert(!stt_pose_frame(&pose,0,0,&result));
    pose.frame_offset[0]=0; pose.clip_start[0]=UINT16_MAX;
    assert(!stt_pose_frame(&pose,0,0,&result));
    free(raw); return 0;
}
