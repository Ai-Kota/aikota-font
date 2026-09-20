# -*- coding: utf-8 -*-
"""
aikota-font · C 路线 350 全量生成器 (曲线笔形, 成品字体)
================================================================
B 路线骨架 (部件拆分 + 几何均值 + 摆位) -> C 路线 brush_shape 曲线 taper
-> TTF (楷体笔锋风格). 出成 aikota-c350.ttf (成品).
跑法: python gen_c350.py
"""
import sys, os, math, json, io
sys.path.insert(0, os.path.dirname(__file__))

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = open(os.path.join(HERE, '350chars.txt'), encoding='utf-8').read().split()

from layout import part_box, scale_strokes, UPM, BASELINE, TOP
from brush_shape import all_contours, H, V, PIE, NA, DIAN
from _patch_fix import part_geo_mean, to_rad, COMP, stroke_geo

# 部件几何缓存 (复用 _patch_fix 的均值 + 类型判定)
_PART_CACHE = {}
def part_strokes(part):
    if part in _PART_CACHE:
        return _PART_CACHE[part]
    g = part_geo_mean(part)
    out = to_rad(g) if g else None
    _PART_CACHE[part] = out
    return out

def glyph_contours(ch):
    """C 路线: 摆位 -> brush 曲线包络 (14 点/笔)."""
    struct, parts = COMP.get(ch, ('O', [ch]))
    boxes = part_box(struct, parts, 0, BASELINE, UPM, TOP - BASELINE)
    contours = []
    for part, box in zip(parts, boxes):
        st = part_strokes(part)
        if st is None:
            continue
        contours.extend(all_contours(scale_strokes(st, box)))
    return contours

def build_ttf(path):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.ttLib.tables._g_l_y_f import Glyph
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    names = ['.notdef']
    cmap = {0: '.notdef'}
    glyf = {}
    g0 = Glyph(); g0.numberOfContours = 0
    g0.xMin = g0.yMin = g0.xMax = g0.yMax = 0
    glyf['.notdef'] = g0
    ok = miss = 0
    for ch in chars:
        cp = ord(ch)
        gn = f'u{cp:04X}'
        names.append(gn); cmap[cp] = gn
        cs = glyph_contours(ch)
        pen = TTGlyphPen(None)
        if not cs:
            pen.moveTo(300, 120); pen.lineTo(450, 120); pen.lineTo(450, 880)
            pen.lineTo(300, 880); pen.closePath()
            miss += 1
        else:
            for c in cs:
                pen.moveTo(c[0])
                for p in c[1:]:
                    pen.lineTo(p)
                pen.closePath()
            ok += 1
        glyf[gn] = pen.glyph()
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf, calcGlyphBounds=True)
    fb.setupHorizontalMetrics({g: (UPM, 0) for g in names})
    fb.setupHorizontalHeader(ascent=880, descent=120)
    fb.setupNameTable({
        'familyName': 'aikota-C', 'styleName': 'Kai',
        'fullName': 'aikota-C 350 (C-route brush shape, self-developed)',
        'psName': 'aikota-C-350', 'version': 'Version 1.0',
        'copyright': 'aikota font (C route): self-developed skeleton + brush taper. 350 common chars.',
    })
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    fb.setupOS2(sTypoAscender=880, sTypoDescender=120, usWinAscent=882, usWinDescent=120,
                fsSelection=64, fsType=8)
    pn = Panose(); pn.bFamilyType = 2; pn.bCharSet = 1; pn.bProportion = 9
    fb.font['OS/2'].panose = pn
    fb.setupPost(isFixedPitch=1)
    fb.setupHead(fontRevision=1.0, created=3937000000, modified=3937000000)
    fb.save(path)
    return ok, miss

if __name__ == '__main__':
    out = os.path.join(HERE, 'aikota-c350.ttf')
    ok, miss = build_ttf(out)
    io.open(os.path.join(HERE, '_c350_summary.txt'), 'w', encoding='utf-8').write(
        f'total {len(chars)}  ok {ok}  fallback-missing {miss}\n')
    print(f'wrote {out}  ({len(chars)} chars, ok={ok}, fallback={miss})')
