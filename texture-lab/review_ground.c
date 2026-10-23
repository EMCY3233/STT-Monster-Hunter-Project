#include "../map-lab/stt_zone.h"
#include <stdio.h>
#include <math.h>
int main(int argc,char **argv){if(argc!=2||!stt_zone_load(argv[1])){puts("FAIL ground stream");return 1;}float p[3];unsigned blocked=0;for(unsigned i=0;i<560;i++){stt_zone_move(0,.05f);blocked+=stt_zone_contact()!=0;}stt_zone_position(p);printf("PASS native ground position %.5f %.5f %.5f blocked=%u\n",p[0],p[1],p[2],blocked);int bad=!isfinite(p[0])||!isfinite(p[1])||!isfinite(p[2]);stt_zone_close();return bad;}
