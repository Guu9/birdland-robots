from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders/director4k';OUT.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(3840,2160),(0,0,0,0));d=ImageDraw.Draw(im)
f='/System/Library/Fonts/Supplemental/Arial.ttf';b='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def rect(box,color):d.rectangle(tuple(v*2 for v in box),fill=color)
def text(x,y,s,size,color,bold=False):d.text((x*2,y*2),s,font=ImageFont.truetype(b if bold else f,size*2),fill=color)
rect((0,0,1920,76),(3,9,16,238));rect((0,1028,1920,1080),(3,9,16,238));rect((48,22,53,54),(26,210,213,255))
text(72,22,'BIRDLAND / WEATHER REPORT',27,(240,245,246,255),True)
text(1480,27,'DIRECTOR EDIT / 4K UHD / 24 FPS',17,(97,208,214,255))
text(48,1044,'FOUR ARMS / ONE GROOVE',17,(240,245,246,255),True)
text(1355,1044,'RHINO + GRASSHOPPER + ROBOTS',16,(97,208,214,255))
im.save(OUT/'overlay.png')
