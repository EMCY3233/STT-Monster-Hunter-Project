#include "visibility.h"
#include <assert.h>
#include <stdio.h>
int main(void){const float m[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};const float inside[6]={-.5f,-.5f,-.5f,.5f,.5f,.5f},outside[6]={2,0,0,3,1,1},crossing[6]={-2,-2,-2,2,2,2};assert(stt_bounds_visible(m,inside));assert(!stt_bounds_visible(m,outside));assert(stt_bounds_visible(m,crossing));puts("PASS conservative bounds visibility");return 0;}
