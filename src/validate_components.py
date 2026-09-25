import clr,System,Rhino,scriptcontext as sc,json,traceback,os,math
clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
import Grasshopper as GH,GH_IO
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rhdoc=Rhino.RhinoDoc.ActiveDoc
try:
 results=[]
 for midi in [False,True]:
  new=sc.sticky['components_'+str(midi)]
  a=GH_IO.Serialization.GH_Archive();a.ReadFromFile(ROOT+'/grasshopper/'+new['oldname']+'.gh');old=GH.Kernel.GH_Document();a.ExtractObject(old,'Definition')
  core=next(o for o in old.Objects if hasattr(o,'Code') and 'IMPORT' not in o.NickName)
  slider=next(o for o in old.Objects if o.NickName=='PLAYBACK / 0 to 1')
  GH.Instances.DocumentServer.AddDocument(old);old.Enabled=True
  for o in old.Objects:o.ExpireSolution(False)
  old.NewSolution(False);sc.doc=rhdoc
  maxdelta=0;counts=[];errors=[]
  samples=[i/48.0 for i in range(49)]+[.5729,.588,.600,.652,.3,.1,.9,.0]
  for t in samples:
   for d,s in [(old,slider),(new['doc'],new['time'])]:
    GH.Instances.ActiveCanvas.Document=d;d.Enabled=True
    s.SetSliderValue(System.Decimal(t));s.ExpireSolution(False);d.NewSolution(False);sc.doc=rhdoc
   before=[v.Value for v in core.Params.Output[0].VolatileData.AllData(True)]
   after=[v.Value for v in new['preview'].VolatileData.AllData(True)]
   counts.append([len(before),len(after)])
   if len(before)!=49 or len(after)!=49:raise Exception('Wrong mesh count '+str(counts[-1]))
   for a,b in zip(before,after):
    if a.Vertices.Count!=b.Vertices.Count:raise Exception('Mesh topology mismatch')
    for j in range(a.Vertices.Count):maxdelta=max(maxdelta,a.Vertices[j].DistanceTo(b.Vertices[j]))
   for o in new['doc'].Objects:
    if hasattr(o,'RuntimeMessages'):
     for e in o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error):errors.append([t,o.NickName,str(e)])
  results.append(dict(file=new['doc'].FilePath,samples=len(samples),arm_poses=len(samples)*4,max_vertex_delta_mm=maxdelta,errors=errors,meshes=49))
  GH.Instances.DocumentServer.RemoveDocument(old)
  # Reload the saved file to verify serialization of native variable target ports.
  ar=GH_IO.Serialization.GH_Archive();ar.ReadFromFile(new['doc'].FilePath);loaded=GH.Kernel.GH_Document();ar.ExtractObject(loaded,'Definition');GH.Instances.DocumentServer.AddDocument(loaded);loaded.Enabled=True;GH.Instances.ActiveCanvas.Document=loaded
  for o in loaded.Objects:o.ExpireSolution(False)
  loaded.NewSolution(False);sc.doc=rhdoc
  results[-1]['reload_meshes']=next(o for o in loaded.Objects if o.NickName=='ANIMATED ROBOTS').VolatileDataCount
  results[-1]['reload_errors']={o.NickName:list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)) for o in loaded.Objects if hasattr(o,'RuntimeMessages') and list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))}
  GH.Instances.DocumentServer.RemoveDocument(loaded)
 GH.Instances.ActiveCanvas.Document=sc.sticky['components_False']['doc']
 with open(ROOT+'/data/components-validation.json','w') as f:json.dump(results,f,indent=2)
except:
 with open(ROOT+'/data/components-validation.json','w') as f:f.write(traceback.format_exc())
sc.doc=rhdoc
