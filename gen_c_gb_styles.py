# -*- coding: utf-8 -*-
"""
aikota-font · C 路线 GB2312 全量 4 风格生成器
================================================================
跑 4 风格 (KAISO/SHOULJIN/YUAN/ART) 各出 GB2312 全量 6763 字 TTF.
跑法: python gen_c_gb_styles.py
"""
import sys, os, math, json, io, time
sys.path.insert(0, os.path.dirname(__file__))

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = list(open(os.path.join(HERE, 'gb2312_all.txt'), encoding='utf-8').read().strip())

from layout import part_box, scale_strokes, UPM, BASELINE, TOP
from brush_shape import all_contours, _DEFAULT_WM_STRENGTH
from _patch_fix import part_geo_mean, to_rad, COMP

_PART_CACHE = {}
def part_strokes(part):
    if part in _PART_CACHE:
        return _PART_CACHE[part]
    g = part_geo_mean(part)
    out = to_rad(g) if g else None
    _PART_CACHE[part] = out
    return out

STYLE_META = {
    # style -> (psName, 中文名, fullName, 渠道水印id)
    'KAISO':    ('aikota-C-Kai',     '楷体',   'aikota-C GB2312 full (KAISO, Kaiti brush, self-dev)', 0xA1),
    'SHOULJIN': ('aikota-C-Shoujin', '瘦金',   'aikota-C GB2312 full (SHOULJIN, thin-brisk, self-dev)', 0xA2),
    'YUAN':     ('aikota-C-Yuan',    '圆体',   'aikota-C GB2312 full (YUAN, rounded, self-dev)', 0xA3),
    'ART':      ('aikota-C-Art',     '美术',   'aikota-C GB2312 full (ART, square-bold, self-dev)', 0xA4),
}

def get_channel(style):
    """取渠道水印 id. 支持从 vault 密码墙注入密钥 (aikota/wm-key).
    vault 明文: {"channel": {"KAISO": 0xA1, ...}, "strength": 0.5}
    无 vault 时回退 STYLE_META 里的内置 id (生成字体仍带水印, 只是密钥非秘密)."""
    chan = STYLE_META[style][3]
    try:
        import json as _json, subprocess
        out = subprocess.run(
            [r'E:/AImlyForge/releases/vault/v0.1.0/vault-cli.exe', 'get', 'aikota/wm-key'],
            capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            key = _json.loads(out.stdout)
            if style in key.get('channel', {}):
                chan = key['channel'][style]
    except Exception:
        pass
    return chan

def glyph_contours(ch, style):
    struct, parts = COMP.get(ch, ('O', [ch]))
    boxes = part_box(struct, parts, 0, BASELINE, UPM, TOP - BASELINE)
    contours = []
    for part, box in zip(parts, boxes):
        st = part_strokes(part)
        if st is None:
            continue
        contours.extend(all_contours(scale_strokes(st, box), style=style,
                                      watermark=(get_channel(style), _DEFAULT_WM_STRENGTH)))
    return contours

def build_ttf(path, style, name_cn, full_name):
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
        cs = glyph_contours(ch, style)
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
        if (i + 1) % 1000 == 0:
            print(f'  {style} progress {i+1}/{len(chars)}')
        glyf[gn] = pen.glyph()
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf, calcGlyphBounds=True)
    fb.setupHorizontalMetrics({g: (UPM, 0) for g in names})
    fb.setupHorizontalHeader(ascent=880, descent=120)
    fb.setupNameTable({
        'familyName': name_cn, 'styleName': style,
        'fullName': full_name,
        'psName': f'aikota-C-{style}', 'version': 'Version 1.0',
        'copyright': f'aikota font (C route) {style}: self-developed skeleton + brush taper. GB2312 full 6763 chars.',
    })
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    fb.setupOS2(sTypoAscender=880, sTypoDescender=120, usWinAscent=882, usWinDescent=120,
                fsSelection=64, fsType=8)
    pn = Panose(); pn.bFamilyType = 2; pn.bCharSet = 1; pn.bProportion = 9
    fb.font['OS/2'].panose = pn
    fb.setupPost(isFixedPitch=1)
    fb.setupHead(fontRevision=1.0, created=3937000000, modified=3937000000)
    fb.save(path)
    print(f'  {style} build {time.time()-t0:.1f}s')
    return ok, miss

if __name__ == '__main__':
    for style, meta in STYLE_META.items():
        name_cn, _cn, full_name, _chan = meta
        out = os.path.join(HERE, f'aikota-c-{style.lower()}.ttf')
        ok, miss = build_ttf(out, style, name_cn, full_name)
        print(f'wrote {out}  ({len(chars)} chars, ok={ok}, fallback={miss})')
