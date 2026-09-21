# -*- coding: utf-8 -*-
"""独立最小渲染: 从当前 radicals.py 重新生成 TTF 并放大渲染, 不依赖历史 png."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib.tables._g_l_y_f import Glyph
from radicals import RADICALS
from layout import part_box, scale_strokes, UPM, BASELINE, TOP
import math

def blank():
    g = Glyph(); g.numberOfContours = 0
    g.xMin = g.yMin = g.xMax = g.yMax = 0
    return g

CHARS = {0x65E5: '日', 0x6708: '月', 0x53E3: '口', 0x5C71: '山',
         0x6C34: '水', 0x6728: '木', 0x5929: '天', 0x571F: '土'}

glyphs_order = ['.notdef'] + [f'u{cp:04X}' for cp in CHARS]
cmap = {0: '.notdef'}
glyf = {'.notdef': blank()}
for cp, cname in CHARS.items():
    gname = f'u{cp:04X}'; cmap[cp] = gname
    box = part_box('O', [cname], 0, BASELINE, UPM, TOP - BASELINE)[0]
    pen = TTGlyphPen(None)
    for (stk, px, py, dx, dy, w) in scale_strokes(RADICALS[cname], box):
        x0, y0, x1, y1 = px, py, px + dx, py + dy
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        hw = w / 2
        r0 = {0: .4, 1: 1, 2: 1, 3: .4}.get(stk, 1)
        r1 = {0: 1, 1: .4, 2: .4, 3: 1}.get(stk, 1)
        p0 = (x0 + nx * hw * r0, y0 + ny * hw * r0)
        p1 = (x0 - nx * hw * r0, y0 - ny * hw * r0)
        p2 = (x1 - nx * hw * r1, y1 - ny * hw * r1)
        p3 = (x1 + nx * hw * r1, y1 + ny * hw * r1)
        pen.moveTo(p0); pen.lineTo(p3); pen.lineTo(p2); pen.lineTo(p1); pen.closePath()
    glyf[gname] = pen.glyph()

fb = FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(glyphs_order)
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyf, calcGlyphBounds=True)
fb.setupHorizontalMetrics({g: (UPM, 0) for g in glyphs_order})
fb.setupHorizontalHeader(ascent=880, descent=120)
fb.setupNameTable({"familyName": "aikotaB", "styleName": "R", "fullName": "aikotaB",
                   "psName": "aikotaB-R", "version": "0.2", "copyright": "aikota"})
fb.setupOS2(sTypoAscender=880, sTypoDescender=120, usWinAscent=882, usWinDescent=120, fsSelection=64, fsType=8)
fb.setupPost(isFixedPitch=1)
fb.save(os.path.join(os.path.dirname(__file__), 'min8.ttf'))

from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'min8.ttf'), 200)
img = Image.new('RGB', (1000, 280), 'white')
d = ImageDraw.Draw(img)
x = 10
for cp, cname in CHARS.items():
    d.text((x, 40), cname, font=f, fill='#0033cc')
    x += 120
img.save(os.path.join(os.path.dirname(__file__), 'min8.png'))
print('wrote min8.png (fresh, not cached)')
