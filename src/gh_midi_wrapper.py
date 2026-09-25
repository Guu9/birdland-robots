# Appended to midi_adapter.py inside the GhPython component.
import json,os,Grasshopper as GH
from System import Guid
result_json=None;duration=0.0;snare_times='';hat_times='';kick_times='';pedal_times='';report=''
try:
    requested=str(file_path or '').strip().strip('"')
    raw=open(requested,'rb').read() if requested else base64.b64decode(str(embedded or '').strip())
    result=parse_midi(raw,channel=int(channel),mapping=parse_mapping(note_map),start=float(start_seconds),speed=float(speed),tom_policy=str(tom_policy or 'snare').strip())
    result_json=json.dumps(result);duration=result['duration']
    def csv(name):return ','.join('{:.6f}'.format(v) for v in result['events'][name])
    snare_times=csv('snare');hat_times=csv('hat');kick_times=csv('kick');pedal_times=csv('pedal')
    report='MIDI: {0} hits / {1:.3f} seconds\nChannels: {2}; tempo changes: {3}\n'.format(result['note_count'],duration,result['channels'],result['tempo_changes'])+'\n'.join(result['warnings'])
    report+='\nVelocities scale stroke heights; MIDI itself produces no audio.'
    if requested:
        encoded=base64.b64encode(raw)
        if not isinstance(encoded,str):encoded=encoded.decode('ascii')
        document=ghenv.Component.OnPingDocument()
        cache=next(o for o in document.Objects if o.NickName=='MIDI / EMBEDDED BYTES')
        filepath=next(o for o in document.Objects if o.NickName=='MIDI / FILE TO IMPORT')
        def cache_import(doc):
            cache.UserText=encoded;cache.ExpireSolution(False)
            filepath.UserText='';filepath.ExpireSolution(False)
        document.ScheduleSolution(1,GH.Kernel.GH_Document.GH_ScheduleDelegate(cache_import))
        report+='\nImported bytes are being embedded. Save the GH file to retain them.'
    else:report+='\nUsing embedded MIDI bytes: no external MIDI file needed.'
except Exception as error:
    report='MIDI IMPORT ERROR: '+str(error)
    ghenv.Component.AddRuntimeMessage(GH.Kernel.GH_RuntimeMessageLevel.Error,str(error))
