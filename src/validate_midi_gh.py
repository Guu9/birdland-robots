import clr,System,Rhino,scriptcontext as sc,json,os,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
 import Grasshopper as GH,GH_IO
 rhdoc=Rhino.RhinoDoc.ActiveDoc;d=sc.sticky['midi_drums'];doc=d['doc'];core=d['core'];adapter=d['adapter'];errors=[]
 GH.Instances.ActiveCanvas.Document=doc
 for n in range(217):
  d['time'].SetSliderValue(System.Decimal(n/216.0));d['time'].ExpireSolution(False);doc.NewSolution(False);sc.doc=rhdoc
  ee=[str(x) for x in core.Params.Output[2].VolatileData.AllData(True)]
  if ee:errors.append({'frame':n,'errors':ee})
 # Exercise file import and the scheduled internalization callback.
 d['file'].UserText=ROOT+'/examples/demo-drums.mid';d['file'].ExpireSolution(False);doc.NewSolution(False);sc.doc=rhdoc
 with open(ROOT+'/data/midi-validation.json','w') as f:json.dump({'samples':217,'armPoses':868,'ikErrors':errors,'meshes':core.Params.Output[0].VolatileDataCount,'coreErrors':list(core.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error)),'importErrors':list(adapter.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))},f,indent=2)
except:
 with open(ROOT+'/data/midi-validation.json','w') as f:f.write(traceback.format_exc())
