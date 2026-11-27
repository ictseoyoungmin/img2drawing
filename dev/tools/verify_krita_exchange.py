#!/usr/bin/env python3
"""Optional real-Krita ORA interoperability probe; synthetic data only.

Requires the candidate img2drawing package plus Krita's installed ``kritarunner``.
Example: python verify_krita_exchange.py --output-dir /tmp/ora-check
An executable wrapper may be supplied with --kritarunner for a private install.

Creates no user artwork and changes no native checkpoint or input ORA after export.
Uses Krita's real document engine and Python API, not GUI automation. Reports the
observed 127->126 ORA opacity precision limit separately; KRA must remain exact.
"""
from pathlib import Path
import argparse, os, shutil, subprocess, sys, tempfile

FIXTURE = r'''
from pathlib import Path
from dataclasses import asdict
import json, hashlib
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import InkAction, InkArea, InkElement, apply_ink_actions, dot_screentone, fineliner

root=Path(__file__).resolve().parent
probe=root/'probe'
probe.mkdir(exist_ok=True)
ref=probe/'reference.png'
Image.new('RGB',(256,192),'white').save(ref)
s=DrawingSession.create(subject=ref,output_dir=probe/'native',render_profile=RenderProfile.mixed_media(256,192,supersample=2))
o=s.observe({'purpose':'Krita import of explicit synthetic nested groups, hidden content, order, opacity, Korean/XML-sensitive names'})
s.enable_layers(name='Paper & <base>')
s.create_layer('outer','외부 그룹 & <outer> "A"',kind='group')
s.create_layer('inner','Inner <isolated>',kind='group',parent_id='outer')
s.create_layer('black','Ink 선화 & black',parent_id='inner')
s.create_layer('white','White highlights',parent_id='inner')
s.create_layer('tone','Tone 25%',parent_id='outer')
s.create_layer('hidden','Hidden 원본 <keep>',parent_id='outer')
s.create_layer('guide','Pencil guide',parent_id='outer')
s.update_layer('outer',opacity=.8)
s.update_layer('inner',opacity=.5)
s.update_layer('hidden',visible=False)
s.draw([(18,166),(46,151),(82,171),(118,153),(156,170),(210,151)],stroke_id='pencil',layer_id='guide',observation_id=o)
def rect(x,y,w,h): return ((x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y))
def add(eid,mark,lid):
 e=InkElement(eid,mark,'test','explicit fixture',0)
 apply_ink_actions(s,[InkAction('add-'+eid,'ink.add',eid,e,o,'explicit probe geometry','test export interoperability')],layer_id=lid)
add('blackshape',InkArea(rect(20,20,126,105)),'black')
add('whitecut',InkArea(rect(72,56,92,43),paint='white'),'white')
add('screen',dot_screentone(rect(167,28,65,100),coverage=.25,pitch=6,phase_origin=(.4,.7)),'tone')
add('hiddenmark',InkArea(rect(181,9,59,16)),'hidden')
add('line',fineliner(((15,137),(235,137)),width=2).resolve(),'guide')
s.update_layer('black',locked=True)
final=s.render_final(probe/'native-final.png')
receipt=s.export_openraster(probe/'baseline.ora')
s.export_layer_pngs(probe/'layers')
result={'version':__import__('importlib.metadata').metadata.version('img2drawing'),'canonical_pixel_sha256':final.pixel_sha256,'manifest':receipt.manifest,'checkpoint_sha256':hashlib.sha256(s.checkpoint_path.read_bytes()).hexdigest(),'layer_document':s.layer_document.to_dict()}
(probe/'expected.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'ora':str(receipt.path),'canonical_pixel_sha256':final.pixel_sha256,'manifest':str(receipt.manifest_path)},ensure_ascii=False))

'''

ENGINE = r'''
from pathlib import Path
import json,traceback,hashlib
from krita import Krita,InfoObject
ROOT=Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def flatten_nodes(node):
 result=[]
 for child in node.childNodes():
  result.append(child);result.extend(flatten_nodes(child))
 return result
def tree(node,w,h):
 result=[]
 for n in node.childNodes():
  b=n.bounds()
  row={'name':n.name(),'type':n.type(),'opacity':n.opacity(),'visible':n.visible(),'locked':n.locked(),'bounds':[b.x(),b.y(),b.width(),b.height()]}
  if n.type()=='grouplayer':
   row['pass_through']=n.passThroughMode();row['children']=tree(n,w,h)
  else:
   raw=bytes(n.pixelData(0,0,w,h));row['raw_bgra_sha256']=hashlib.sha256(raw).hexdigest();row['nonzero_alpha_pixels']=sum(x!=0 for x in raw[3::4])
  result.append(row)
 return result
def compare_with_editor_opacity_rounding(expected, actual, path=""):
 differences=[]
 if isinstance(expected,dict):
  assert expected.keys()==actual.keys(),"node fields changed at "+path
  for key in expected: differences.extend(compare_with_editor_opacity_rounding(expected[key],actual[key],path+"/"+key))
 elif isinstance(expected,list):
  assert len(expected)==len(actual),"child count changed at "+path
  for i,(a,b) in enumerate(zip(expected,actual)):differences.extend(compare_with_editor_opacity_rounding(a,b,path+"/"+str(i)))
 elif expected!=actual:
  assert path.endswith("/opacity") and expected==127 and actual==126,(path,expected,actual)
  differences.append({"path":path,"before":expected,"after":actual})
 return differences
def export(doc,path):
 doc.refreshProjection();doc.waitForDone()
 assert doc.exportImage(str(path),InfoObject()),'export failed '+str(path)
 assert path.is_file(),str(path)
def save(doc,path):
 assert doc.saveAs(str(path)),'save failed '+str(path)
 assert path.is_file(),str(path)
def __main__(args):
 report={'engine':'Krita official Python API via kritarunner','version':Krita.instance().version(),'status':'RUNNING'}
 src=ROOT/'probe/baseline.ora';out=ROOT/'probe/validated'
 if args: src=Path(args[0]);out=Path(args[1])
 report['source']=str(src);report['source_sha256_before']=digest(src)
 out.mkdir(parents=True,exist_ok=True)
 try:
  app=Krita.instance();doc=app.openDocument(str(src));assert doc is not None
  doc.setBatchmode(True);doc.waitForDone();w,h=doc.width(),doc.height()
  report['dimensions']=[w,h];report['initial_tree']=tree(doc.rootNode(),w,h)
  export(doc,out/'baseline.png');save(doc,out/'baseline.kra');export(doc,out/'baseline.ora')
  nodes={n.name():n for n in flatten_nodes(doc.rootNode())}
  outer=nodes['외부 그룹 & <outer> "A"'];inner=nodes['Inner <isolated>'];hidden=nodes['Hidden 원본 <keep>'];guide=nodes['Pencil guide']
  assert outer.type()=='grouplayer' and inner.type()=='grouplayer'
  assert not outer.passThroughMode() and not inner.passThroughMode()
  assert outer.opacity()==204 and abs(inner.opacity()-127.5)<=.5
  assert not hidden.visible()
  assert any(bytes(hidden.pixelData(0,0,w,h))[3::4]),'hidden raster content missing'
  assert [n.name() for n in inner.childNodes()]==['Ink 선화 & black','White highlights']
  hidden.setVisible(True);outer.setOpacity(153);inner.setName('Renamed 중첩 그룹 & <edited>');guide.move(guide.position().x()+7,guide.position().y()+3)
  report['edits']=['show hidden paint layer','outer group opacity 204 -> 153','rename nested group','translate guide layer +7,+3']
  export(doc,out/'edited.png');report['edited_tree']=tree(doc.rootNode(),w,h)
  save(doc,out/'edited.kra');export(doc,out/'edited.ora')
  doc.close()
  report['reopened']={}
  for extension in ('kra','ora'):
   restored=app.openDocument(str(out/('edited.'+extension)));assert restored is not None
   restored.setBatchmode(True);restored.waitForDone()
   rt=tree(restored.rootNode(),w,h);report['reopened'][extension]=rt
   export(restored,out/('reopened-'+extension+'.png'))
   if extension=='kra': assert rt==report['edited_tree'],'KRA roundtrip changed layer tree'
   else: report['edited_ora_opacity_drift']=compare_with_editor_opacity_rounding(report['edited_tree'],rt)
   restored.close()
  baseline_doc=app.openDocument(str(out/'baseline.ora'));assert baseline_doc is not None
  baseline_doc.setBatchmode(True);baseline_doc.waitForDone();report['baseline_reopened_tree']=tree(baseline_doc.rootNode(),w,h)
  export(baseline_doc,out/'baseline-reopened.png')
  report['baseline_ora_opacity_drift']=compare_with_editor_opacity_rounding(report['initial_tree'],report['baseline_reopened_tree'])
  baseline_doc.close()
  report['source_sha256_after']=digest(src)
  assert report['source_sha256_after']==report['source_sha256_before']
  report['status']='PASS_WITH_KRITA_ORA_OPACITY_QUANTIZATION' if report['edited_ora_opacity_drift'] or report['baseline_ora_opacity_drift'] else 'PASS'
 except Exception as e:
  report['status']='FAIL';report['error']=str(e);report['traceback']=traceback.format_exc()
 (out/'operations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

'''

MEASURE = r'''
from pathlib import Path
import io,json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
probe=root/'probe';validated=probe/'validated-v3'
ops=json.loads((validated/'operations.json').read_text())
expected=json.loads((probe/'expected.json').read_text())
def pixels(path):return np.array(Image.open(path).convert('RGBA'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def compare(a,b):
 aa,bb=pixels(a),pixels(b);assert aa.shape==bb.shape
 delta=np.abs(aa.astype(np.int16)-bb.astype(np.int16))
 return {'dimensions':[aa.shape[1],aa.shape[0]],'rgba_equal':bool(np.array_equal(aa,bb)),'differing_pixels':int(np.any(delta,axis=2).sum()),'max_channel_error':int(delta.max()),'mean_absolute_channel_error':float(delta.mean()),'a_rgba_sha256':hashlib.sha256(aa.tobytes()).hexdigest(),'b_rgba_sha256':hashlib.sha256(bb.tobytes()).hexdigest()}
def xml_opacities(path):
 with zipfile.ZipFile(path) as z:doc=ET.fromstring(z.read('stack.xml'))
 return [{'name':e.get('name'),'opacity':e.get('opacity'),'tag':e.tag} for e in doc.iter() if e.tag in ('stack','layer')]
def verify_import(stack, rows, archive):
 # ORA order is top-to-bottom; Krita childNodes returns bottom-to-top.
 elements=list(reversed(list(stack)))
 assert len(elements)==len(rows), 'import changed child count'
 imported=[]
 for element,row in zip(elements,rows):
  assert element.get('name')==row['name'], 'import changed name or order'
  assert (element.get('visibility')!='hidden')==row['visible'], 'import changed visibility'
  assert (element.get('edit-locked')=='true')==row['locked'], 'import changed lock'
  assert abs(float(element.get('opacity','1'))*255-row['opacity'])<=.5, 'import changed opacity'
  if element.tag=='stack':
   assert row['type']=='grouplayer' and not row['pass_through'], 'import changed isolation'
   imported.extend(verify_import(element,row['children'],archive))
  else:
   assert row['type']=='paintlayer'
   rgba=np.array(Image.open(io.BytesIO(archive.read(element.get('src')))).convert('RGBA'))
   bgra=rgba[:,:,[2,1,0,3]]
   assert hashlib.sha256(bgra.tobytes()).hexdigest()==row['raw_bgra_sha256'], 'import changed raw paint pixels'
   imported.append({'name':row['name'],'rgba_exact':True,'nonzero_alpha_pixels':row['nonzero_alpha_pixels']})
 return imported
with zipfile.ZipFile(probe/'baseline.ora') as archive:
 xml=ET.fromstring(archive.read('stack.xml'))
 imported=verify_import(xml.find('stack'),ops['initial_tree'],archive)
checks={
 'canonical_to_krita':compare(probe/'native-final.png',validated/'baseline.png'),
 'krita_baseline_to_krita_ora_reopen':compare(validated/'baseline.png',validated/'baseline-reopened.png'),
 'edits_applied':compare(validated/'baseline.png',validated/'edited.png'),
 'edited_kra_reopen':compare(validated/'edited.png',validated/'reopened-kra.png'),
 'edited_ora_reopen':compare(validated/'edited.png',validated/'reopened-ora.png')}
native_unchanged=sha(probe/'native/session.checkpoint.json')==expected['checkpoint_sha256']
sidecar_unchanged=sha(probe/'baseline.checkpoint.json')==expected['manifest']['native_checkpoint']['sha256']
assert native_unchanged and sidecar_unchanged
assert checks['edited_kra_reopen']['rgba_equal']
assert checks['edited_ora_reopen']['max_channel_error']<=1
assert checks['krita_baseline_to_krita_ora_reopen']['max_channel_error']<=1
report={'engine':'Krita '+ops['version']+' official scripting/document engine','interaction':'kritarunner public Python API; GUI interaction NOT_RUN','source_candidate':__import__('importlib.metadata').metadata.version('img2drawing'),'status':ops['status'],'operations':str(validated/'operations.json'),'source_ora_unchanged':ops['source_sha256_before']==ops['source_sha256_after'],'native_checkpoint_unchanged':native_unchanged,'export_checkpoint_unchanged':sidecar_unchanged,'measurements':checks,'imported_paint_pixels':imported,'package_recomposition_measurement':expected['manifest']['recomposition'],'original_xml':xml_opacities(probe/'baseline.ora'),'krita_saved_baseline_xml':xml_opacities(validated/'baseline.ora'),'opacity_drift':{'baseline':ops['baseline_ora_opacity_drift'],'edited':ops['edited_ora_opacity_drift']},'limitation':('The tested Krita '+ops['version']+' ORA re-save/reopen changes group opacity from 127/255 to 126/255. Other tested fields and raw paint pixels remain equal; edited KRA tree and flattened pixels are exact. No compensation is applied to img2drawing export.' if ops['status']=='PASS_WITH_KRITA_ORA_OPACITY_QUANTIZATION' else None)}
assert ops['status'] in ('PASS','PASS_WITH_KRITA_ORA_OPACITY_QUANTIZATION'),ops
(root/'synthetic_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'status':report['status'],'engine':report['engine'],'report':str(root/'synthetic_report.json'),'edited_kra_exact':checks['edited_kra_reopen']['rgba_equal'],'edited_ora_max_channel_error':checks['edited_ora_reopen']['max_channel_error']},ensure_ascii=False))

'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kritarunner',default=shutil.which('kritarunner'))
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    if not args.kritarunner: parser.error('Krita kritarunner is required; this probe never substitutes a fake editor')
    out=args.output_dir or Path(tempfile.mkdtemp(prefix='img2drawing-krita-'))
    out=out.resolve()
    if out.exists() and any(out.iterdir()): parser.error('output directory must be empty')
    out.mkdir(parents=True,exist_ok=True)
    for name,source in [('prepare_probe.py',FIXTURE),('_img2drawing_ora_probe.py',ENGINE),('measure_probe.py',MEASURE)]:
        (out/name).write_text(source,encoding='utf-8')
    subprocess.run([sys.executable,str(out/'prepare_probe.py')],check=True)
    env=os.environ.copy()
    env['PYTHONPATH']=str(out)+os.pathsep+env.get('PYTHONPATH','')
    with (out/'krita.log').open('w') as log:
        subprocess.run([args.kritarunner,'-s','_img2drawing_ora_probe',str(out/'probe/baseline.ora'),str(out/'probe/validated-v3')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,check=True)
    subprocess.run([sys.executable,str(out/'measure_probe.py')],check=True)

if __name__=='__main__': main()
