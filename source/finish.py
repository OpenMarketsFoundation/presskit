from pathlib import Path
import sys,json,subprocess,math
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import imageio_ffmpeg

R=Path(__file__).resolve().parent.parent
for f in sorted((R/'logos/svg').glob('*.svg')):
    drawing=svg2rlg(str(f))
    if drawing is None:raise RuntimeError(f)
    renderPDF.drawToFile(drawing,str(R/'logos/pdf'/f.with_suffix('.pdf').name))

pdfmetrics.registerFont(TTFont('Body',str(R/'typography/static/Manrope-400.ttf')))
pdfmetrics.registerFont(TTFont('Bold',str(R/'typography/static/Manrope-600.ttf')))
pdfmetrics.registerFont(TTFont('Serif',str(R/'typography/static/Merriweather-700.ttf')))
ink=HexColor('#282238');paper=HexColor('#F7F4ED');iris=HexColor('#7C65B3')
c=Canvas(str(R/'brand-guide.pdf'),pagesize=(960,640))
c.setTitle('Open Markets Foundation Brand Guide');c.setAuthor('Open Markets Foundation')
def tx(s,x,y,size=14,font='Body',color=ink):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,s)
def page(n,title,sub):
    c.setFillColor(paper);c.rect(0,0,960,640,fill=1,stroke=0)
    tx('OPEN MARKETS FOUNDATION',45,600,10,'Bold');tx(f'BRAND GUIDE / {n:02d}',775,600,10)
    c.setStrokeColor(ink);c.setLineWidth(.4);c.line(45,583,915,583)
    tx(title,45,534,32,'Serif');tx(sub,45,502,13)
    tx('Watercolor identity | 24 October 2026',45,24,9);tx('openmarkets.pub',815,24,9)
page(1,'One mark. One visual family.','The badge and complete text block align. Use the original homepage artwork unchanged.')
c.drawImage(str(R/'previews/asset-library.png'),45,65,870,420,preserveAspectRatio=True,anchor='c',mask='auto')
c.showPage()
page(2,'Use the right file.','SVG for scalable digital artwork. Transparent PNG for everyday use. PDF for vector handoff.')
items=[('Primary identity','Ink badge and wordmark on paper or a quiet light background.'),('Dark backgrounds','Use the white symbol or white lockup on ink or a quiet dark area.'),('Minimum sizes','Full badge: 48 px. Stacked lockup: 280 px wide. Horizontal: 360 px wide.'),('Clear space','Leave at least one bar-width around the symbol and lockups.'),('Small icons','Use the simplified icon at 16-32 px; it omits the stars and outer broadcast arcs.'),('Avoid','Do not stretch, recolor individual parts, add glows, or place text over busy artwork.')]
y=455
for label,body in items:
    tx(label,45,y,14,'Bold');tx(body,45,y-24,12);y-=66
c.showPage()
page(3,'Color, type and watercolor.','A crisp ink identity with warm paper, editorial typography and human scenes of commerce.')
colors=[('Ink','#282238'),('Paper','#F7F4ED'),('Iris','#7C65B3'),('Sage','#879B83'),('Ochre','#C8A65A')]
for i,(name,hx) in enumerate(colors):
    x=45+i*176;c.setFillColor(HexColor(hx));c.rect(x,386,150,72,fill=1,stroke=0)
    tx(name,x,365,13,'Bold');tx(hx,x,345,12)
tx('Merriweather 700',45,285,25,'Serif');tx('Headlines and editorial display type.',45,255,13)
tx('Manrope 400 / 600',480,285,24,'Body');tx('Body copy, navigation and supporting labels.',480,255,13)
tx('The logo lettering is outlined from the concept. Do not retype it in a substitute font.',45,210,12)
tx('Use ink on paper for body text. Iris supports white text at the supplied digital values.',45,180,12)
tx('Sage and ochre are illustration accents, not body-text colors.',45,155,12)
tx('Keep watercolor behind or beside the identity. Protect quiet areas around words.',45,110,12)
tx('Both font families include their SIL Open Font License files. Logo files need no installed font.',45,80,12)
c.showPage();c.save()

# A silent title sequence avoids adding an unapproved music or voice recording.
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-loglevel','error','-loop','1','-i',str(R/'media/podcast-title.png'),'-t','6','-vf','fps=30,fade=t=in:st=0:d=0.8,fade=t=out:st=5:d=1,format=yuv420p','-c:v','libx264','-preset','medium','-crf','20','-movflags','+faststart','-an',str(R/'media/open-markets-intro.mp4')],check=True)
subprocess.run([ff,'-y','-loglevel','error','-ss','2','-i',str(R/'media/open-markets-intro.mp4'),'-frames:v','1',str(R.parent/'intro-check.png')],check=True)
print('Created 12 vector PDFs, 3-page brand guide, and six-second 1080p intro.')
