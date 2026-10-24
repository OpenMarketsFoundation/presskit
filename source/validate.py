from pathlib import Path
import sys,json,re,hashlib,zipfile,subprocess,xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader
import numpy as np
import imageio_ffmpeg

R=Path(__file__).resolve().parent.parent
results={}
for f in R.rglob('*.md'):
    s=f.read_text()
    assert '/Users/' not in s and '/var/folders/' not in s,f
    for href in re.findall(r'\]\(([^)]+)\)',s)+re.findall(r'src="([^"]+)"',s):
        if not href.startswith(('http://','https://','#')):assert (f.parent/href).exists(),(f,href)
results['local_document_links']='pass'
ns='{http://www.w3.org/2000/svg}'
for f in R.rglob('*.svg'):
    tree=ET.parse(f);root=tree.getroot()
    for el in root.iter():
        for k,v in el.attrib.items():
            if k.endswith('href') and not v.startswith(('data:','#')):assert (f.parent/v).exists(),(f,v)
    if f.parent==R/'logos/svg':
        assert not list(root.iter(ns+'image')),f
        assert not list(root.iter(ns+'text')),f
    if f.name.endswith('-editable.svg') and f.name!='hero-editable.svg':assert list(root.iter(ns+'text')),f
results['svg_structure_and_linked_art']='pass'
for variant in ['badge','symbol','stacked','horizontal']:
    for size in [512,2048]:
        ref=None
        for color in ['ink','black','white']:
            f=R/f'logos/png/omf-{variant}-{color}-{size}.png'
            im=Image.open(f);assert im.mode=='RGBA',f;assert im.width==size,f
            alpha=np.array(im.getchannel('A'));assert alpha.min()==0 and alpha.max()==255,f
            assert alpha[0,0]==0 and alpha[-1,-1]==0,f
            if ref is not None:assert np.array_equal(ref,alpha),f
            ref=alpha
results['transparent_pngs_and_variant_geometry']='pass'
dims={'podcast/open-markets-podcast-cover.png':(3000,3000),'social/square.png':(1080,1080),'social/story.png':(1080,1920),'social/link-preview.png':(1200,630),'website/hero.png':(1152,1152),'media/podcast-title.png':(1920,1080),'templates/presentation-title.png':(1920,1080)}
for f,size in dims.items():assert Image.open(R/f).size==size,f
for n in [16,32,48,180,512]:assert Image.open(R/f'website/icon-{n}.png').size==(n,n)
results['export_dimensions']='pass'
for f in (R/'logos/pdf').glob('*.pdf'):
    p=PdfReader(f);assert len(p.pages)==1 and len(p.pages[0].images)==0,f
assert len(PdfReader(R/'brand-guide.pdf').pages)==3
results['vector_pdfs_and_guide']='pass'
palette=json.loads((R/'colors/palette.json').read_text())['colors']
for f in ['palette.css','palette.scss','palette.txt']:
    s=(R/'colors'/f).read_text().lower()
    assert all(v.lower() in s for v in palette.values()),f
def lum(h):
    vals=[int(h[i:i+2],16)/255 for i in [1,3,5]]
    a=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in vals]
    return sum(x*w for x,w in zip(a,[.2126,.7152,.0722]))
def contrast(a,b):
    ls=sorted([lum(a),lum(b)]);return round((ls[1]+.05)/(ls[0]+.05),2)
results['contrast']={'ink_on_paper':contrast(palette['ink'],palette['paper']),'white_on_iris':contrast('#FFFFFF',palette['iris'])}
assert results['contrast']['white_on_iris']>=4.5
for fam in ['Merriweather','Manrope']:
    assert 'SIL OPEN FONT LICENSE' in (R/f'typography/{fam}/OFL.txt').read_text()
with zipfile.ZipFile(R/'typography/fonts.zip') as z:assert z.testzip() is None
results['font_licenses_and_zip']='pass'
ff=imageio_ffmpeg.get_ffmpeg_exe()
p=subprocess.run([ff,'-i',str(R/'media/open-markets-intro.mp4'),'-f','null','-'],capture_output=True,text=True)
assert p.returncode==0,p.stderr
assert '1920x1080' in p.stderr and '30 fps' in p.stderr and '00:00:06.00' in p.stderr
results['intro_video']={'decode':'pass','size':'1920x1080','fps':30,'duration_seconds':6,'audio':'none'}
results['counts']={'vector_logos':len(list((R/'logos/svg').glob('*.svg'))),'transparent_logo_pngs':len(list((R/'logos/png').glob('*.png'))),'vector_logo_pdfs':len(list((R/'logos/pdf').glob('*.pdf'))),'editable_templates':len(list((R/'templates').glob('*-editable.svg')))}
(R/'source/validation.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
