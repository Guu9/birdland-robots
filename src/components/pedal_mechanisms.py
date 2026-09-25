import math
from Rhino.Geometry import *
from System.Drawing import Color
meshes=[]
contacts=[0,0,float(kick_lift),float(hat_lift)]
# Pedal mechanisms are driven by the same contact heights as their arms.
def append_brep(b,color):
    for m in Mesh.CreateFromBrep(b,MeshingParameters.FastRenderMesh):
        m.VertexColors.CreateMonotoneMesh(color);meshes.append(m)
for x,y,lift in [(0,-460,contacts[2]),(550,-380,contacts[3])]:
    b=Box(Plane.WorldXY,Interval(x-46,x+46),Interval(y-100,y+100),Interval(50,68)).ToBrep()
    # Match the presser's center height while rotating about the rear hinge.
    angle=math.atan2(lift,100.0)
    b.Transform(Transform.Rotation(angle,Vector3d.XAxis,Point3d(x,y-100,59)))
    append_brep(b,Color.FromArgb(175,190,199))
# Kick linkage: the beater swings toward the drum as the pedal descends.
end=Point3d(0,-230-contacts[2]*2.1,285)
start=Point3d(0,-350,55);direction=end-start
append_brep(Cylinder(Circle(Plane(start,direction),9),direction.Length).ToBrep(True,True),Color.FromArgb(180,195,205))
append_brep(Sphere(end,32).ToBrep(),Color.FromArgb(224,219,200))
# Hi-hat top plate opens 0..14 mm as its pedal arm releases.
z=957+contacts[3]*.5
profile=PolylineCurve([Point3d(550+r,-50,z+h) for r,h in [(0,27),(35,30),(62,11),(180,0),(180,-3),(62,6),(35,24),(0,22)]])
append_brep(RevSurface.Create(profile,Line(Point3d(550,-50,z-50),Point3d(550,-50,z+60)),0,2*math.pi).ToBrep(),Color.FromArgb(185,131,48))
