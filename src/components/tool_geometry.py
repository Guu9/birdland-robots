from Rhino.Geometry import *
length=float(length);radius=7 if length>150 else 20
mesh=Mesh.CreateFromCylinder(Cylinder(Circle(Plane.WorldXY,radius),length),1,16)
mesh.Append(Mesh.CreateFromSphere(Sphere(Point3d(0,0,length),8 if length>150 else 24),12,8))
tcp=Plane(Point3d(0,0,length),Vector3d.ZAxis)
