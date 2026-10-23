#ifndef STT_VISIBILITY_H
#define STT_VISIBILITY_H
/* Column-major clip matrix, conservative eight-corner plane rejection. */
static int stt_bounds_visible(const float m[16],const float b[6]){
 unsigned outside[6]={0};
 for(unsigned i=0;i<8;i++){
  float x=b[(i&1)?3:0],y=b[(i&2)?4:1],z=b[(i&4)?5:2];
  float q[4];for(unsigned k=0;k<4;k++)q[k]=m[k]*x+m[4+k]*y+m[8+k]*z+m[12+k];
  outside[0]+=q[0]<-q[3];outside[1]+=q[0]>q[3];outside[2]+=q[1]<-q[3];outside[3]+=q[1]>q[3];outside[4]+=q[2]<-q[3];outside[5]+=q[2]>q[3];
 }
 for(unsigned i=0;i<6;i++)if(outside[i]==8)return 0;
 return 1;
}
#endif
