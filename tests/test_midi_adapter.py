import unittest,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from midi_adapter import parse_midi,parse_mapping

def vlq(v):
 out=[v&127];v>>=7
 while v:out.insert(0,(v&127)|128);v>>=7
 return bytes(out)
def track(events):
 data=b''.join(vlq(dt)+e for dt,e in events)+b'\0\xff\x2f\0'
 return b'MTrk'+struct.pack('>I',len(data))+data
def smf(tracks,division=480,fmt=None):
 return b'MThd'+struct.pack('>IHHH',6,(0 if len(tracks)==1 else 1) if fmt is None else fmt,len(tracks),division)+b''.join(tracks)

class AdapterTests(unittest.TestCase):
 def test_tempo_map_across_tracks_and_running_status(self):
  t=track([(0,b'\xff\x51\x03\x07\xa1\x20'),(480,b'\xff\x51\x03\x0f\x42\x40')])
  notes=track([(0,b'\x99\x24\x64'),(480,b'\x26\x5a'),(480,b'\x2a\x50'),(0,b'\x2a\0')])
  d=parse_midi(smf([t,notes]));self.assertEqual(d['events']['kick'],[0.]);self.assertEqual(d['events']['heavy'],[.5]);self.assertEqual(d['events']['hat'],[1.5]);self.assertEqual(d['note_count'],3)
 def test_start_and_speed(self):
  d=parse_midi(smf([track([(0,b'\x99\x24\x64'),(480,b'\x99\x26\x50'),(480,b'\x99\x24\x64')])]),start=.5,speed=2)
  self.assertEqual(d['events']['kick'],[.25]);self.assertEqual(d['events']['heavy'],[0.])
 def test_smpte(self):
  d=parse_midi(smf([track([(250,b'\x99\x24\x64')])],division=(231<<8)|10))
  self.assertEqual(d['events']['kick'],[1.])
 def test_channel_fallback_and_ambiguity(self):
  d=parse_midi(smf([track([(0,b'\x92\x24\x64')])]))
  self.assertEqual(d['channels'],[3]);self.assertTrue(d['warnings'])
  data=smf([track([(0,b'\x92\x24\x64'),(0,b'\x93\x26\x64')])])
  with self.assertRaises(ValueError):parse_midi(data)
  self.assertEqual(parse_midi(data,channel=4)['channels'],[4])
 def test_unknown_notes_toms_and_remapping(self):
  data=smf([track([(0,b'\x99\x29\x64'),(240,b'\x99\x3c\x50')])])
  d=parse_midi(data);self.assertEqual(d['events']['heavy'],[0.]);self.assertEqual(len(d['warnings']),2)
  d=parse_midi(data,mapping=parse_mapping('kick=60'));self.assertEqual(d['events']['kick'],[.25])
 def test_meta_sysex_and_velocity_zero(self):
  data=smf([track([(0,b'\xff\x03\x04test'),(0,b'\xf0\x03\x01\x02\xf7'),(0,b'\x99\x24\x64'),(480,b'\x99\x24\0')])])
  self.assertEqual(parse_midi(data)['note_count'],1)
 def test_rejects_malformed_and_type2(self):
  with self.assertRaises(ValueError):parse_midi(b'garbage')
  with self.assertRaises(ValueError):parse_midi(smf([track([(0,b'\x99\x24\x64')])],fmt=2))
  with self.assertRaises(ValueError):parse_midi(smf([track([(0,b'\x99\x24\x64')])])[:-2])
  with self.assertRaises(ValueError):parse_mapping('kick=38')
if __name__=='__main__':unittest.main()
