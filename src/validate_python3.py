# Run in Rhino after migrate_python3.py. Compare every mesh vertex bit-for-bit.
import clr,System,Rhino,scriptcontext as sc,json,traceback,os
clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
import Grasshopper as GH,GH_IO
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rhdoc=Rhino.RhinoDoc.ActiveDoc

def load(path):
 a=GH_IO.Serialization.GH_Archive();a.ReadFromFile(path);d=GH.Kernel.GH_Document();a.ExtractObject(d,'Definition')
 d.GetType().GetMethod('SetDocumentID',System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic).Invoke(d,System.Array[System.Object]([System.Guid.NewGuid()]))
 GH.Instances.DocumentServer.AddDocument(d);GH.Instances.ActiveCanvas.Document=d;d.Enabled=True
 for o in d.Objects:o.ExpireSolution(False)
 d.NewSolution(False);sc.doc=rhdoc
 return d

def signatures(port):
 result=[]
 for goo in port.VolatileData.AllData(True):
  m=goo.Value;coords=m.Vertices.ToFloatArray()
  data=System.Array.CreateInstance(System.Byte,System.Buffer.ByteLength(coords));System.Buffer.BlockCopy(coords,0,data,0,data.Length)
  sha=System.Security.Cryptography.SHA256.Create()
  result.append([m.Vertices.Count,m.Faces.Count,System.Convert.ToBase64String(sha.ComputeHash(data))]);sha.Dispose()
 return result

def errors(d):return {o.NickName:list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)) for o in d.Objects if hasattr(o,'RuntimeMessages') and list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))}
try:
 results=[]
 samples=[i/48.0 for i in range(49)]+[.5729,.588,.600,.652,.3,.1,.9,.0]
 for label in ['Birdland','MIDI-Drum']:
  old=load(ROOT+'/grasshopper/'+label+'-Robots.gh')
  core=next(o for o in old.Objects if hasattr(o,'Code') and 'IMPORT' not in o.NickName)
  oldtime=next(o for o in old.Objects if o.NickName=='PLAYBACK / 0 to 1')
  reference=[]
  for t in samples:
   oldtime.SetSliderValue(System.Decimal(t));oldtime.ExpireSolution(False);old.NewSolution(False);sc.doc=rhdoc
   sig=signatures(core.Params.Output[0]);assert len(sig)==49
   reference.append(sig)
  GH.Instances.DocumentServer.RemoveDocument(old)
  new=sc.sticky['python3_'+label];d=new['doc'];GH.Instances.ActiveCanvas.Document=d;d.Enabled=True
  for o in d.Objects:o.ExpireSolution(False)
  for i,t in enumerate(samples):
   new['time'].SetSliderValue(System.Decimal(t));new['time'].ExpireSolution(False);d.NewSolution(False);sc.doc=rhdoc
   actual=signatures(new['preview'])
   assert len(actual)==49,'Mesh count {0} at {1}: {2}'.format(len(actual),t,errors(d))
   assert actual==reference[i],'Vertex mismatch at '+str(t)
   assert not errors(d),str(errors(d))
  # A separate reload proves modern ports, marshalling flags and source survive save.
  reloaded=load(d.FilePath);out=next(o for o in reloaded.Objects if o.NickName=='ANIMATED ROBOTS')
  assert out.VolatileDataCount==49
  assert not errors(reloaded),str(errors(reloaded))
  results.append(dict(file='grasshopper/'+label+'-Python3.gh',samples=len(samples),arm_poses=len(samples)*4,meshes=49,all_vertex_hashes_identical=True,errors={},reload_meshes=49,reload_errors={}))
  GH.Instances.DocumentServer.RemoveDocument(reloaded)
 GH.Instances.ActiveCanvas.Document=sc.sticky['python3_Birdland']['doc']
 with open(ROOT+'/data/python3-validation.json','w') as f:json.dump(results,f,indent=2)
except:
 with open(ROOT+'/data/python3-validation.json','w') as f:f.write(traceback.format_exc())
sc.doc=rhdoc
