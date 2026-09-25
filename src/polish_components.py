import System,Rhino,scriptcontext as sc,json,os
import Grasshopper as GH,GH_IO
from System.Drawing import PointF
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for midi in [False,True]:
 d=sc.sticky['components_'+str(midi)];doc=d['doc'];GH.Instances.ActiveCanvas.Document=doc;doc.Enabled=True
 for o in doc.Objects:
  if hasattr(o,'Params'):
   for p in o.Params.Input:
    if p.NickName in ['seconds','articulation','arm_index','length'] or (o.GetType().Namespace=='Robots.Grasshopper' and p.Name in ['Tool','Motion','Display Geometry','Name']):p.WireDisplay=GH.Kernel.GH_ParamWireDisplay.faint
 d['time'].SetSliderValue(System.Decimal(.3));d['time'].ExpireSolution(False);doc.NewSolution(False)
 a=GH_IO.Serialization.GH_Archive();a.AppendObject(doc,'Definition');a.WriteToFile(doc.FilePath,True,False)
GH.Instances.ActiveCanvas.Document=sc.sticky['components_False']['doc']
sc.doc=Rhino.RhinoDoc.ActiveDoc
