from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'docs'
p=R/'Birdland-Pseudocode.pdf'
c=canvas.Canvas(str(p),pagesize=(842,595));c.setTitle('Birdland - Pseudocode and Design Intent')
navy='#0A1721';teal='#25CED0';white='#F1F5F6';muted='#A4BBC5'
c.setFillColor(HexColor(navy));c.rect(0,0,842,595,fill=1,stroke=0)
def text(x,y,t,size=10,color=white,font='Helvetica'):
 c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,t)
def paragraph(x,y,s,w,size=10,color=muted,leading=14):
 for line in simpleSplit(s,'Helvetica',size,w):text(x,y,line,size,color);y-=leading
 return y
text(32,554,'BIRDLAND / FOUR ROBOT ARMS',28,white,'Helvetica-Bold')
text(33,531,'KINEMATIC DRUM STUDY  /  RHINO 8 + GRASSHOPPER + ROBOTS 2.4.0',10,teal)

def box(x,y,w,h,num,title,lines):
 c.setStrokeColor(HexColor('#294654'));c.setFillColor(HexColor('#102632'));c.roundRect(x,y,w,h,7,fill=1,stroke=1)
 text(x+13,y+h-23,num+' / '+title,11,teal,'Helvetica-Bold')
 yy=y+h-45
 for line in lines:yy=paragraph(x+13,yy,line,w-26,9,white,12)-5

def arrow(x,y,xx,yy):
 c.setStrokeColor(HexColor(teal));c.setLineWidth(1.4);c.line(x,y,xx,yy)
 import math
 a=math.atan2(yy-y,xx-x)
 for q in [-.45,.45]:c.line(xx,yy,xx-6*math.cos(a+q),yy-6*math.sin(a+q))
box(32,325,177,169,'01','INPUTS',['Clock: 75 s / movie: first 70 s','Playback: t in [0, 1]','Chart + audio hit times, or MIDI note events','Four UR10e base planes + tool geometry','Embedded stage, solver and timing data'])
box(232,325,177,169,'02','MUSICAL CLOCK',['seconds = clipLength * t','Use recorded events or MIDI ticks converted through its tempo map','MIDI velocity scales stroke height; imported bytes are embedded','For each arm: distance = nearest hit in seconds','phase = clamp(distance / strokeWindow, 0, 1)'])
box(432,325,177,169,'03','MOTION',['rebound = (1 - cos(pi * phase)) / 2','STICKS: flat cross-stick clicks in intro; larger strokes for fill and shots','PEDALS: kick linked to beater; hats open and close with the groove.','Right arm travels to crash cymbal for selected accents.'])
box(632,325,178,169,'04','SOLVE + OUTPUT',['Build TCP target planes','Solve each UR10e with Robots inverse kinematics','Report IK errors; pose link meshes','4K: 1680 frames at 24 fps, moving close-ups + orbit','Measured shots trigger fireworks. Mux audio; fade 65-70 s.'])
for x in [209,409,609]:arrow(x,410,x+23,410)
text(32,293,'LOOP: update playback -> recompute clock -> swing / press -> solve -> display',11,teal,'Helvetica-Bold')
text(32,257,'DESIGN INTENT',11,teal,'Helvetica-Bold')
intent=('Four robot arms reinterpret the hand and foot roles of a drummer in the opening of Weather Report\'s Birdland: hi-hat strokes, flat snare side-stick clicks, a linked kick beater and a hi-hat pedal. Chart-guided audio events drive the internally referenced Grasshopper motion, while the reusable MIDI variant embeds imported note data and maps tempo and velocity to the same arms. The 4K film alternates an orbit with instrument close-ups; measured ensemble attacks trigger fireworks. These presentation effects emphasize the musical structure, with original audio and a fade from 1:05 to 1:10.')
paragraph(32,237,intent,778,11,white,16)
text(32,137,'VALIDATION + BOUNDARIES',11,teal,'Helvetica-Bold')
paragraph(32,119,'Birdland motion has been sampled across 1800 instants; the MIDI demo across 217. This is an inverse-kinematics visualization, not a controller-ready program. Continuous collisions, joint speeds, accelerations, contact forces and physical synchronization require validation before execution.',778,10,muted,14)
text(32,45,'DELIVERABLES:  MP4 with original audio  /  Internally referenced GH  /  This diagram + intent',9,white)
text(32,27,'Audio: Weather Report official channel (SvhmaNlLgRM), 00:00-01:10. Chart: Pedro Marambio / Drumeo.',9,muted)
c.save()
import fitz
doc=fitz.open(p);doc[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(R/'diagram-review.png')
print(p)
