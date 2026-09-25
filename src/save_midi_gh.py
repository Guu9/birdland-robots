import System,Rhino,scriptcontext as sc,json,os,traceback
import Grasshopper as GH,GH_IO
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
 d=sc.sticky['midi_drums'];doc=d['doc'];rhdoc=Rhino.RhinoDoc.ActiveDoc
 assert not d['file'].UserText.strip(),'File import was not internalized'
 assert d['cache'].UserText.startswith('TVRo'),'Missing MIDI bytes'
 d['time'].SetSliderValue(System.Decimal(.2));d['time'].ExpireSolution(False);doc.NewSolution(False);sc.doc=rhdoc
 arc=GH_IO.Serialization.GH_Archive();arc.AppendObject(doc,'Definition');arc.WriteToFile(doc.FilePath,True,False)
 # Reload from the saved archive. The file-path field is empty.
 reader=GH_IO.Serialization.GH_Archive();reader.ReadFromFile(doc.FilePath);fresh=GH.Kernel.GH_Document();reader.ExtractObject(fresh,'Definition')
 fresh.GetType().GetMethod('SetDocumentID',System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.Public|System.Reflection.BindingFlags.NonPublic).Invoke(fresh,System.Array[System.Object]([System.Guid.NewGuid()]))
 GH.Instances.DocumentServer.AddDocument(fresh);GH.Instances.ActiveCanvas.Document=fresh;fresh.Enabled=True
 for o in fresh.Objects:o.ExpireSolution(False)
 fresh.NewSolution(False);sc.doc=rhdoc
 core=next(o for o in fresh.Objects if o.NickName=='MIDI / FOUR ARM SOLVER')
 imp=next(o for o in fresh.Objects if o.NickName=='MIDI IMPORT + INTERNALIZE')
 report={'filePathCleared':True,'embeddedByteCharacters':len(d['cache'].UserText),'reloadedMeshes':core.Params.Output[0].VolatileDataCount,'coreErrors':list(core.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)),'importErrors':list(imp.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))}
 for o in fresh.Objects:
  if hasattr(o,'Hidden'):o.Hidden=True
 for o in doc.Objects:
  if hasattr(o,'Hidden'):o.Hidden=True
 with open(ROOT+'/data/midi-reload.json','w') as f:json.dump(report,f,indent=2)
except:
 with open(ROOT+'/data/midi-reload.json','w') as f:f.write(traceback.format_exc())
