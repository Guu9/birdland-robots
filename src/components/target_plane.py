import math,json
from Rhino.Geometry import Point3d,Vector3d,Plane
state=json.loads(str(articulation));index=int(arm_index)
rim=state['rim'];crash=state['crash']
points=[Point3d(-350,-100+180*rim,668),Point3d(660+160*crash,-50+380*crash,968+115*crash+state['opening']),Point3d(0,-460,92),Point3d(550,-380,92)]
contact=points[index]
if index<2:
 angle=.72+(.76*rim if index==0 else 0)
 swing=((.36-.29*rim) if index==0 else .24)*float(rebound)*state['strengths'][index]
 direction=Vector3d(0,math.sin(angle+swing),-math.cos(angle+swing))
 wrist=contact-Vector3d(0,math.sin(angle),-math.cos(angle))*float(length)
 plane=Plane(wrist+direction*float(length),Vector3d.XAxis,Vector3d.CrossProduct(direction,Vector3d.XAxis))
else:plane=Plane(contact+Vector3d(0,0,float(lift)),Vector3d.XAxis,-Vector3d.YAxis)
