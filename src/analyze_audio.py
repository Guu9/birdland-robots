from pathlib import Path
import numpy as np,soundfile as sf,json
from scipy.signal import stft,find_peaks
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'assets/audio';O=ROOT/'data'
features={}
for name,path,bands in [('drums',R/'analysis/htdemucs/opening-75/drums.wav',[(35,160),(160,2200),(5500,16000)]),('mix',R/'opening-75.wav',[(100,5000)])]:
 y,sr=sf.read(path);y=y.mean(axis=1);freq,t,z=stft(y,sr,nperseg=1024,noverlap=896);amp=abs(z)
 for i,(lo,hi) in enumerate(bands):
  e=gaussian_filter1d(np.sqrt(np.mean(amp[(freq>=lo)&(freq<hi)]**2,axis=0)),.8)
  flux=np.maximum(e-np.roll(e,3),0);flux[:3]=0
  region=(t>=42.5)&(t<=55.5)
  features[name+str(i)]=flux/(np.quantile(flux[region],.99)+1e-9)
score=.4*features['drums0']+.4*features['drums1']+.2*features['mix0']
peaks,props=find_peaks(score,distance=int(.24/(t[1]-t[0])),prominence=.12,height=.20)
selected=[]
for p in peaks:
 if not 42.75<t[p]<55.5:continue
 # Return to beginning of energy rise, rather than the later amplitude maximum.
 k=p
 while k>p-12 and score[k-1]>.15*score[p]:k-=1
 selected.append({'time':round(float(t[k]),4),'strength':round(float(score[p]),3),'frame':round(float(t[k])*24)})
# Keep the pronounced ensemble accents, not every snare flourish.
threshold=max(x['strength'] for x in selected)*.16
shots=[x for x in selected if x['strength']>=threshold]
e=json.loads((ROOT/'data/birdland-events.json').read_text())['events']
firsthat=e['hat'][0];firstkick=e['kick'][0];secondkick=e['kick'][1];firstrim=e['rim'][0]
# Cuts lead the measured impact, allowing the viewer to see the stick/beater approach.
cuts=[(0,'orbit'),(firstkick-.65,'kick'),(firsthat-.10,'hat'),(secondkick-.45,'kick'),(secondkick+.65,'rim'),(24.25,'orbit'),(28.15,'rim'),(30.5,'orbit'),(e['kick'][2]-.40,'kick'),(e['kick'][3]+.70,'orbit'),(34.2,'hat'),(37.15,'orbit'),(40.75,'rim'),(42.65,'orbit'),(45.65,'snare'),(47.05,'orbit'),(49.40,'kick'),(50.50,'orbit'),(55.5,'hat'),(58.25,'orbit'),(60.8,'snare'),(63.35,'orbit'),(70,'end')]
report={'shots':shots,'cuts':[{'start':round(a,4),'view':b} for a,b in cuts],'first_entries':{'hat':firsthat,'kick':firstkick,'second_kick':secondkick,'rim':firstrim},'method':'Weighted positive spectral-energy rise: separated drum low band (40%), drum mid band (40%), original mix (20%). Strong local peaks within 42.75–55.5 s; backtracked to onset. Bursts start on nearest 24 fps frame. Instrument close-ups anticipate existing chart-guided drum events.','fade':[65,70],'fps':24,'resolution':[3840,2160]}
(O/'edit-analysis.json').write_text(json.dumps(report,indent=2))
fig,ax=plt.subplots(figsize=(16,4));ax.plot(t,score,lw=1,color='#159aaa');ax.set_xlim(41.5,56);ax.set_xlabel('Seconds from original recording start');ax.set_ylabel('Weighted onset strength');ax.set_title('Birdland: fireworks follow measured ensemble attacks')
for x in shots:ax.axvline(x['time'],color='#e08b25',alpha=.7);ax.text(x['time'],x['strength']+.05,str(x['time']),rotation=90,fontsize=8)
ax.grid(alpha=.2);fig.tight_layout();fig.savefig(O/'shot-analysis.png',dpi=150)
print(json.dumps(report,indent=2))
