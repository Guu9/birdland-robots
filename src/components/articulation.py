import json, math
state = json.loads(str(event_data))
def near(values):return min([abs(float(seconds)-v) for v in values]+[100.0])
def ease(v):
 v=max(0.0,min(1.0,v));return v*v*(3-2*v)
rim = ease((near(state['heavy'])-.16)/.24)
crash = ease((.42-near(state['crash']))/.26)
hits=state.get('velocities',[])
history=[v for v in hits if v['time']<=seconds and (v['role']=='pedal' or v['note'] in [42,46])]
opened=bool(history and max(history,key=lambda v:v['time'])['note']==46)
strengths=[]
for roles in [['snare','rim'],['hat','crash'],['kick'],['pedal']]:
 selected=[v for v in hits if v['role'] in roles]
 velocity=min(selected,key=lambda v:abs(seconds-v['time']))['velocity'] if selected else 64
 strengths.append(.45+.55*velocity/127.0 if state['midi'] else 1.0)
opening=4.0 if opened else 0.0
if not state['midi']:
 opening=4*(.5-.5*math.cos(math.pi*min(1.0,near(state['pedal'])/.16)))
articulation=json.dumps(dict(rim=rim,crash=crash,opening=opening,opened=opened,strengths=strengths,midi=state['midi']))
