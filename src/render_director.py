import System,Rhino,scriptcontext as sc,os,json,time,traceback,math,random
from Rhino.Geometry import Point3d,Vector3d,Line
from System.Drawing import Color
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.environ.get('BIRDLAND_OUTPUT',os.path.join(ROOT,'renders','director4k'))
if not os.path.exists(OUT):os.makedirs(OUT)
PREVIEW=False
analysis=json.load(open(ROOT+'/data/edit-analysis.json'))
events=json.load(open(ROOT+'/data/birdland-events.json'))['events']
# The orbital camera continues on its global clock underneath each close-up.
def camera(vp,sec):
 cuts=analysis['cuts'];cut=max([v for v in cuts if v['start']<=sec],key=lambda v:v['start'])
 mode=cut['view'];elapsed=sec-cut['start']
 if mode=='orbit':
  u=sec/75.0;a=-1.02+3*math.pi*u;r=6400-650*math.sin(math.pi*u)**2;z=2400+1050*math.sin(math.pi*u)**2
  target=Point3d(0,-100,700+150*math.sin(math.pi*u));eye=Point3d(r*math.cos(a),-100+r*math.sin(a),z);lens=38
 else:
  settings={'hat':((600,-45,930),(1750,-1900,1700),55),'hat_pedal':((550,-340,110),(200,-1450,650),45),'kick':((0,-325,275),(450,-1900,1050),48),'rim':((-350,10,690),(250,1000,1900),52),'snare':((-350,-50,720),(150,1000,1850),50)}
  target0,eye0,lens=settings[mode];target=Point3d(*target0);base=Point3d(*eye0)
  delta=base-target;delta*=1-.025*min(elapsed,3);eye=target+delta;eye.X+=22*elapsed
 vp.ChangeToPerspectiveProjection(True,lens);vp.SetCameraLocations(target,eye);vp.CameraUp=Vector3d.ZAxis
 return mode
bursts=[]
maxstrength=max(v['strength'] for v in analysis['shots'])
for idx,event in enumerate(analysis['shots']):
 sec=event['frame']/24.0;power=(event['strength']/maxstrength)**.5
 for side in range(2 if power>.6 else 1):
  rng=random.Random(idx*83+side*17+9);a=idx*1.91+side*math.pi
  center=Point3d(2050*math.cos(a),-100+2050*math.sin(a),1850+rng.random()*250)
  palette=[(255,175,50),(55,235,255),(255,80,175),(255,220,140)];rays=[]
  for j in range(int(50+40*power)):
   zz=rng.uniform(-1,1);ang=rng.random()*2*math.pi;rr=math.sqrt(1-zz*zz);speed=rng.uniform(350,750)*(.65+.35*power)
   rays.append((rr*math.cos(ang)*speed,rr*math.sin(ang)*speed,zz*speed))
  bursts.append((sec,center,palette[(idx+side)%4],rays))
def spark(center,vel,age):
 drag=(1-math.exp(-.65*age))/.65
 return Point3d(center.X+vel[0]*drag,center.Y+vel[1]*drag,center.Z+vel[2]*drag-180*age*age)
class Fireworks(Rhino.Display.DisplayConduit):
 def __init__(self):self.seconds=0;self.failed=None
 def PostDrawObjects(self,e):
  try:
   t=self.seconds
   for sec,c,rgb,rays in bursts:
    age=t-sec
    if 0<=age<.09:
     e.Display.DrawPoint(c,Rhino.Display.PointStyle.RoundSimple,int(22*(1-age/.09))+4,Color.FromArgb(255,246,206))
    if -.7<age<0:
     f=(age+.7)/.7;p=Point3d(c.X,c.Y,40+(c.Z-40)*f)
     e.Display.DrawLine(Line(Point3d(p.X,p.Y,max(20,p.Z-160)),p),Color.FromArgb(255,183,65),2)
     e.Display.DrawPoint(p,Rhino.Display.PointStyle.RoundSimple,4,Color.FromArgb(255,248,205))
    if age<0 or age>1.35:continue
    fade=max(0,1-age/1.35)**.65
    for j,v in enumerate(rays):
     tip=spark(c,v,age+.06)
     for k in range(3):
      a=max(0,age+.06-(k+1)*.07);b=max(0,age+.06-k*.07)
      bright=fade*(1-k*.24)
      col=Color.FromArgb(int(rgb[0]*bright),int(rgb[1]*bright),int(rgb[2]*bright))
      e.Display.DrawLine(Line(spark(c,v,a),spark(c,v,b)),col,5 if k==0 else 3)
     if (j+int(age*30))%5!=0:e.Display.DrawPoint(tip,Rhino.Display.PointStyle.RoundSimple,3,Color.FromArgb(int(255*fade),int(248*fade),int(218*fade)))
   # Short contact glint emphasizes the far snare rim during side-stick clicks.
   nearest=min([abs(t-v) for v in events['rim']]+[100])
   if nearest<.065:
    gain=1-nearest/.065;col=Color.FromArgb(int(255*gain),int(198*gain),int(80*gain))
    e.Display.DrawCircle(Rhino.Geometry.Circle(Rhino.Geometry.Plane(Point3d(-350,-100,674),Vector3d.ZAxis),181),col,3)
    e.Display.DrawPoint(Point3d(-350,80,674),Rhino.Display.PointStyle.RoundSimple,7,Color.FromArgb(255,228,149))
  except Exception as ex:self.failed=str(ex)
try:
 import Grasshopper as GH
 rhdoc=Rhino.RhinoDoc.ActiveDoc;sc.doc=rhdoc;d=sc.sticky['birdland_extended'];doc=d['doc'];core=d['core']
 GH.Instances.ActiveCanvas.Document=doc;doc.Enabled=True;GH.Kernel.GH_Document.EnableSolutions=True
 core.ExpireSolution(False);doc.NewSolution(False);sc.doc=rhdoc
 folder=OUT+('/preview' if PREVIEW else '/frames')
 if not os.path.exists(folder):os.makedirs(folder)
 view=rhdoc.Views.ActiveView;vp=view.ActiveViewport
 cap=Rhino.Display.ViewCapture();cap.Width=3840;cap.Height=2160;cap.ScaleScreenItems=False;cap.DrawAxes=False;cap.DrawGrid=False;cap.DrawGridAxes=False
 fx=Fireworks();fx.Enabled=True;sc.sticky['spiral_fx']=fx
 started=time.time();errors=[];rhdoc.UndoRecordingEnabled=False
 batch=json.load(open(ROOT+'/data/render-batch.json'))
 frames=[444,451,517,540,1035] if PREVIEW else batch.get('frames',list(range(batch['start'],batch['end'])))
 # Prime capture dimensions before setting the first camera lens. Rhino can otherwise
 # reuse the on-screen viewport projection for one frame after a resize/restart.
 warmup=cap.CaptureToBitmap(view);warmup.Dispose()
 for n in frames:
  sec=n/24.0;camera(vp,sec);fx.seconds=sec
  d['time'].SetSliderValue(System.Decimal(n/1800.0));d['time'].ExpireSolution(False);doc.NewSolution(False);sc.doc=rhdoc
  source=list(core.Params.Output[0].VolatileData.AllData(True))
  if len(source)!=49:raise Exception('Mesh count '+str(len(source))+' at '+str(n))
  err=[str(v) for v in core.Params.Output[2].VolatileData.AllData(True)]
  if err:errors.append({'frame':n,'errors':err})
  for oid,item in zip(d['dynamic'],source):
   mesh=item.Value.DuplicateMesh();mesh.VertexColors.Clear();rhdoc.Objects.Replace(oid,mesh)
  bmp=cap.CaptureToBitmap(view);bmp.Save(folder+'/frame_{0:04d}.png'.format(n),System.Drawing.Imaging.ImageFormat.Png);bmp.Dispose()
  if fx.failed:raise Exception(fx.failed)
  if n%24==0:
   rhdoc.ClearUndoRecords(True);System.GC.Collect();System.GC.WaitForPendingFinalizers();Rhino.RhinoApp.Wait()
  if n%80==0 or PREVIEW:
   with open(OUT+'/progress.json','w') as f:json.dump({'frame':n,'total':1680,'elapsed':time.time()-started,'preview':PREVIEW},f)
 fx.Enabled=False
 with open(OUT+('/preview-validation.json' if PREVIEW else '/validation-{0:04d}.json'.format(batch['start'])),'w') as f:json.dump({'frames':len(frames),'fps':24,'duration':70,'frameStart':min(frames),'frameEnd':max(frames),'armPoses':len(frames)*4,'ikErrors':errors,'componentErrors':list(core.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)),'camera':'Alternating global orbit and event-led instrument close-ups','fireworks':'Drum/mix spectral-onset peaks, frame-snapped; strength-scaled 3D bursts only during shots'},f,indent=2)
 with open(OUT+'/progress.json','w') as f:json.dump({'done':True,'preview':PREVIEW,'start':min(frames),'end':max(frames),'elapsed':time.time()-started},f)
except:
 if 'fx' in globals():fx.Enabled=False
 with open(OUT+'/progress.json','w') as f:f.write(traceback.format_exc())
