"""Verify source fidelity and visible lockup alignment across exported SVGs."""
from pathlib import Path
import base64,hashlib,io,json,re,xml.etree.ElementTree as ET
from PIL import Image
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
R=Path(__file__).resolve().parent.parent
manifest=json.loads((R/'source/homepage-artwork.json').read_text())
original=(R/'illustrations/lemonade-children-day-transparent.webp').read_bytes()
assert hashlib.sha256(original).hexdigest()==manifest['sha256']
a=Image.open(io.BytesIO(original)).convert('RGBA')
b=Image.open(R/'illustrations/lemonade-children-day-transparent.png').convert('RGBA')
assert a.size==b.size==(1152,1152) and a.tobytes()==b.tobytes()
assert not any((R/p).exists() for p in ['illustrations/market-watercolor.png','illustrations/merchant-watercolor.png','concepts/open-markets-identity.png'])
master=json.loads((R/'source/identity-paths.json').read_text())
mark=master['symbol']['path']
svg_ns='{http://www.w3.org/2000/svg}'
allowed={hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['illustrations/lemonade-children-day-transparent.png','illustrations/podcast-watercolor.png']}
lockups=0;placements=0
for f in R.rglob('*.svg'):
 root=ET.parse(f).getroot();current_badge=None;block=[]
 for el in root.iter():
  if el.tag==svg_ns+'path' and el.get('d')==mark:
   lockups+=1
  if el.tag==svg_ns+'image':
   href=el.get('{http://www.w3.org/1999/xlink}href',el.get('href',''))
   if href.startswith('data:'):
    raw=base64.b64decode(href.split(',',1)[1]);assert hashlib.sha256(raw).hexdigest() in allowed,(f,'unexpected embedded artwork')
    is_original=hashlib.sha256(raw).hexdigest()==hashlib.sha256((R/'illustrations/lemonade-children-day-transparent.png').read_bytes()).hexdigest()
   else:is_original='lemonade-children-day-transparent' in href
   if is_original:
    x,y,w,h=[float(el.get(k,'0')) for k in ['x','y','width','height']]
    assert w==h and el.get('preserveAspectRatio')=='xMidYMid meet',f
    assert x>=0 and y>=0 and x+w<=float(root.get('width')) and y+h<=float(root.get('height')),(f,'cropped artwork')
    placements+=1
for logo in (R/'logos/svg').glob('*.svg'):
 paths={el.get('d') for el in ET.parse(logo).iter(svg_ns+'path')}
 required={mark}
 if 'horizontal' in logo.name or 'stacked' in logo.name:
  required.update([master['name']['path'],master['foundation']['path']])
 assert paths==required,logo
out={'original_sha256':manifest['sha256'],'original_webp_unchanged':True,'png_decoded_pixels_identical':True,'rejected_artwork_absent':True,'canonical_mark_instances':lockups,'uncropped_square_placements':placements,'embedded_artwork_allowlist':'pass'}
(R/'source/consistency.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
