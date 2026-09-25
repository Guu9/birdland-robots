import math,json
state=json.loads(str(articulation));index=int(arm_index)
hits=[float(v.Value if hasattr(v,'Value') else v) for v in events]
distance=min([abs(float(seconds)-v) for v in hits]+[1.0])
phase=min(1.0,distance/(.115 if index<2 else .16))
rebound=.5-.5*math.cos(math.pi*phase)
strength=state['strengths'][index]
lift=(48.0 if index<2 else 8.0 if index==3 else 28.0)*rebound*strength
if index==3 and state['midi']:lift=8.0 if state['opened'] else 0.0
