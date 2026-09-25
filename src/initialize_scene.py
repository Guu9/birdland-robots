import clr,System,Rhino,scriptcontext as sc,json,traceback
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=ROOT+'/data'
try:
 clr.AddReference('Grasshopper');clr.AddReference('GH_IO')
 import Grasshopper as GH,GH_IO
 rhdoc=Rhino.RhinoDoc.ActiveDoc;sc.doc=rhdoc
 reader=GH_IO.Serialization.GH_Archive();reader.ReadFromFile(ROOT+'/grasshopper/Birdland-Robots.gh')
 doc=GH.Kernel.GH_Document();reader.ExtractObject(doc,'Definition')
 GH.Instances.DocumentServer.AddDocument(doc);GH.Instances.ActiveCanvas.Document=doc;doc.Enabled=True;GH.Kernel.GH_Document.EnableSolutions=True
 core=[o for o in doc.Objects if o.NickName=='BIRDLAND / AUDIO CLOCK'][0]
 t=[o for o in doc.Objects if o.NickName=='PLAYBACK / 0 to 1'][0]
 for o in doc.Objects:
  if hasattr(o,'Hidden'):o.Hidden=True
 core.ExpireSolution(False);doc.NewSolution(False);sc.doc=rhdoc
 for o in doc.Objects:o.ExpireSolution(False)
 doc.NewSolution(False);sc.doc=rhdoc
 dynamic=sorted([o for o in rhdoc.Objects if o.Attributes.Name and o.Attributes.Name.startswith('Arm ')],key=lambda o:tuple(int(x) for x in [o.Attributes.Name.split()[1],o.Attributes.Name.split()[3]]))
 assert len(dynamic)==49,str(len(dynamic))
 sc.sticky['birdland_extended']={'doc':doc,'core':core,'time':t,'dynamic':[o.Id for o in dynamic]}
 rhdoc.Views.ActiveView.ActiveViewport.DisplayMode=Rhino.Display.DisplayModeDescription.FindByName('Rendered')
 with open(OUT+'/resume-report.json','w') as f:json.dump({'meshes':core.Params.Output[0].VolatileDataCount,'errors':list(core.RuntimeMessages(GH.Kernel.GH_RuntimeMessageLevel.Error))},f)
except:
 with open(OUT+'/resume-report.json','w') as f:f.write(traceback.format_exc())
