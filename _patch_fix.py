# -*- coding: utf-8 -*-
"""
aikota-font · 第一性原理引擎补丁 (B 路线)
=========================================
修 3 根因 + 补 PANOSE + 出 manifest. 不改 radicals.py 坐标, 只改管线.
1) part_geo 众数->均值 (笔画几何稳定化)
2) 笔画类型: 绝对方向 -> 相对基线方向 (修 页/辰 撇捺误判)
3) 摆位比例 (NARROW 旁 30%, 其余 40%)
"""
import sys, os, math, json, collections, io, hashlib
sys.path.insert(0, os.path.dirname(__file__))

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = open(os.path.join(HERE, '350chars.txt'), encoding='utf-8').read().split()

from layout import part_box, scale_strokes, UPM, BASELINE, TOP, GAP, NARROW_PARTS

# ── 根因1: part_geo 众数->均值 (笔画几何稳定化) ─────────────────
def stroke_geo(v):
    out = []
    for m in v['medians']:
        pts = [(float(p[0]), float(p[1])) for p in m]
        if len(pts) < 2:
            continue
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        out.append((int(x0), int(y0), int(x1 - x0), int(y1 - y0)))
    return out

def part_geo_mean(part):
    """部件几何 = 自身字 + 350里含该部件字 的 medians 均值 (非众数)."""
    samples = []
    if part in data:
        samples.append(stroke_geo(data[part]))
    for ch in chars:
        if ch != part and ch in data and ch.startswith(part):
            samples.append(stroke_geo(data[ch]))
    if not samples:
        return None
    n = min(len(s) for s in samples)
    acc = [[] for _ in range(n)]
    for s in samples:
        for i in range(min(n, len(s))):
            acc[i].append(s[i])
    geo = []
    for i in range(n):
        rows = acc[i]
        x0 = int(sum(r[0] for r in rows) / len(rows))
        y0 = int(sum(r[1] for r in rows) / len(rows))
        dx = int(sum(r[2] for r in rows) / len(rows))
        dy = int(sum(r[3] for r in rows) / len(rows))
        geo.append((x0, y0, dx, dy))
    return geo

# ── 根因2: 笔画类型判定 (相对基线方向, 非绝对方向) ─────────────
def to_rad(strokes, y_base=400):
    """把 (x0,y0,dx,dy) 判笔画类型. 斜笔按 相对基线 的方向判:
    上斜 (dy<0) -> 左下收=撇(dx<0) / 右下收=捺(dx>0)
    下斜 (dy>0) -> 左上收=撇(dx<0) / 右上收=捺(dx>0)
    这样 页 的 s5 上斜捺 正确判 3, s3 中斜也正确."""
    out = []
    for (x0, y0, dx, dy) in strokes:
        ln = math.hypot(dx, dy)
        # 横: 横向主导 且 足够长
        if abs(dx) > abs(dy) * 1.8 and abs(dx) > 100:
            t, w = 0, 95
        # 竖: 纵向主导 且 足够长
        elif abs(dy) > abs(dx) * 1.8 and abs(dy) > 100:
            t, w = 1, 70
        # 短斜 = 点
        elif ln < 160:
            t, w = 4, 55
        # 斜笔: 相对基线方向判撇捺. 撇=向右下收(dx>0,dy>0), 捺=向左下收(dx<0,dy>0)
        elif dy > 0:  # 下斜 (向画面下)
            t, w = (3, 65) if dx < 0 else (2, 65)
        else:         # 上斜 (向画面上)
            t, w = (2, 65) if dx > 0 else (3, 65)
        out.append((t, x0, y0, dx, dy, w))
    return out

# ── 根因3: 摆位比例 (NARROW 旁 30%, 其余 40%) ──────────────────
# 已存在 part_box, 不动. NARROW_PARTS 已含 氵讠阝忄礻衤犭.

# ── 部件拆分表 (沿用 gen_350.py 的 COMP, 这里内联) ────────────
COMP = {}
def R(ch, l, r): COMP[ch] = ('R', [l, r])
def T(ch, t, b): COMP[ch] = ('T', [t, b])
R('河','氵','可'); R('海','氵','每'); R('江','氵','工'); R('法','氵','去')
R('洋','氵','羊'); R('清','氵','青'); R('洗','氵','先'); R('活','氵','舌')
R('治','氵','台'); R('流','氵','丣')
R('语','讠','五'); R('认','讠','人'); R('计','讠','十'); R('话','讠','舌')
R('说','讠','兑'); R('请','讠','青'); R('讲','讠','井'); R('让','讠','上')
R('讨','讠','十'); R('论','讠','仑'); R('记','讠','己'); R('诉','讠','斥')
R('打','扌','乙'); R('把','扌','巴'); R('接','扌','妾'); R('提','扌','是')
R('指','扌','止'); R('推','扌','隹'); R('拉','扌','立'); R('持','扌','寺')
R('拍','扌','白'); R('拔','扌','巴'); R('抓','扌','爪')
R('抱','扌','包'); R('拨','扌','发'); R('撑','扌','堂'); R('撤','扌','育')
R('挣','扌','争'); R('挤','扌','齐'); R('拼','扌','并')
R('情','忄','青'); R('性','忄','生'); R('悟','忄','吾'); R('怀','忄','不')
R('快','忄','夬'); R('想','木','心'); R('没','氵','殳')
R('都','者','阝'); R('队','阝','人')
T('安','宀','女'); T('家','宀','豕'); T('定','宀','正')
T('宝','宀','玉'); T('字','宀','子'); T('它','宀','匕'); T('宜','宀','且')
T('元','二','儿'); T('全','人','王'); T('今','亼','人')
T('床','广','木'); T('庆','广','夂'); T('庐','广','户')
T('去','土','厶'); T('丢','亠','8'); T('夹','大','8'); T('奇','大','可')
T('思','田','心'); T('意','音','心'); T('忠','中','心'); T('志','士','心')
T('忘','亡','心'); T('忍','刃','心'); T('告','⺌','口'); T('高','亠','口')
T('音','立','日'); T('雪','雨','夕'); T('雷','雨','田'); T('雾','雨','务')
T('需','雨','而'); T('露','雨','路'); T('霉','雨','贵')
T('态','太','心'); T('怒','奴','心'); T('悲','非','心'); T('恰','忄','合')
T('总','穴','心'); T('感','咸','心')
COMP['国'] = ('W', ['口', '玉']); COMP['圆'] = ('W', ['囗', '员'])
COMP['围'] = ('W', ['囗', '韦']); COMP['团'] = ('W', ['囗', '才'])
COMP['回'] = ('W', ['囗', '口']); COMP['固'] = ('W', ['口', '古'])
COMP['区'] = ('W', ['囗', '8']); COMP['向'] = ('W', ['丿', '口'])
COMP['同'] = ('W', ['冂', '一'])
COMP['匠'] = ('F', ['匚', '8']); COMP['医'] = ('F', ['匚', '矢'])
COMP['建'] = ('F', ['廴', '8'])

# ── 轮廓展开 (笔形 taper) ──────────────────────────────────────
def contour_of(strokes, box):
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    pen = TTGlyphPen(None)
    for (stk, px, py, dx, dy, w) in scale_strokes(strokes, box):
        x0, y0, x1, y1 = px, py, px + dx, py + dy
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        hw = w / 2
        r0 = {0: .4, 1: 1, 2: 1, 3: .4, 4: 1}.get(stk, 1)
        r1 = {0: 1, 1: .4, 2: .4, 3: 1, 4: .4}.get(stk, 1)
        c0 = (x0 + nx * hw * r0, y0 + ny * hw * r0)
        c1 = (x0 - nx * hw * r0, y0 - ny * hw * r0)
        c2 = (x1 - nx * hw * r1, y1 - ny * hw * r1)
        c3 = (x1 + nx * hw * r1, y1 + ny * hw * r1)
        pen.moveTo(c0); pen.lineTo(c3); pen.lineTo(c2); pen.lineTo(c1); pen.closePath()
    return pen.glyph()

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
        for (stk, px, py, dx, dy, w) in scale_strokes(st, box):
            x0, y0, x1, y1 = px, py, px + dx, py + dy
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            nx, ny = -uy, ux
            hw = w / 2
            r0 = {0: .4, 1: 1, 2: 1, 3: .4, 4: 1}.get(stk, 1)
            r1 = {0: 1, 1: .4, 2: .4, 3: 1, 4: .4}.get(stk, 1)
            c0 = (x0 + nx * hw * r0, y0 + ny * hw * r0)
            c1 = (x0 - nx * hw * r0, y0 - ny * hw * r0)
            c2 = (x1 - nx * hw * r1, y1 - ny * hw * r1)
            c3 = (x1 + nx * hw * r1, y1 + ny * hw * r1)
            contours.append([c0, c3, c2, c1])
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
        'familyName': 'aikota-B', 'styleName': '350',
        'fullName': 'aikota-B 350 (self-developed skeleton, B route, fixed v2)',
        'psName': 'aikota-B-350', 'version': 'Version 0.5-draft',
        'copyright': 'aikota font engine (B route): self-developed skeleton, 350 common chars. Draft for review.',
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
    out = os.path.join(HERE, 'aikota350_fixed.ttf')
    ok, miss = build_ttf(out)
    io.open(os.path.join(HERE, '_350_fixed_summary.txt'), 'w', encoding='utf-8').write(
        f'total {len(chars)}  ok {ok}  fallback-missing {miss}\n')
    print(f'wrote {out}  ({len(chars)} chars, ok={ok}, fallback={miss})')
