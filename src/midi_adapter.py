"""Dependency-free Standard MIDI File parser, compatible with Rhino GhPython (2.7).
SMF 0/1, PPQN tempo maps and SMPTE division. No MIDI playback or hardware I/O.
"""
import struct,bisect,base64
DEFAULT_MAPPING = {'kick':[35,36], 'snare':[38,40], 'rim':[37], 'hat':[42,46],
                   'pedal':[44], 'crash':[49,51,52,53,55,57,59], 'tom':[41,43,45,47,48,50]}

def _byte(data,i):
    v=data[i]
    return v if isinstance(v,int) else ord(v)

def _vlq(data,pos,end):
    value=0
    for unused in range(4):
        if pos>=end:raise ValueError('Truncated variable-length MIDI number')
        b=_byte(data,pos);pos+=1;value=(value<<7)|(b&127)
        if b<128:return value,pos
    raise ValueError('MIDI variable-length number exceeds four bytes')

def parse_mapping(text):
    result=dict((k,list(v)) for k,v in DEFAULT_MAPPING.items())
    if text and str(text).strip():
        for line in str(text).splitlines():
            line=line.split('#',1)[0].strip()
            if not line:continue
            if '=' not in line:raise ValueError('Mapping lines must be role=note,note')
            role,notes=line.split('=',1);role=role.strip().lower()
            if role not in result:raise ValueError('Unknown role: '+role)
            result[role]=[int(n.strip()) for n in notes.split(',') if n.strip()]
    seen={}
    for role,notes in result.items():
        for note in notes:
            if not 0<=note<=127:raise ValueError('MIDI notes must be 0..127')
            if note in seen:raise ValueError('Note %s appears in both %s and %s'%(note,seen[note],role))
            seen[note]=role
    return result

def parse_midi(data,channel=0,mapping=None,start=0.0,speed=1.0,tom_policy='snare'):
    # channel: 0 auto (channel 10 preferred), 1..16 explicit, -1 all.
    if not data or data[:4]!=b'MThd':raise ValueError('Expected a Standard MIDI .mid/.midi file (MThd header)')
    if len(data)<14:raise ValueError('Truncated MIDI header')
    size=struct.unpack('>I',data[4:8])[0]
    if size<6 or 8+size>len(data):raise ValueError('Invalid MIDI header length')
    fmt,ntracks,division=struct.unpack('>HHH',data[8:14])
    if fmt not in (0,1):raise ValueError('MIDI type 2 contains independent songs; export as type 0 or 1 first')
    if not ntracks or (fmt==0 and ntracks!=1):raise ValueError('Invalid MIDI track count')
    if not division:raise ValueError('MIDI time division cannot be zero')
    speed=float(speed);start=float(start);channel=int(channel)
    if speed<=0 or start<0:raise ValueError('Speed must be positive and start must be non-negative')
    if channel not in range(-1,17):raise ValueError('Channel must be -1 (all), 0 (auto), or 1..16')
    mapping=mapping or DEFAULT_MAPPING
    lookup=dict((n,k) for k,notes in mapping.items() for n in notes)
    pos=8+size;notes=[];tempos=[(0,-1,500000)];end_tick=0;order=0
    for track in range(ntracks):
        if pos+8>len(data) or data[pos:pos+4]!=b'MTrk':raise ValueError('Missing MIDI track %s'%track)
        length=struct.unpack('>I',data[pos+4:pos+8])[0];pos+=8;end=pos+length
        if end>len(data):raise ValueError('Truncated MIDI track %s'%track)
        tick=0;running=None
        while pos<end:
            delta,pos=_vlq(data,pos,end);tick+=delta;end_tick=max(end_tick,tick)
            if pos>=end:raise ValueError('Missing MIDI event status')
            b=_byte(data,pos)
            if b>=128:status=b;pos+=1
            elif running is not None:status=running
            else:raise ValueError('Running status without a preceding channel message')
            if status==255:
                running=None
                if pos>=end:raise ValueError('Truncated meta event')
                kind=_byte(data,pos);pos+=1;length,pos=_vlq(data,pos,end)
                if pos+length>end:raise ValueError('Truncated meta payload')
                if kind==81:
                    if length!=3:raise ValueError('Tempo meta event must have three bytes')
                    tempo=(_byte(data,pos)<<16)|(_byte(data,pos+1)<<8)|_byte(data,pos+2)
                    if tempo<=0:raise ValueError('MIDI tempo must be positive')
                    tempos.append((tick,order,tempo));order+=1
                pos+=length
                if kind==47:break
            elif status in (240,247):
                running=None;length,pos=_vlq(data,pos,end)
                if pos+length>end:raise ValueError('Truncated system-exclusive payload')
                pos+=length
            elif 128<=status<=239:
                running=status;kind=status&240;ch=status&15;count=1 if kind in (192,208) else 2
                if pos+count>end:raise ValueError('Truncated channel event')
                values=[_byte(data,pos+i) for i in range(count)];pos+=count
                if any(v>=128 for v in values):raise ValueError('Invalid MIDI data byte')
                if kind==144 and values[1]>0:notes.append((tick,track,ch,values[0],values[1]))
            else:raise ValueError('Unsupported status byte in Standard MIDI file: %s'%status)
        pos=end
    warnings=[];tempos.sort();tempo_ticks=[];tempo_seconds=[];tempo_values=[]
    if division&32768:
        code=(division>>8)-256;tpf=division&255
        if code not in (-24,-25,-29,-30) or not tpf:raise ValueError('Unsupported SMPTE time division')
        fps=29.97 if code==-29 else float(-code)
        def seconds(tick):return tick/(fps*tpf)
        warnings.append('SMPTE timing: tempo messages do not affect event seconds.')
    else:
        last_tick=0;elapsed=0.0;tempo=500000
        for tick,unused,newtempo in tempos:
            elapsed+=(tick-last_tick)*tempo/(division*1000000.0)
            if tempo_ticks and tick==tempo_ticks[-1]:tempo_values[-1]=newtempo
            else:tempo_ticks.append(tick);tempo_seconds.append(elapsed);tempo_values.append(newtempo)
            tempo=newtempo;last_tick=tick
        def seconds(tick):
            i=bisect.bisect_right(tempo_ticks,tick)-1
            return tempo_seconds[i]+(tick-tempo_ticks[i])*tempo_values[i]/(division*1000000.0)
    present=sorted(set(n[2] for n in notes));mapped_channels=sorted(set(n[2] for n in notes if n[3] in lookup))
    if channel==0:
        if 9 in present:selected=[9]
        elif len(mapped_channels)==1:selected=mapped_channels;warnings.append('No channel 10: using the sole mapped-note channel %s.'%(selected[0]+1))
        elif not mapped_channels:raise ValueError('No mapped drum notes found')
        else:raise ValueError('Several non-GM channels contain mapped notes. Choose the drum channel (1..16), or -1 for all.')
    else:selected=present if channel==-1 else [channel-1]
    events=dict((k,[]) for k in ['kick','snare','rim','hat','pedal','heavy','crash','open_hat','tom'])
    velocities=[];ignored={};tom_count=0
    for tick,track,ch,note,velocity in notes:
        if ch not in selected:continue
        absolute=seconds(tick)
        if absolute<start:continue
        when=(absolute-start)/speed;role=lookup.get(note)
        if not role:ignored[note]=ignored.get(note,0)+1;continue
        if role=='tom':
            tom_count+=1;events['tom'].append(when)
            if tom_policy=='ignore':continue
            if tom_policy!='snare':raise ValueError('Tom policy must be snare or ignore')
            role='snare'
        velocities.append({'time':when,'note':note,'velocity':velocity,'role':role,'channel':ch+1,'track':track})
        events[role].append(when)
        if role=='rim':events['snare'].append(when)
        if role=='snare':events['heavy'].append(when)
        if role=='crash':events['hat'].append(when)
        if role=='hat' and note==46:events['open_hat'].append(when)
    for key in events:events[key]=sorted(set(round(x,6) for x in events[key]))
    if not velocities:raise ValueError('No mapped drum hits remain for the selected channel/start')
    if ignored:warnings.append('Unmapped note numbers skipped: '+', '.join('%s (%s)'%(k,ignored[k]) for k in sorted(ignored)))
    if tom_count:warnings.append('%s tom hits %s; this four-arm scene has no independent tom choreography.'%(tom_count,'routed to snare' if tom_policy=='snare' else 'ignored'))
    duration=max((seconds(end_tick)-start)/speed,max(x['time'] for x in velocities)+.5)
    return {'events':events,'velocities':velocities,'duration':duration,'channels':[v+1 for v in selected],
            'format':fmt,'tracks':ntracks,'warnings':warnings,'tempo_changes':len(tempos)-1,
            'note_count':len(velocities),'source':'Standard MIDI file','mapping':mapping}
