"""Pure orthographic viewer projection, shared by mesh and bone overlays."""
import math

def project(point, yaw, zoom, width, height):
    c, s = math.cos(yaw), math.sin(yaw)
    x, z = c*point[0]+s*point[2], -s*point[0]+c*point[2]
    cp, sp = math.cos(math.radians(20)), math.sin(math.radians(20))
    y = point[1]*cp-z*sp
    depth = point[1]*sp+z*cp
    return width/2+x*zoom, height*0.74-y*zoom, depth
