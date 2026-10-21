"""Generate original low-poly articulated practice dummy, not derived from game assets."""
import math
from pathlib import Path
from stt_asset_lab.model import export

def make_sample():
    bones = [dict(name='root',parent=-1,offset=[0,0,0]),
             dict(name='torso',parent=0,offset=[0,0.85,0]),
             dict(name='arm',parent=1,offset=[0.35,0.65,0]),
             dict(name='blade',parent=2,offset=[0.65,0,0])]
    vertices, triangles = [], []
    def box(bone, center, half):
        start = len(vertices)
        for x,y,z in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
            vertices.append(dict(position=[center[0]+x*half[0],center[1]+y*half[1],center[2]+z*half[2]],bone=bone))
        for a,b,c,d in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
            triangles.extend([[start+a,start+b,start+c],[start+a,start+c,start+d]])
    box(0,[-0.17,0.4,0],[0.12,0.4,0.12]); box(0,[0.17,0.4,0],[0.12,0.4,0.12])
    box(1,[0,0.4,0],[0.3,0.4,0.16]); box(1,[0,0.98,0],[0.18,0.18,0.18])
    box(2,[0.32,0,0],[0.32,0.09,0.09]); box(3,[0.55,0,0],[0.55,0.045,0.035])
    return dict(format='STT Asset',version=1,name='STT original practice dummy',bones=bones,vertices=vertices,triangles=triangles,
                clips=[dict(name='Idle',duration=2,tracks=[dict(bone=1,keys=[[0,0],[1,0.03],[2,0]])]),
                       dict(name='Practice swing',duration=1.2,tracks=[dict(bone=2,keys=[[0,0],[0.3,1.4],[0.55,-1.2],[1.2,0]])])])

if __name__ == '__main__':
    export(make_sample(),Path(__file__).parent/'samples'/'practice-dummy.stt.json')
