# -*- coding: utf-8 -*-
"""
aikota-font · C 路线 GB2312 一级 6763 字生成器 (曲线笔形, 成品字体)
================================================================
复用 gen_c350.py 的 C 路线引擎 (brush_shape 14点包络 + 部件几何均值 + 摆位),
字表换成 GB2312 L1 6763. 出成 aikota-c-gb.ttf (C 路线全量成品).
跑法: python gen_c_l1.py
"""
import sys, os, math, json, io, time
sys.path.insert(0, os.path.dirname(__file__))

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = list(open(os.path.join(HERE, '../data', 'gb2312_all.txt'), encoding='utf-8').read().strip())

from layout import part_box, scale_strokes, UPM, BASELINE, TOP
from brush_shape import all_contours
from _patch_fix import part_geo_mean, to_rad, COMP

_PART_CACHE = {}
def part_strokes(part):
    if part in _PART_CACHE:
        return _PART_CACHE[part]
    g = part_geo_mean(part)
    out = to_rad(g) if g else None
    _PART_CACHE[part] = out
    return out

def glyph_contours(ch):
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
    t0 = time.time()
    names = ['.notdef']
    cmap = {0: '.notdef'}
    glyf = {}
    g0 = Glyph(); g0.numberOfContours = 0
    g0.xMin = g0.yMin = g0.xMax = g0.yMax = 0
    glyf['.notdef'] = g0
    ok = miss = 0
    for i, ch in enumerate(chars):
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
        if (i + 1) % 500 == 0:
            print(f'  progress {i+1}/{len(chars)}')
        glyf[gn] = pen.glyph()
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf, calcGlyphBounds=True)
    fb.setupHorizontalMetrics({g: (UPM, 0) for g in names})
    fb.setupHorizontalHeader(ascent=880, descent=120)
    fb.setupNameTable({
        'familyName': 'aikota-C', 'styleName': 'GB2312-L1',
        'fullName': 'aikota-C GB2312 L1 (C-route brush shape, self-developed)',
        'psName': 'aikota-C-L1', 'version': 'Version 1.1',
        'copyright': 'aikota font (C route): self-developed skeleton + brush taper. GB2312 L1 6763 chars.',
    })
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    fb.setupOS2(sTypoAscender=880, sTypoDescender=120, usWinAscent=882, usWinDescent=120,
                fsSelection=64, fsType=8)
    pn = Panose(); pn.bFamilyType = 2; pn.bCharSet = 1; pn.bProportion = 9
    fb.font['OS/2'].panose = pn
    fb.setupPost(isFixedPitch=1)
    fb.setupHead(fontRevision=1.0, created=3937000000, modified=3937000000)
    fb.save(path)
    print(f'build time {time.time()-t0:.1f}s')
    return ok, miss

if __name__ == '__main__':
    out = os.path.join(HERE, 'aikota-c-gb.ttf')
    ok, miss = build_ttf(out)
    io.open(os.path.join(HERE, '_c_gb_summary.txt'), 'w', encoding='utf-8').write(
        f'total {len(chars)}  ok {ok}  fallback-missing {miss}\n')
    print(f'wrote {out}  ({len(chars)} chars, ok={ok}, fallback={miss})')
