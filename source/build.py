from pathlib import Path
import sys, json, math, base64
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent.parent
INK='#282238'; PAPER='#F7F4ED'; IRIS='#7C65B3'
for d in ['source','logos/svg','logos/png','logos/pdf','templates','social','website','media','previews','press','typography/static']:
    (ROOT/d).mkdir(parents=True,exist_ok=True)

def svg(w,h,body,title='Open Markets Foundation'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>{body}</svg>'
def put(path,s):
    (ROOT/path).write_text(s)

# Corrected outlined letters are the canonical source; never retrace a concept raster.
master=json.loads((ROOT/'source/identity-paths.json').read_text())
def shape(key,x,y,width,color=INK):
    p=master[key];s=width/p['width']
    return f'<path fill="{color}" fill-rule="evenodd" transform="translate({x} {y}) scale({s})" d="{p["path"]}"/>'
def symbol(x,y,size,color=INK): return shape('symbol',x,y,size,color)
def badge(x,y,size,fg=PAPER,bg=INK):
    scale=size*.82/master['symbol']['width'];ox=x+size*.055;oy=y+size*.085
    cx=(x+size/2-ox)/scale;cy=(y+size/2-oy)/scale;r=size/2/scale
    circle=f'M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0Z'
    clip=f'clip-{x}-{y}-{size}'.replace('.','p')
    return f'<defs><clipPath id="{clip}"><circle cx="{x+size/2}" cy="{y+size/2}" r="{size/2}"/></clipPath></defs><g clip-path="url(#{clip})"><path fill="{bg}" fill-rule="evenodd" transform="translate({ox} {oy}) scale({scale})" d="{circle+master["symbol"]["path"]}"/></g>'
def words(x,y,w,color=INK):
    # Preserve concept lettering with clearance below the repaired p descender.
    s=w/286
    return shape('open',x,y,199*s,color)+shape('markets',x,y+100*s,286*s,color)+shape('foundation',x+6*s,y+178*s,279*s,color)
def horizontal(x,y,w,color=INK):
    # Same word paths, rearranged on one baseline for a wide lockup.
    s=w/500
    return shape('open',x,y-8*s,199*s,color)+shape('markets',x+214*s,y,286*s,color)+shape('foundation',x+6*s,y+98*s,279*s,color)

# Fit the complete text block, including FOUNDATION, inside the badge height.
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen

def word_bounds(arrangement):
    offsets=[('open',0,0),('markets',0,100),('foundation',6,178)] if arrangement=='stacked' else [('open',0,-8),('markets',214,0),('foundation',6,98)]
    bounds=[]
    for key,x,y in offsets:
        pen=BoundsPen(None);parse_path(master[key]['path'],pen)
        a,b,c,d=pen.bounds;bounds.append((a+x,b+y,c+x,d+y))
    return min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)

def aligned_lockup(x,y,width,color=INK,arrangement='horizontal'):
    a,b,c,d=word_bounds(arrangement)
    # Badge height equals the actual visible text height; gap scales with it.
    scale=width/((d-b)*1.18+c-a)
    size=(d-b)*scale
    xx=x+size*1.18-a*scale; yy=y-b*scale
    letters=words(xx,yy,286*scale,color) if arrangement=='stacked' else horizontal(xx,yy,500*scale,color)
    return badge(x,y,size,PAPER if color in [INK,'#000000'] else INK,color)+letters

def lockup_height(width,arrangement):
    a,b,c,d=word_bounds(arrangement)
    return width*(d-b)/((d-b)*1.18+c-a)

variants={
 'badge':(1000,1000,lambda c,b:badge(40,40,920,PAPER if c in [INK,'#000000'] else INK,c)),
 'symbol':(1000,920,lambda c,b:symbol(40,40,920,c)),
 'stacked':(1500,700,lambda c,b:aligned_lockup(50,(700-lockup_height(1400,'stacked'))/2,1400,c,'stacked')),
 'horizontal':(1900,500,lambda c,b:aligned_lockup(40,(500-lockup_height(1820,'horizontal'))/2,1820,c))
}
for name,(w,h,fn) in variants.items():
 for variant,c in [('ink',INK),('black','#000000'),('white','#FFFFFF')]:
  # White variants use transparent backgrounds; the badge intentionally contains
  # ink-colored internal detail so it matches the board's solid reverse treatment.
  put(f'logos/svg/omf-{name}-{variant}.svg',svg(w,h,fn(c,None),f'Open Markets Foundation {name}, {variant}'))

small=''.join(master['symbol']['parts'][i]['path'] for i in [3,5,6,7,8])
put('website/icon.svg',svg(1000,1000,badge(40,40,920).replace(master['symbol']['path'],small),'Open Markets simplified icon'))

# Installable static instances and deterministic outline typesetting for exports.
fonts={}
for key,family,weight in [('serif','Merriweather',700),('body','Manrope',400),('semibold','Manrope',600)]:
    f=TTFont(ROOT/f'typography/{family}/{family}-Variable.ttf')
    axes={'wght':weight}
    if family=='Merriweather':axes.update({'opsz':48,'wdth':100})
    f=instantiateVariableFont(f,axes,inplace=False,updateFontNames=True)
    dest=ROOT/f'typography/static/{family}-{weight}.ttf' # Existing static instances stay unchanged.
    fonts[key]=f
LIVE=False
def text(s,x,y,size=48,font='body',color=INK,tracking=0,anchor='start'):
    f=fonts[font];glyphs=f.getGlyphSet();cmap=f.getBestCmap();upm=f['head'].unitsPerEm
    widths=[f['hmtx'][cmap.get(ord(ch),'.notdef')][0]*size/upm for ch in s]
    width=sum(widths)+max(0,len(s)-1)*tracking
    xx=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
    if LIVE:
      fam='Merriweather' if font=='serif' else 'Manrope';weight=700 if font=='serif' else 600 if font=='semibold' else 400
      return f'<text x="{x}" y="{y}" fill="{color}" font-family="{fam}" font-weight="{weight}" font-size="{size}" font-kerning="none" font-variant-ligatures="none" letter-spacing="{tracking}" text-anchor="{anchor}">{escape(s)}</text>'
    out=''
    for ch,adv in zip(s,widths):
      pen=SVGPathPen(glyphs);glyphs[cmap.get(ord(ch),'.notdef')].draw(pen)
      out+=f'<path fill="{color}" transform="translate({xx:.3f} {y}) scale({size/upm:.6f} {-size/upm:.6f})" d="{pen.getCommands()}"/>'
      xx+=adv+tracking
    return out
def img(path,w,h,x=0,y=0,fit='xMidYMid slice'):
    uri=('../'+path) if LIVE else ('data:image/webp;base64,' if path.endswith('.webp') else 'data:image/png;base64,')+base64.b64encode((ROOT/path).read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{fit}" xlink:href="{uri}"/>'
def rect(x,y,w,h,color): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'
def rule(x,y,w):return rect(x,y,w,5,IRIS)
def brand(x,y,w,color=INK):
    return aligned_lockup(x,y,w,color)
def base(w,h): return rect(0,0,w,h,PAPER)

def podcast():
    w=h=3000
    body=img('illustrations/podcast-watercolor.png',w,h)
    body+=symbol(930,420,1140,PAPER)
    body+=horizontal(265,1650,2470,PAPER)
    # Podcast is a sibling lockup: no FOUNDATION subtitle in the show title.
    s=2470/500
    # Replace the horizontal lockup above with its two word paths only.
    body=img('illustrations/podcast-watercolor.png',w,h)+symbol(930,420,1140,PAPER)
    body+=shape('open',265,1580,199*s,PAPER)+shape('markets',265+214*s,1580+8*s,286*s,PAPER)
    body+=text('PODCAST',1500,2210,130,'body',PAPER,38,'middle')
    body+=rect(1315,2370,370,9,IRIS)
    body+=text('Eric FJ & Sync',1500,2670,100,'body',PAPER,0,'middle')
    return svg(w,h,body,'Open Markets Podcast — Eric FJ & Sync')
# Lossless PNG encoding for SVG renderers that do not decode embedded WebP.
# The authoritative WebP file and decoded pixels remain unchanged.
ART='illustrations/lemonade-children-day-transparent.png'
Image.open(ROOT/'illustrations/lemonade-children-day-transparent.webp').save(ROOT/ART)
def original(x,y,size):
    return img(ART,size,size,x,y,fit='xMidYMid meet')
def social(w=1080,h=1080):
    body=base(w,h)+brand(65,45,520)
    body+=text('Markets with integrity.',65,240,60,'serif')
    body+=original(175,280,730)
    body+=text('openmarkets.pub',65,1040,25,'body')
    return svg(w,h,body)
def linkcard():
    w,h=1200,630;body=base(w,h)+original(600,15,600)
    body+=brand(50,45,475)
    body+=text('Markets with',50,285,60,'serif')+text('integrity.',50,370,72,'serif')
    body+=text('Open infrastructure for markets',50,450,25)+text('that work for everyone.',50,490,25)
    body+=rule(50,535,90)+text('openmarkets.pub',50,590,22)
    return svg(w,h,body)
def story():
    w,h=1080,1920;body=base(w,h)+brand(80,75,680)
    for i,line in enumerate(['Build.','Buy.','Trade. Sell.']):body+=text(line,80,420+i*145,110,'serif')
    body+=text('On open protocols.',80,850,43)+rule(80,900,130)
    body+=original(90,930,900)
    body+=text('openmarkets.pub',80,1870,30,'body')
    return svg(w,h,body)
def hero():
    # Square artwork, kept intact; responsive site text belongs outside the image.
    return svg(1152,1152,original(0,0,1152),'Original Open Markets homepage artwork')
def episode():
    w,h=1920,1080;body=img('illustrations/podcast-watercolor.png',w,h)
    body+=f'<rect width="{w}" height="{h}" fill="{INK}" opacity="0.45"/>'
    body+=brand(90,70,590,PAPER)
    body+=text('OPEN MARKETS PODCAST',90,340,33,'semibold',PAPER,4)
    body+=text('Markets with',90,510,98,'serif',PAPER)+text('integrity.',90,640,113,'serif',PAPER)
    body+=rule(90,715,150)+text('Conversations on open commerce',90,815,35,'body',PAPER)
    body+=text('Eric FJ & Sync',90,970,32,'body',PAPER)
    body+=symbol(1320,360,470,PAPER)
    return svg(w,h,body,'Open Markets Podcast title card')
def slide():
    w,h=1920,1080;body=base(w,h)+original(930,100,950)
    body+=brand(90,80,650)+text('Open infrastructure.',90,430,76,'serif')+text('Open possibilities.',90,550,76,'serif')
    body+=rule(90,660,150)+text('Open Markets Foundation',90,770,35)+text('openmarkets.pub',90,980,26)
    return svg(w,h,body,'Open Markets Foundation presentation title')

applications={'podcast/open-markets-podcast-cover':podcast,'social/square':social,'social/link-preview':linkcard,'social/story':story,'website/hero':hero,'media/podcast-title':episode,'templates/presentation-title':slide}
for name,fn in applications.items():
    LIVE=False;put(name+'.svg',fn())
    LIVE=True;put('templates/'+Path(name).name+'-editable.svg',fn())
LIVE=False

# A contact sheet doubles as the public download index preview.
body=base(1800,1200)
body+=text('Open Markets Foundation',70,95,50,'serif')+text('Production asset library / watercolor identity',70,145,24)
body+=badge(85,225,280)+symbol(440,245,270)+badge(820,225,280,INK,PAPER)
body=body.replace(badge(820,225,280,INK,PAPER),rect(780,205,360,330,INK)+badge(820,225,280,INK,PAPER))
body+=rect(1190,205,540,330,INK)+symbol(1320,245,270,PAPER)
for label,x in [('Primary badge',85),('Freestanding symbol',430),('Reversed badge',800),('White symbol',1250)]:body+=text(label,x,580,22)
body+=aligned_lockup(70,685,650,INK,'stacked')
body+=aligned_lockup(830,740,880)
body+=text('Stacked lockup',75,1040,23)+text('Horizontal lockup',865,1040,23)
for i,(label,color) in enumerate([('Ink',INK),('Paper',PAPER),('Iris',IRIS),('Sage','#879B83'),('Ochre','#C8A65A')]):
    body+=rect(70+i*340,1100,80,30,color)+text(label+' '+color,165+i*340,1124,18)
put('previews/asset-library.svg',svg(1800,1200,body))
put('source/build-manifest.json',json.dumps({'master':'source/identity-paths.json','method':'Corrected vector paths; badge height aligned to the full text block including FOUNDATION. Foundation artwork is the unchanged square homepage image.', 'artwork':'source/homepage-artwork.json','applications':list(applications),'palette':{'ink':INK,'paper':PAPER,'iris':IRIS,'sage':'#879B83','ochre':'#C8A65A'}},indent=2)+'\n')
print('Created shared master paths, 12 logo SVGs, 7 layouts, 7 editable templates, using existing font instances.')
print({k:v['contours'] for k,v in master.items()})
