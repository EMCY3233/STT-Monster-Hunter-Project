#include "stt_pose.h"
#include <math.h>
#include <string.h>

typedef struct { const unsigned char *s; size_t n, p; } Reader;
static void ws(Reader *r) {
    while (r->p < r->n && (r->s[r->p]==' ' || r->s[r->p]=='\n' || r->s[r->p]=='\r' || r->s[r->p]=='\t')) ++r->p;
}
static int take(Reader *r, unsigned char c) {
    ws(r);
    if (r->p == r->n || r->s[r->p] != c) return 0;
    ++r->p; return 1;
}
/* Canonical exporter profile: plain ASCII strings, no escapes. */
static int string(Reader *r, char out[65]) {
    size_t count=0;
    if (!take(r,'"')) return 0;
    while (r->p < r->n && r->s[r->p]!='"') {
        unsigned char c=r->s[r->p++];
        if (c<32 || c>126 || c=='\\' || count==64) return 0;
        out[count++]=(char)c;
    }
    out[count]=0;
    return count>0 && take(r,'"');
}
static int literal(Reader *r, const char *value) {
    char s[65]; return string(r,s) && strcmp(s,value)==0;
}
static int key(Reader *r, const char *value) { return literal(r,value) && take(r,':'); }
static int integer(Reader *r, int32_t lo, int32_t hi, int32_t *out) {
    uint32_t value=0; int negative=0;
    size_t start;
    ws(r);
    if (r->p<r->n && r->s[r->p]=='-') { negative=1; ++r->p; }
    start=r->p;
    while (r->p<r->n && r->s[r->p]>='0' && r->s[r->p]<='9') {
        uint32_t digit=(uint32_t)(r->s[r->p]-'0');
        if (value>(1000000u-digit)/10u) return 0;
        value=value*10u+digit; ++r->p;
    }
    if (r->p==start || (r->p-start>1 && r->s[start]=='0')) return 0;
    *out=negative ? -(int32_t)value : (int32_t)value;
    return *out>=lo && *out<=hi;
}
static int point(Reader *r, int32_t out[3]) {
    if (!take(r,'[')) return 0;
    for (unsigned j=0;j<3;++j) {
        if (j && !take(r,',')) return 0;
        if (!integer(r,-1000000,1000000,&out[j])) return 0;
    }
    return take(r,']');
}
static int points(Reader *r, int32_t (*out)[3], unsigned cap, unsigned *count) {
    unsigned n=0; int32_t p[3];
    if (!take(r,'[')) return 0;
    do {
        if (n==cap || !point(r,p)) return 0;
        if (out) memcpy(out[n],p,sizeof p);
        ++n; ws(r);
        if (r->p==r->n) return 0;
        if (r->s[r->p]!=',') break;
        ++r->p;
    } while (1);
    *count=n;
    return take(r,']');
}
static int frame(Reader *r, SttPoseFrame *out, unsigned bones, unsigned *vertices) {
    unsigned nb=0,nv=0;
    if (!take(r,'{') || !key(r,"joints") ||
        !points(r,out?out->joints:NULL,STT_POSE_BONES,&nb) || nb!=bones ||
        !take(r,',') || !key(r,"vertices") ||
        !points(r,out?out->vertices:NULL,STT_POSE_VERTICES,&nv) ||
        (*vertices && nv!=*vertices) || !take(r,'}')) return 0;
    *vertices=nv; return 1;
}
static int parse(Reader *r, SttPose *out) {
    int32_t v; unsigned n=0, vertices=0;
    char names[8][65];
    if (!take(r,'{') || !key(r,"format") || !literal(r,"STT Pose") ||
        !take(r,',') || !key(r,"version") || !integer(r,1,1,&v) ||
        !take(r,',') || !key(r,"hz") || !integer(r,60,60,&v) ||
        !take(r,',') || !key(r,"basis") || !literal(r,"RH_Xright_Yup_Zforward_mm") ||
        !take(r,',') || !key(r,"parents") || !take(r,'[')) return 0;
    do {
        if (n==STT_POSE_BONES || !integer(r,n?0:-1,(int32_t)n-1,&v)) return 0;
        out->parents[n++]=(int16_t)v;
        ws(r); if (r->p==r->n) return 0;
        if (r->s[r->p]!=',') break;
        ++r->p;
    } while (1);
    out->bones=(uint16_t)n;
    if (!take(r,']') || !take(r,',') || !key(r,"triangles") || !take(r,'[')) return 0;
    n=0;
    do {
        if (n==STT_POSE_TRIANGLES || !take(r,'[')) return 0;
        for (unsigned j=0;j<3;++j) {
            if ((j && !take(r,',')) || !integer(r,0,STT_POSE_VERTICES-1,&v)) return 0;
            out->triangles[n][j]=(uint16_t)v;
        }
        if (out->triangles[n][0]==out->triangles[n][1] || out->triangles[n][0]==out->triangles[n][2] ||
            out->triangles[n][1]==out->triangles[n][2] || !take(r,']')) return 0;
        ++n; ws(r); if (r->p==r->n) return 0;
        if (r->s[r->p]!=',') break;
        ++r->p;
    } while (1);
    out->triangle_count=(uint16_t)n;
    if (!take(r,']') || !take(r,',') || !key(r,"clips") || !take(r,'[')) return 0;
    n=0;
    do {
        if (n==8 || !take(r,'{') || !key(r,"name") || !string(r,names[n])) return 0;
        for (unsigned i=0;i<n;++i) if (!strcmp(names[i],names[n])) return 0;
        if (!take(r,',') || !key(r,"frames") || !take(r,'[')) return 0;
        out->clip_start[n]=out->frames;
        do {
            ws(r);
            if (out->frames==STT_POSE_FRAMES || r->p>=r->n) return 0;
            out->frame_offset[out->frames]=(uint32_t)r->p;
            if (!frame(r,NULL,out->bones,&vertices)) return 0;
            ++out->frames; ++out->clip_frames[n];
            ws(r); if (r->p==r->n) return 0;
            if (r->s[r->p]!=',') break;
            ++r->p;
        } while (1);
        if (!take(r,']') || !take(r,'}')) return 0;
        ++n; ws(r); if (r->p==r->n) return 0;
        if (r->s[r->p]!=',') break;
        ++r->p;
    } while (1);
    out->clips=(uint16_t)n; out->vertices=(uint16_t)vertices;
    for (unsigned i=0;i<out->triangle_count;++i)
        for (unsigned j=0;j<3;++j) if (out->triangles[i][j]>=vertices) return 0;
    if (!take(r,']') || !take(r,'}')) return 0;
    ws(r); return r->p==r->n;
}
int stt_pose_open(SttPose *out, const void *json, size_t bytes) {
    Reader r={(const unsigned char*)json,bytes,0};
    if (!out) return 0;
    memset(out,0,sizeof *out);
    if (!json || bytes==0 || bytes>STT_POSE_BYTES || !parse(&r,out)) {
        memset(out,0,sizeof *out); return 0;
    }
    out->json=(const unsigned char*)json; out->bytes=bytes; return 1;
}
int stt_pose_frame(const SttPose *pose, unsigned clip, uint64_t tick, SttPoseFrame *out) {
    unsigned vertices; size_t index; Reader r;
    if (!out) return 0;
    memset(out,0,sizeof *out);
    if (!pose || !pose->json || pose->bytes>STT_POSE_BYTES || pose->bytes==0 ||
        clip>=pose->clips || clip>=8 || !pose->clip_frames[clip] ||
        pose->bones==0 || pose->bones>STT_POSE_BONES ||
        pose->vertices==0 || pose->vertices>STT_POSE_VERTICES) return 0;
    index=(size_t)pose->clip_start[clip]+(size_t)(tick%pose->clip_frames[clip]);
    if (index>=STT_POSE_FRAMES || index>=pose->frames || pose->frame_offset[index]>=pose->bytes) return 0;
    r=(Reader){pose->json,pose->bytes,pose->frame_offset[index]}; vertices=pose->vertices;
    if (!frame(&r,out,pose->bones,&vertices)) { memset(out,0,sizeof *out); return 0; }
    return 1;
}
int stt_pose_transform(const int32_t p[3], int32_t x, int32_t z, uint16_t yaw, float out[3]) {
    if (!p || !out) return 0;
    for (unsigned j=0;j<3;++j) if (p[j]<-1000000 || p[j]>1000000) return 0;
    if (x<-1000000 || x>1000000 || z<-1000000 || z>1000000) return 0;
    float angle=(float)yaw*(6.283185307179586f/65536.0f), s=sinf(angle), c=cosf(angle);
    out[0]=((float)x+(float)p[0]*c+(float)p[2]*s)*.001f;
    out[1]=(float)p[1]*.001f;
    out[2]=((float)z+(float)p[2]*c-(float)p[0]*s)*.001f;
    return 1;
}
