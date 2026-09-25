# Run with Rhino's RunPythonScript. Keeps the legacy GH definitions intact.
import clr,System,Rhino,scriptcontext as sc,json,traceback,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
for a in System.AppDomain.CurrentDomain.GetAssemblies():
 if a.GetName().Name in ['RhinoCodePluginGH','GhPython']:clr.AddReference(a)
import Grasshopper as GH,GH_IO
from RhinoCodePluginGH.Components import Python3Component
from RhinoCodePluginGH.Parameters import ScriptVariableParam
rhdoc=Rhino.RhinoDoc.ActiveDoc

def migrate(label):
 ar=GH_IO.Serialization.GH_Archive();ar.ReadFromFile(ROOT+'/grasshopper/'+label+'-Components.gh')
 doc=GH.Kernel.GH_Document();ar.ExtractObject(doc,'Definition')
 doc.GetType().GetMethod('SetDocumentID',System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic).Invoke(doc,System.Array[System.Object]([System.Guid.NewGuid()]))
 doc.FilePath=ROOT+'/grasshopper/'+label+'-Python3.gh'
 replacements={};sources={};newnodes=[];oldnodes=[]
 for o in list(doc.Objects):
  if str(o.GetType())!='GhPython.Component.ZuiPythonComponent':continue
  oldnodes.append(o)
  code=o.Code.replace('from Rhino.Geometry import *','from Rhino.Geometry import Mesh, Cylinder, Circle, Plane, Sphere, Point3d, Vector3d, Box, Interval, Transform, MeshingParameters, PolylineCurve, RevSurface, Line')
  new=Python3Component.Create(o.NickName,code)
  new.MarshInputs=True;new.MarshOutputs=True;new.MarshGuids=False
  new.UsingStandardOutputParam=False
  for p in list(new.Params.Input):new.Params.UnregisterInputParameter(p,True)
  for p in list(new.Params.Output):new.Params.UnregisterOutputParameter(p,True)
  for side,params in [('Input',o.Params.Input),('Output',o.Params.Output)]:
   for p in params:
    q=ScriptVariableParam(p.NickName);q.PrettyName=p.Name;q.ToolTip=p.Description;q.Optional=p.Optional;q.Access=p.Access;q.WireDisplay=p.WireDisplay;q.AllowTreeAccess=True;q.CreateAttributes()
    if side=='Input':new.Params.RegisterInputParam(q);sources[q]=list(p.Sources)
    else:new.Params.RegisterOutputParam(q);replacements[p]=q
  new.VariableParameterMaintenance();new.Params.OnParametersChanged()
  new.CreateAttributes();new.Attributes.Pivot=o.Attributes.Pivot;new.Name=o.Name;new.NickName=o.NickName;new.Description='Python 3: '+o.NickName;new.Hidden=o.Hidden
  doc.AddObject(new,False);newnodes.append(new)
  for group in doc.Objects:
   if isinstance(group,GH.Kernel.Special.GH_Group) and o.InstanceGuid in list(group.ObjectIDs):
    group.RemoveObject(o.InstanceGuid);group.AddObject(new.InstanceGuid);group.Attributes.ExpireLayout()
 # Replace references to old output ports everywhere, including other new scripts.
 for obj in list(doc.Objects):
  if obj in oldnodes:continue
  inputs=list(obj.Params.Input) if hasattr(obj,'Params') else ([obj] if hasattr(obj,'Sources') else [])
  for p in inputs:
   original=sources.get(p,list(p.Sources))
   if p in sources or any(s in replacements for s in original):
    p.RemoveAllSources()
    for source in original:p.AddSource(replacements.get(source,source))
 for o in oldnodes:doc.RemoveObject(o,False)
 # Recreate group attributes after replacing script objects; cached bounds from
 # the legacy objects can otherwise stretch across the canvas.
 for group in list(doc.Objects):
  if isinstance(group,GH.Kernel.Special.GH_Group):
   nickname=group.NickName;color=group.Colour;members=list(group.ObjectIDs)
   doc.RemoveObject(group,False)
   if nickname=='TIME + ARTICULATION':continue
   fresh=GH.Kernel.Special.GH_Group();fresh.NickName=nickname;fresh.Colour=color;doc.AddObject(fresh,False)
   for guid in members:
    if doc.FindObject(guid,False) is not None:fresh.AddObject(guid)
 GH.Instances.DocumentServer.AddDocument(doc);GH.Instances.ActiveCanvas.Document=doc;doc.Enabled=True;GH.Kernel.GH_Document.EnableSolutions=True
 for o in doc.Objects:o.ExpireSolution(False)
 doc.NewSolution(False);sc.doc=rhdoc
 preview=next(o for o in doc.Objects if o.NickName=='ANIMATED ROBOTS')
 errors={o.NickName:list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)) for o in doc.Objects if hasattr(o,'RuntimeMessages') and list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))}
 archive=GH_IO.Serialization.GH_Archive();archive.AppendObject(doc,'Definition');archive.WriteToFile(doc.FilePath,True,False)
 sc.sticky['python3_'+label]={'doc':doc,'preview':preview,'time':next(o for o in doc.Objects if o.NickName=='PLAYBACK / 0 to 1')}
 return dict(file='grasshopper/'+label+'-Python3.gh',python3_nodes=len(newnodes),legacy_nodes=sum(str(o.GetType())=='GhPython.Component.ZuiPythonComponent' for o in doc.Objects),meshes=preview.VolatileDataCount,errors=errors)
try:
 result=[migrate('Birdland'),migrate('MIDI-Drum')]
 with open(ROOT+'/data/python3-build.json','w') as f:json.dump(result,f,indent=2)
except:
 with open(ROOT+'/data/python3-build.json','w') as f:f.write(traceback.format_exc())
sc.doc=rhdoc
