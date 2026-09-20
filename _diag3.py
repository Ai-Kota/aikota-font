# -*- coding: utf-8 -*-
"""独立诊断: 只渲 日/山/水 3 字 (全格盒 O 结构), 看当前 radicals+layout 管线实际输出."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib.tables._g_l_y_f import Glyph
from radicals import RADICALS
from layout import part_box, scale_strokes, UPM, BASELINE, TOP

def contour_of(strokes, box):
    pen = TTGlyphPen(None)
    for (stk, px, py, dx, dy, w) in scale_strokes(strokes, box):
        x0, y0, x1, y1 = px, py, px + dx, py + dy
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        hw = w / 2
        r0 = {0: .4, 1: 1, 2: 1, 3: .4, 4: 1, 5: 1, 6: 1}.get(stk, 1)
        r1 = {0: 1, 1: .4, 2: .4, 3: 1, 4: .4, 5: 1, 6: .4}.get(stk, 1)
        c0 = (x0 + nx * hw * r0, y0 + ny * hw * r0)
        c1 = (x0 - nx * hw * r0, y0 - ny * hw * r0)
        c2 = (x1 - nx * hw * r1, y1 - ny * hw * r1)
        c3 = (x1 + nx * hw * r1, y1 + ny * hw * r1)
        pen.moveTo(c0); pen.lineTo(c3); pen.lineTo(c2); pen.lineTo(c1); pen.closePath()
    return pen.glyph()

CH = [(0x65E5, '日'), (0x5C71, '山'), (0x6C34, '水')]
names = ['.notdef']
cmap = {0: '.notdef'}
g0 = Glyph(); g0.numberOfContours = 0
g0.xMin = g0.yMin = g0.xMax = g0.yMax = 0
glyf = {'.notdef': g0}
for cp, ch in CH:
    gn = 'u%04X' % cp
    names.append(gn); cmap[cp] = gn
    box = part_box('O', [ch], 0, BASELINE, UPM, TOP - BASELINE)[0]
    glyf[gn] = contour_of(RADICALS[ch], box)

fb = FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(names)
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyf, calcGlyphBounds=True)
fb.setupHorizontalMetrics({g: (UPM, 0) for g in names})
fb.setupHorizontalHeader(ascent=880, descent=120)
fb.setupNameTable({"familyName": "d", "styleName": "R", "fullName": "d", "psName": "d-R",
                   "version": "1", "copyright": "c"})
fb.setupOS2(sTypoAscender=880, sTypoDescender=120, usWinAscent=882, usWinDescent=120,
            fsSelection=64, fsType=8)
fb.setupPost(isFixedPitch=1)
fb.save(os.path.join(os.path.dirname(__file__), '_d3.ttf'))

from PIL import Image, ImageFont, ImageDraw
f = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '_d3.ttf'), 220)
img = Image.new('RGB', (900, 320), 'white')
d = ImageDraw.Draw(img)
x = 10
for cp, ch in CH:
    d.text((x, 50), ch, font=f, fill='#002288')
    x += 300
img.save(os.path.join(os.path.dirname(__file__), '_diag3.png'))
print('wrote _diag3.png')
