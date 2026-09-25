import clr,System,Rhino,scriptcontext as sc,json,traceback,os,re,base64
from System.Drawing import PointF,RectangleF,Font
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
 clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
 for a in System.AppDomain.CurrentDomain.GetAssemblies():
  if a.GetName().Name=='GhPython':clr.AddReference(a)
 import Grasshopper as GH,GH_IO
 from GhPython.Component import ZuiPythonComponent
 from Grasshopper.Kernel.Parameters import Param_GenericObject
 from Grasshopper.Kernel.Special import GH_Panel,GH_NumberSlider,GH_Group
 rhdoc=Rhino.RhinoDoc.ActiveDoc;sc.doc=rhdoc
 reader=GH_IO.Serialization.GH_Archive();reader.ReadFromFile(ROOT+'/grasshopper/Birdland-Robots.gh')
 doc=GH.Kernel.GH_Document();reader.ExtractObject(doc,'Definition')
 doc.GetType().GetMethod('SetDocumentID',System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic).Invoke(doc,System.Array[System.Object]([System.Guid.NewGuid()]))
 doc.FilePath=ROOT+'/grasshopper/MIDI-Drum-Robots.gh'
 def place(o,x,y,nick):
  o.CreateAttributes();o.Attributes.Pivot=PointF(x,y);o.NickName=nick;doc.AddObject(o,False);return o
 def panel(value,x,y,nick,w=410,h=100):
  p=place(GH_Panel(),x,y,nick);p.UserText=value;p.Properties.Multiline=True;p.Properties.Font=Font('Arial',10);p.Attributes.Bounds=RectangleF(x,y,w,h);return p
 def slider(value,low,high,x,y,nick,dec=0):
  p=place(GH_NumberSlider(),x,y,nick);p.Slider.Minimum=System.Decimal(low);p.Slider.Maximum=System.Decimal(high);p.Slider.DecimalPlaces=dec;p.SetSliderValue(System.Decimal(value));return p
 core=next(o for o in doc.Objects if o.NickName=='BIRDLAND / AUDIO CLOCK');core.NickName='MIDI / FOUR ARM SOLVER'
 playback=next(o for o in doc.Objects if o.NickName=='PLAYBACK / 0 to 1');playback.SetSliderValue(System.Decimal(.2))
 length=next(o for o in doc.Objects if o.NickName=='CLIP LENGTH / seconds');length.NickName='LEGACY CLIP LENGTH / not used'
 p=Param_GenericObject();p.Name='midijson';p.NickName='midijson';core.Params.RegisterInputParam(p);core.Params.OnParametersChanged()
 code=core.Code
 code=code.replace('duration = float(bpm)','import json\nmidiData=json.loads(str(midijson))\nduration = float(bpm)')
 code=code.replace('patterns = [pattern(snare),pattern(hat),pattern(kick),pattern(pedal)]',"patterns = [midiData['events'][k] for k in ['snare','hat','kick','pedal']]\nhatHistory=[v for v in midiData['velocities'] if v['time']<=seconds and (v['role']=='pedal' or v['note'] in [42,46])]\nmidiOpen=bool(hatHistory and max(hatHistory,key=lambda v:v['time'])['note']==46)")
 code=re.sub(r'heavyTimes = .*',"heavyTimes = midiData['events']['heavy']",code)
 code=re.sub(r'crashTimes = .*',"crashTimes = midiData['events']['crash']",code)
 code=re.sub(r'points\[1\]\.Z \+= .*',"points[1].Z += 4.0 if midiOpen else 0.0",code)
 code=code.replace('    p = points[i] + Vector3d(0,0,lift)',"    roles=[['snare','rim'],['hat','crash'],['kick'],['pedal']][i]\n    hits=[v for v in midiData['velocities'] if v['role'] in roles]\n    velocity=min(hits,key=lambda v:abs(seconds-v['time']))['velocity'] if hits else 64\n    strength=.45+.55*velocity/127.0\n    lift*=strength\n    if i==3:lift=8.0 if midiOpen else 0.0\n    p = points[i] + Vector3d(0,0,lift)")
 code=code.replace('        direction=Vector3d','        swing*=strength\n        direction=Vector3d')
 code=re.sub(r"status = 'BIRDLAND.*", "status = 'MIDI / FOUR ARM STUDY\\\\nTime {0:.2f} / {1:.2f} seconds\\\\nIK errors: {2}\\\\nVelocity scales rebound; hardware dynamics unverified.'.format(seconds,duration,len(errors))",code)
 core.Code=code
 adapter=ZuiPythonComponent();adapter.Name='Standard MIDI file to robot event clock';adapter.NickName='MIDI IMPORT + INTERNALIZE'
 for p in list(adapter.Params.Input):adapter.Params.UnregisterInputParameter(p,True)
 for name in ['file_path','embedded','channel','note_map','start_seconds','speed','tom_policy']:
  p=Param_GenericObject();p.Name=name;p.NickName=name;p.Access=GH.Kernel.GH_ParamAccess.item;adapter.Params.RegisterInputParam(p)
 for p in list(adapter.Params.Output):adapter.Params.UnregisterOutputParameter(p,True)
 for name in ['result_json','duration','snare_times','hat_times','kick_times','pedal_times','report']:
  p=Param_GenericObject();p.Name=name;p.NickName=name;adapter.Params.RegisterOutputParam(p)
 adapter.Params.OnParametersChanged();adapter.Code=open(ROOT+'/src/midi_adapter.py').read()+'\n'+open(ROOT+'/src/gh_midi_wrapper.py').read();place(adapter,-240,230,'MIDI IMPORT + INTERNALIZE');adapter.Hidden=True
 filepanel=panel('',-760,110,'MIDI / FILE TO IMPORT',420,65)
 raw=base64.b64encode(open(ROOT+'/examples/demo-drums.mid','rb').read())
 cache=panel(raw,-760,980,'MIDI / EMBEDDED BYTES',420,85)
 channel=slider(0,-1,16,-760,230,'CHANNEL / 0 auto, -1 all')
 mapping=panel('kick=35,36\nsnare=38,40\nrim=37\nhat=42,46\npedal=44\ncrash=49,51,52,53,55,57,59\ntom=41,43,45,47,48,50',-760,335,'EDITABLE GM NOTE MAP',420,190)
 start=slider(0,0,300,-760,590,'START OFFSET / seconds',3)
 speed=slider(1,.25,3,-760,670,'PLAYBACK SPEED',2)
 tom=panel('snare',-760,740,'TOM POLICY / snare or ignore',420,50)
 for i,o in enumerate([filepanel,cache,channel,mapping,start,speed,tom]):adapter.Params.Input[i].AddSource(o)
 core.Params.Input[1].RemoveAllSources();core.Params.Input[1].AddSource(adapter.Params.Output[1]);core.Params.Input[10].AddSource(adapter.Params.Output[0])
 for i,nick in enumerate(['SNARE / seconds','CYMBAL / seconds','KICK / seconds','HAT PEDAL / chart groove']):
  pp=next(o for o in doc.Objects if o.NickName==nick);pp.RemoveAllSources();pp.AddSource(adapter.Params.Output[i+2]);pp.NickName=['MIDI SNARE','MIDI CYMBALS','MIDI KICK','MIDI PEDAL'][i]
 status=panel('',-260,510,'MIDI IMPORT STATUS',430,255);status.AddSource(adapter.Params.Output[6])
 panel('IMPORT A DRUM MIDI\nPaste an absolute .mid path into FILE TO IMPORT.\nValid imports replace EMBEDDED BYTES and clear the path.\nSave this GH definition after importing.\nThe supplied demo is already embedded.\nDrag PLAYBACK to scrub; the clip duration follows the MIDI.\nGH does not synthesize audio.',-760,-140,'MIDI QUICK START',620,195)
 for o in doc.Objects:
  if isinstance(o,GH_Panel):
   if o.UserText.startswith('BIRDLAND / WEATHER REPORT'):o.UserText='MIDI / FOUR ROBOT ARMS\nStandard MIDI drum adapter\nTwo sticks + kick + hi-hat pedal'
   elif o.UserText.startswith('READ ME'):o.UserText='READ ME\nRequires Rhino 8 + GhPython + Robots 2.4.0 + UniversalRobot library.\nMIDI parser, imported bytes, event data, geometry and solver are internal.\nCustom drum note maps are editable. Type 0/1 MIDI supported.\nTom routing is approximate; unmapped notes are reported.\nNo controller connection. Kinematics only; dynamics/collisions unverified.'
   elif o.UserText.startswith('Drag PLAYBACK'):o.UserText='Drag PLAYBACK to scrub the imported MIDI duration.\nThe MIDI import status reports missing mappings and approximations.\nVelocity scales rebound height. Hi-hat open/closed notes drive the pedal.\nNo external MIDI file is needed after import and Save.'
 group=GH_Group();group.NickName='00 / MIDI FILE -> EMBEDDED EVENTS';doc.AddObject(group,False)
 for o in [adapter,filepanel,cache,channel,mapping,start,speed,tom,status]:group.AddObject(o.InstanceGuid)
 GH.Instances.DocumentServer.AddDocument(doc);GH.Instances.ActiveCanvas.Document=doc;doc.Enabled=True;GH.Kernel.GH_Document.EnableSolutions=True
 for o in doc.Objects:o.ExpireSolution(False)
 doc.NewSolution(False);sc.doc=rhdoc
 sc.sticky['midi_drums']={'doc':doc,'core':core,'adapter':adapter,'time':playback,'file':filepanel,'cache':cache}
 archive=GH_IO.Serialization.GH_Archive();archive.AppendObject(doc,'Definition');archive.WriteToFile(doc.FilePath,True,False)
 with open(ROOT+'/data/midi-build.json','w') as f:json.dump({'meshes':core.Params.Output[0].VolatileDataCount,'coreErrors':list(core.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)),'importErrors':list(adapter.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)),'report':[str(v) for v in adapter.Params.Output[6].VolatileData.AllData(True)]},f,indent=2)
except:
 with open(ROOT+'/data/midi-build.json','w') as f:f.write(traceback.format_exc())
