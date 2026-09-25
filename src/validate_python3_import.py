# Run twice: phase 1 imports a new MIDI and returns to Rhino's event loop;
# phase 2 verifies the scheduled cache update, saves and reopens without the MIDI.
import clr,System,Rhino,scriptcontext as sc,json,traceback,os,struct,tempfile
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
import Grasshopper as GH,GH_IO
rhdoc=Rhino.RhinoDoc.ActiveDoc

def load(path):
 a=GH_IO.Serialization.GH_Archive();a.ReadFromFile(path);d=GH.Kernel.GH_Document();a.ExtractObject(d,'Definition')
 d.GetType().GetMethod('SetDocumentID',System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic).Invoke(d,System.Array[System.Object]([System.Guid.NewGuid()]))
 GH.Instances.DocumentServer.AddDocument(d);GH.Instances.ActiveCanvas.Document=d;d.Enabled=True
 for o in d.Objects:o.ExpireSolution(False)
 d.NewSolution(False);sc.doc=rhdoc
 return d

def named(d,n):return next(o for o in d.Objects if o.NickName==n)
def errors(d):return {o.NickName:list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)) for o in d.Objects if hasattr(o,'RuntimeMessages') and list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))}
def midi_result(d):return json.loads(str(list(named(d,'MIDI IMPORT + INTERNALIZE').Params.Output[0].VolatileData.AllData(True))[0]))
try:
 if 'python3_import_test' not in sc.sticky:
  folder=tempfile.mkdtemp(prefix='birdland-python3-midi-');path=folder+'/fixture.mid'
  def vlq(v):
   values=[v&127];v>>=7
   while v:values.insert(0,(v&127)|128);v>>=7
   return ''.join(chr(n) for n in values)
  track='\x00\xff\x51\x03\x07\xa1\x20'
  for i,(note,velocity) in enumerate([(42,80),(36,100),(46,60),(38,120),(44,70),(37,50)]):
   track+=vlq(0 if i==0 else 230)+'\x99'+chr(note)+chr(velocity)
   track+=vlq(10)+'\x89'+chr(note)+'\x00'
  track+='\x00\xff\x2f\x00'
  raw='MThd'+struct.pack('>IHHH',6,0,1,480)+'MTrk'+struct.pack('>I',len(track))+track
  with open(path,'wb') as f:f.write(raw)
  d=load(ROOT+'/grasshopper/MIDI-Drum-Python3.gh');cached=named(d,'MIDI / EMBEDDED BYTES').UserText
  source=named(d,'MIDI / FILE TO IMPORT');source.UserText=path;source.ExpireSolution(False);d.NewSolution(False);sc.doc=rhdoc
  sc.sticky['python3_import_test']=dict(doc=d,folder=folder,path=path,previous_cache=cached)
  result=dict(phase='awaiting scheduled cache update',import_errors=errors(d),notes=midi_result(d)['note_count'])
 else:
  test=sc.sticky['python3_import_test'];d=test['doc'];GH.Instances.ActiveCanvas.Document=d;d.Enabled=True;d.NewSolution(False);sc.doc=rhdoc
  source=named(d,'MIDI / FILE TO IMPORT');cache=named(d,'MIDI / EMBEDDED BYTES');data=midi_result(d)
  assert source.UserText=='','Import path did not clear'
  assert cache.UserText!=test['previous_cache'],'Embedded bytes did not update'
  assert data['note_count']==6,str(data)
  assert not errors(d),str(errors(d))
  saved=test['folder']+'/imported.gh';a=GH_IO.Serialization.GH_Archive();a.AppendObject(d,'Definition');a.WriteToFile(saved,True,False)
  os.rename(test['path'],test['path']+'.unavailable')
  reloaded=load(saved);redata=midi_result(reloaded)
  assert redata==data,'MIDI data changed after save/reload'
  assert named(reloaded,'ANIMATED ROBOTS').VolatileDataCount==49
  assert not errors(reloaded),str(errors(reloaded))
  # Failed imports must leave the last valid embedded bytes untouched.
  before=named(reloaded,'MIDI / EMBEDDED BYTES').UserText
  bad=test['folder']+'/invalid.mid'
  with open(bad,'wb') as f:f.write('not a MIDI file')
  filepanel=named(reloaded,'MIDI / FILE TO IMPORT');filepanel.UserText=bad;filepanel.ExpireSolution(False);reloaded.NewSolution(False);sc.doc=rhdoc
  failure=list(named(reloaded,'MIDI IMPORT + INTERNALIZE').RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))
  assert failure,'Invalid MIDI was not reported'
  assert before==named(reloaded,'MIDI / EMBEDDED BYTES').UserText,'Failed import replaced valid cache'
  filepanel.UserText='';filepanel.ExpireSolution(False);reloaded.NewSolution(False);sc.doc=rhdoc
  assert named(reloaded,'ANIMATED ROBOTS').VolatileDataCount==49
  result=dict(phase='complete',fresh_import_notes=6,path_cleared=True,cache_changed=True,reloaded_without_source=True,reload_meshes=49,reload_data_identical=True,invalid_import_reported=True,invalid_import_preserved_cache=True,recovered_meshes=49,errors=errors(reloaded))
  GH.Instances.DocumentServer.RemoveDocument(d);GH.Instances.DocumentServer.RemoveDocument(reloaded)
  GH.Instances.ActiveCanvas.Document=sc.sticky['python3_Birdland']['doc']
 with open(ROOT+'/data/python3-import-validation.json','w') as f:json.dump(result,f,indent=2)
except:
 with open(ROOT+'/data/python3-import-validation.json','w') as f:f.write(traceback.format_exc())
sc.doc=rhdoc
