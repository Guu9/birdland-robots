# Run in Rhino 8. Creates separate componentized definitions; originals stay intact.
import clr,System,Rhino,scriptcontext as sc,json,traceback,os,re
from System.Drawing import PointF,RectangleF,Font,Color
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
for a in System.AppDomain.CurrentDomain.GetAssemblies():
 if a.GetName().Name in ['Robots','Robots.Grasshopper','GhPython']:clr.AddReference(a)
import Grasshopper as GH,GH_IO,Robots.Grasshopper as RG
from GhPython.Component import ZuiPythonComponent
from Grasshopper.Kernel.Parameters import Param_GenericObject,Param_Plane,Param_String,Param_Geometry
from Grasshopper.Kernel.Special import GH_Panel,GH_NumberSlider,GH_Group,GH_BooleanToggle
from Grasshopper.Kernel.Types import GH_Plane,GH_String
rhdoc=Rhino.RhinoDoc.ActiveDoc

def read(label):
 a=GH_IO.Serialization.GH_Archive();a.ReadFromFile(ROOT+'/grasshopper/'+label+'.gh');d=GH.Kernel.GH_Document();a.ExtractObject(d,'Definition');return d

def build(midi):
 oldname='MIDI-Drum-Robots' if midi else 'Birdland-Robots'
 doc=read(oldname)
 old=next(o for o in doc.Objects if hasattr(o,'Code') and 'IMPORT' not in o.NickName)
 code=old.Code
 stage=next(o for o in doc.Objects if o.NickName=='INTERNAL STAGE GEOMETRY')
 clockslider=next(o for o in doc.Objects if o.NickName=='PLAYBACK / 0 to 1')
 loaders=[next(o for o in doc.Objects if o.NickName==n) for n in ['SNARE ARM','HAT ARM','KICK ARM','PEDAL ARM']]
 modelvalue=str(list(loaders[0].Params.Input[0].PersistentData.AllData(True))[0])
 bases=[list(o.Params.Input[1].PersistentData.AllData(True))[0].Value for o in loaders]
 adapter=next((o for o in doc.Objects if o.NickName=='MIDI IMPORT + INTERNALIZE'),None)
 keep=[stage,clockslider]+loaders
 if midi:
  keep += [adapter]+[p.Sources[0] for p in adapter.Params.Input]
 else:
  length=next(o for o in doc.Objects if o.NickName=='CLIP LENGTH / seconds');keep.append(length)
  eventpanels=[next(o for o in doc.Objects if o.NickName==n) for n in ['SNARE / seconds','CYMBAL / seconds','KICK / seconds','HAT PEDAL / chart groove']];keep+=eventpanels
 for o in list(doc.Objects):
  if o not in keep:doc.RemoveObject(o,False)
 doc.GetType().GetMethod('SetDocumentID',System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic).Invoke(doc,System.Array[System.Object]([System.Guid.NewGuid()]))
 doc.FilePath=ROOT+'/grasshopper/'+('MIDI-Drum-Components' if midi else 'Birdland-Components')+'.gh'
 def place(o,x,y,nick=None):
  if o.Attributes is None:o.CreateAttributes()
  o.Attributes.Pivot=PointF(x,y)
  if nick is not None:o.NickName=nick
  if not doc.FindObject(o.InstanceGuid,False):doc.AddObject(o,False)
  if hasattr(o,'Hidden'):o.Hidden=True
  return o
 def panel(value,x,y,nick,w=230,h=65):
  p=place(GH_Panel(),x,y,nick);p.UserText=value;p.Properties.Multiline=True;p.Properties.Font=Font('Arial',10);p.Attributes.Bounds=RectangleF(x,y,w,h);return p
 def py(name,filename,inputs,outputs,x,y,body=None):
  c=ZuiPythonComponent();c.Name=name
  for p in list(c.Params.Input):c.Params.UnregisterInputParameter(p,True)
  for spec in inputs:
   p=Param_GenericObject();p.Name=p.NickName=spec.rstrip('*');p.Access=GH.Kernel.GH_ParamAccess.list if spec.endswith('*') else GH.Kernel.GH_ParamAccess.item;c.Params.RegisterInputParam(p)
  for p in list(c.Params.Output):c.Params.UnregisterOutputParameter(p,True)
  for n in outputs:
   p=Param_GenericObject();p.Name=p.NickName=n;c.Params.RegisterOutputParam(p)
  c.Params.OnParametersChanged();c.Code=body if body is not None else open(ROOT+'/src/components/'+filename+'.py').read();return place(c,x,y,name)
 def wire(c,i,source,j=None):c.Params.Input[i].AddSource(source if j is None else source.Params.Output[j])
 def group(title,objects,color):
  g=GH_Group();g.NickName=title;g.Colour=Color.FromArgb(50,*color);doc.AddObject(g,False)
  for o in objects:g.AddObject(o.InstanceGuid)
  return g
 panel(('MIDI' if midi else 'BIRDLAND')+' / FOUR ROBOT DRUMMERS\nRead left to right. Each lane drives one arm.',-520,-510,'COMPONENT STUDY',720,80)
 panel('Purple: event timing / Blue: target geometry / Green: native Robots components\nScrub PLAYBACK. Double-click a Python node to inspect its small, single-purpose operation.\nMeshes, event data and code are embedded. Camera, fireworks and audio remain in the render script.',260,-510,'HOW TO READ',1230,80)
 place(clockslider,-520,-310);clockslider.SetSliderValue(System.Decimal(.3))
 if midi:
  place(adapter,-720,80)
  for idx,p in enumerate(adapter.Params.Input):
   obj=p.Sources[0];place(obj,-1280,-100+idx*125)
   if isinstance(obj,GH_Panel):obj.Attributes.Bounds=RectangleF(-1280,-100+idx*125,390,95)
  dur=adapter.Params.Output[1]
  report=panel('',-1280,840,'IMPORT REPORT',430,180);report.AddSource(adapter.Params.Output[6])
 else:
  place(length,-520,-230);dur=length
 clock=py('SECONDS + FRAME','clock',['playback','duration'],['seconds','frame'],20,-270)
 wire(clock,0,clockslider);wire(clock,1,dur)
 if midi:
  eventbody="import json\nd=json.loads(str(midi_json))\nsnare=d['events']['snare'];hat=d['events']['hat'];kick=d['events']['kick'];pedal=d['events']['pedal']\ns=dict(heavy=d['events']['heavy'],crash=d['events']['crash'],pedal=pedal,velocities=d['velocities'],midi=True)\nevent_data=json.dumps(s)"
  decoder=py('DRUM EVENT LANES',None,['midi_json'],['snare','hat','kick','pedal','event_data'],-280,60,eventbody);wire(decoder,0,adapter,0)
 else:
  heavies=re.search(r'^heavyTimes = (.*)$',code,re.M).group(1);crashes=re.search(r'^crashTimes = (.*)$',code,re.M).group(1)
  heavy=panel(','.join(str(v) for v in json.loads(heavies)),-520,1240,'SNARE ACCENTS / seconds',280,90)
  crash=panel(','.join(str(v) for v in json.loads(crashes)),-520,1360,'CRASH ACCENTS / seconds',280,90)
  eventbody="import json\ndef parse(s):return sorted(set(float(v.strip()) for v in str(s).split(',') if v.strip()))\nsnare=parse(snare_csv);hat=parse(hat_csv);kick=parse(kick_csv);pedal=parse(pedal_csv)\nevent_data=json.dumps(dict(heavy=parse(heavy_csv),crash=parse(crash_csv),pedal=pedal,velocities=[],midi=False))"
  decoder=py('PARSE HIT TIMES',None,['snare_csv','hat_csv','kick_csv','pedal_csv','heavy_csv','crash_csv'],['snare','hat','kick','pedal','event_data'],-100,580,eventbody)
  for i,p in enumerate(eventpanels):place(p,-520,80+i*280);p.Attributes.Bounds=RectangleF(-520,80+i*280,280,110);wire(decoder,i,p)
  wire(decoder,4,heavy);wire(decoder,5,crash)
 articulation=py('RIM / CRASH / HAT STATE','articulation',['seconds','event_data'],['articulation'],250,-140);wire(articulation,0,clock,0);wire(articulation,1,decoder,4)
 model=panel(modelvalue,700,-360,'ROBOT MODEL',230,50)
 show=place(GH_BooleanToggle(),1320,-280,'OUTPUT ROBOT MESHES');show.Value=True
 linear=panel('Linear',1000,-350,'TARGET MOTION',150,50)
 lens=[];tools=[]
 for k,L in enumerate([300,100]):
  ln=panel(str(L),-520,-80+110*k,'STICK mm' if k==0 else 'PRESSER mm',130,45);lens.append(ln)
  geo=py('STICK GEOMETRY' if k==0 else 'PRESSER GEOMETRY','tool_geometry',['length'],['mesh','tcp'],20, -65+100*k);wire(geo,0,ln)
  tool=place(RG.CreateTool(),420,-300+150*k,'STICK TOOL' if k==0 else 'PRESSER TOOL');tool.Params.Input[0].PersistentData.Clear();tool.Params.Input[0].PersistentData.Append(GH_String('Stick' if k==0 else 'PedalPress'));wire(tool,1,geo,1);wire(tool,5,geo,0);tools.append(tool)
  # Match the original tool mass.
  from Grasshopper.Kernel.Types import GH_Number
  tool.Params.Input[3].PersistentData.Clear();tool.Params.Input[3].PersistentData.Append(GH_Number(.15))
 solvers=[];rebounds=[];targets=[]
 preview=place(Param_Geometry(),1900,720,'ANIMATED ROBOTS');preview.Hidden=False
 for i,name in enumerate(['SNARE','HI-HAT','KICK','HAT PEDAL']):
  y=260+i*290
  idx=panel(str(i),100,y+90,name+' / ARM INDEX',105,45)
  pulse=py(name+' REBOUND','rebound',['seconds','events*','articulation','arm_index'],['rebound','lift','phase'],470,y);wire(pulse,0,clock,0);wire(pulse,1,decoder,i);wire(pulse,2,articulation,0);wire(pulse,3,idx);rebounds.append(pulse)
  plane=py(name+' TARGET PLANE','target_plane',['rebound','lift','articulation','arm_index','length'],['plane','contact'],800,y);wire(plane,0,pulse,0);wire(plane,1,pulse,1);wire(plane,2,articulation,0);wire(plane,3,idx);wire(plane,4,lens[0 if i<2 else 1])
  target=place(RG.CreateTarget(),1150,y,name+' TARGET')
  motion=Param_String();motion.Name='Motion';motion.NickName='M';motion.Optional=True;target.Params.RegisterInputParam(motion)
  toolp=RG.ToolParameter();toolp.Name='Tool';toolp.NickName='T';toolp.Optional=True;target.Params.RegisterInputParam(toolp);target.Params.OnParametersChanged()
  wire(target,0,plane,0);wire(target,1,linear);wire(target,2,tools[0 if i<2 else 1],0);targets.append(target)
  base=place(Param_Plane(),800,y+115,name+' MOUNT');base.PersistentData.Append(GH_Plane(bases[i]));base.Description='Editable mounting plane in world millimetres.'
  robot=place(loaders[i],1150,y+125,'LOAD '+name+' UR10e')
  for p in list(robot.Params.Input)[:2]:p.RemoveAllSources();p.PersistentData.Clear()
  wire(robot,0,model);wire(robot,1,base)
  solve=place(RG.Kinematics(),1500,y,name+' IK');wire(solve,0,robot,0);wire(solve,1,target,0);wire(solve,3,show);solvers.append(solve)
  preview.AddSource(solve.Params.Output[0])
  joints=panel('',1700,y-25,name+' JOINTS / radians',280,60);joints.AddSource(solve.Params.Output[1])
  err=panel('',1700,y+55,name+' IK ERRORS',280,45);err.AddSource(solve.Params.Output[3])
  group(str(i+1)+' / '+name,[idx,pulse,plane,base,robot,target,solve,joints,err],(70,155,180))
 mechanism=py('PEDAL LINKAGES + TOP CYMBAL','pedal_mechanisms',['kick_lift','hat_lift'],['meshes'],1500,1500);wire(mechanism,0,rebounds[2],1);wire(mechanism,1,rebounds[3],1);preview.AddSource(mechanism.Params.Output[0])
 place(stage,1900,1450);stage.Hidden=False
 panel('OUTPUT\n32 posed robot/tool meshes + 17 mechanism meshes\nJoint angles and IK errors are visible for each arm.\nNative Robots nodes solve poses; no hardware is connected.',1750,1600,'PREVIEW',360,110)
 group('TIME + ARTICULATION',[clock,clockslider,decoder,articulation],(180,110,205))
 GH.Instances.DocumentServer.AddDocument(doc);GH.Instances.ActiveCanvas.Document=doc;doc.Enabled=True;GH.Kernel.GH_Document.EnableSolutions=True
 for o in doc.Objects:o.ExpireSolution(False)
 doc.NewSolution(False);sc.doc=rhdoc
 archive=GH_IO.Serialization.GH_Archive();archive.AppendObject(doc,'Definition');archive.WriteToFile(doc.FilePath,True,False)
 errors={o.NickName:list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)) for o in doc.Objects if hasattr(o,'RuntimeMessages') and list(o.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))}
 sc.sticky['components_'+str(midi)]={'doc':doc,'time':clockslider,'preview':preview,'solvers':solvers,'targets':targets,'oldname':oldname}
 return dict(file=doc.FilePath,meshes=preview.VolatileDataCount,errors=errors,objects=len(list(doc.Objects)))
try:
 results=[build(False),build(True)]
 with open(ROOT+'/data/components-build.json','w') as f:json.dump(results,f,indent=2)
except:
 with open(ROOT+'/data/components-build.json','w') as f:f.write(traceback.format_exc())
sc.doc=rhdoc
