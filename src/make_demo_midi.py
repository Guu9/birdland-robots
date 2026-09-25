from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
def vlq(v):
 out=[v&127];v>>=7
 while v:out.insert(0,(v&127)|128);v>>=7
 return bytes(out)
def chunk(events):
 events.sort(key=lambda x:x[0]);last=0;data=b''
 for tick,msg in events:data+=vlq(tick-last)+msg;last=tick
 data+=b'\0\xff\x2f\0';return b'MTrk'+struct.pack('>I',len(data))+data
meta=[(0,b'\xff\x51\x03\x07\xa1\x20'),(3840,b'\xff\x51\x03\x09\x27\xc0'),(7680,b'\xff\x01\0')]
notes=[]
for eighth in range(32):
 tick=eighth*240
 roles=[(42 if eighth%8!=7 else 46,60 if eighth%2 else 88)]
 if eighth%8 in (0,4):roles.append((36,108))
 if eighth%8 in (2,6):roles.append((37 if eighth<16 else 38,72 if eighth<16 else 112))
 if eighth in (16,24):roles.append((49,118))
 if eighth%8==0:roles.append((44,65))
 for note,vel in roles:notes.extend([(tick,bytes([0x99,note,vel])),(tick+90,bytes([0x89,note,0]))])
data=b'MThd'+struct.pack('>IHHH',6,1,2,480)+chunk(meta)+chunk(notes)
(ROOT/'examples/demo-drums.mid').write_bytes(data)
