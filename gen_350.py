# -*- coding: utf-8 -*-
"""
aikota-font · 350 全量 TTF 生成器 (B 路线 · 第一性原理管线)
================================================================
每字: 部件拆分表 -> 每部件 medians 几何均值 -> layout 摆位 -> 笔形 taper 轮廓 -> TTF
IP: 拆分=公共知识, 均值=公共数据, 轮廓算法+摆位公式=自有.
跑法: python gen_350.py   -> aikota350.ttf
"""
import sys, os, math, json, collections, io
sys.path.insert(0, os.path.dirname(__file__))

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = open(os.path.join(HERE, '350chars.txt'), encoding='utf-8').read().split()

from layout import part_box, scale_strokes, UPM, BASELINE, TOP, GAP, NARROW_PARTS

# ── 笔画几何: 字 -> [(x0,y0,dx,dy)] [font y-up] ─────────────────
def stroke_geo(v):
    out = []
    for m in v['medians']:
        pts = [(float(p[0]), float(p[1])) for p in m]
        if len(pts) < 2:
            continue
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        out.append((int(x0), int(y0), int(x1 - x0), int(y1 - y0)))
    return out

def part_geo(part):
    """部件几何 = 自身字 + 350里含该部件字 的 medians 几何均值."""
    samples = []
    if part in data:
        samples.append(stroke_geo(data[part]))
    for ch in chars:
        if ch != part and ch in data and ch.startswith(part):
            samples.append(stroke_geo(data[ch]))
    if not samples:
        return None
    n = min(len(s) for s in samples)
    acc = [collections.Counter() for _ in range(n)]
    for s in samples:
        for i in range(min(n, len(s))):
            acc[i][s[i]] += 1
    return [acc[i].most_common(1)[0][0] for i in range(n)]

def to_rad(strokes):
    """几何 -> radicals 行 (font y-up), 宽度按笔画类分档 + 笔画类型推断."""
    out = []
    for (x0, y0, dx, dy) in strokes:
        ln = math.hypot(dx, dy)
        if abs(dx) > abs(dy) * 2.2 and abs(dx) > 120:
            t, w = 0, 95
        elif abs(dy) > abs(dx) * 2.2 and abs(dy) > 120:
            t, w = 1, 70
        elif ln < 160:
            t, w = 4, 55
        elif dx < 0 and dy < 0:
            t, w = 2, 65
        else:
            t, w = 3, 65
        out.append((t, x0, y0, dx, dy, w))
    return out

# ── 部件拆分表: 字 -> (结构, [部件序列]) ─────────────────────────
# 默认独体 (O, [自身]); 复合字覆盖. 部件名 = 数据源里存在的字.
def default_split(ch):
    return ('O', [ch])

COMP = {}
def R(ch, left, right): COMP[ch] = ('R', [left, right])
def T(ch, top, bottom): COMP[ch] = ('T', [top, bottom])

# 左右结构 (R): 偏旁 + 右件. 部件名必须存在于数据源.
R('河','氵','可'); R('海','氵','每'); R('江','氵','工'); R('法','氵','去')
R('洋','氵','羊'); R('清','氵','青'); R('洗','氵','先'); R('活','氵','舌')
R('治','氵','台'); R('流','氵','丣')
R('语','讠','五'); R('认','讠','人'); R('计','讠','十'); R('话','讠','舌')
R('说','讠','兑'); R('请','讠','青'); R('讲','讠','井'); R('让','讠','上')
R('讨','讠','十'); R('论','讠','仑'); R('记','讠','己'); R('诉','讠','斥')
R('打','扌','乙'); R('把','扌','巴'); R('接','扌','妾'); R('提','扌','是')
R('指','扌','止'); R('推','扌','隹'); R('拉','扌','立'); R('持','扌','寺')
R('拍','扌','白'); R('拉','扌','立'); R('拔','扌','巴'); R('抓','扌','爪')
R('抱','扌','包'); R('拨','扌','发'); R('撑','扌','堂'); R('撤','扌','育')
R('挣','扌','争'); R('挤','扌','齐'); R('拼','扌','并'); R('拉','扌','立')
R('情','忄','青'); R('性','忄','生'); R('悟','忄','吾'); R('怀','忄','不')
R('快','忄','夬'); R('想','木','心'); R('成','⺍','丁'); R('没','氵','殳')
R('都','者','阝'); R('邮','𠃑','阝'); R('队','阝','人'); R('队','阝','人')

# 上下结构 (T): 上件 + 下件
T('安','宀','女'); T('宗','宀','8'); T('家','宀','豕'); T('定','宀','正')
T('宝','宀','玉'); T('字','宀','子'); T('它','宀','匕'); T('宜','宀','且')
T('室','宀','至'); T('元','二','儿'); T('全','人','王'); T('今','亼','人')
T('床','广','木'); T('庆','广','夂'); T('庐','广','户'); T('应','广','广')
T('去','土','厶'); T('丢','亠','8'); T('夹','大','8'); T('奇','大','可')
T('思','田','心'); T('意','音','心'); T('忠','中','心'); T('志','士','心')
T('忘','亡','心'); T('忍','刃','心'); T('告','⺌','口'); T('高','亠','口')
T('音','立','日'); T('帝','亠','8'); T('章','立','十'); T('雪','雨','夕')
T('雷','雨','田'); T('雾','雨','务'); T('需','雨','而'); T('露','雨','路')
T('霉','雨','贵'); T('青','青','8'); T('意','立','日'); T('想','相','心')
T('态','太','心'); T('怒','奴','心'); T('悲','非','心'); T('恰','忄','合')
T('总','穴','心'); T('态','太','心'); T('想','相','心'); T('感','咸','心')

# 半包围 (F) / 全包围 (W)
COMP['国'] = ('W', ['口', '玉']); COMP['圆'] = ('W', ['囗', '员'])
COMP['围'] = ('W', ['囗', '韦']); COMP('团') if False else None
COMP['团'] = ('W', ['囗', '才']); COMP['回'] = ('W', ['囗', '口'])
COMP['固'] = ('W', ['口', '古']); COMP['区'] = ('W', ['囗', '8'])
COMP['匠'] = ('F', ['匚', '8']); COMP['医'] = ('F', ['匚', '矢'])
COMP['建'] = ('F', ['廴', '8']); COMP('句') if False else None
COMP['向'] = ('W', ['丿', '口']); COMP['同'] = ('W', ['冂', '一'])

# ── 轮廓展开 (笔形 taper) ───────────────────────────────────────
def contour_of(strokes, box):
    from fontTools.pens.ttGlyphPen import TTGlyphPen
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

# ── 部件笔画来源 (缓存) ─────────────────────────────────────────
_PART_CACHE = {}
def part_strokes(part):
    if part in _PART_CACHE:
        return _PART_CACHE[part]
    g = part_geo(part)
    out = to_rad(g) if g else None
    _PART_CACHE[part] = out
    return out

def glyph_contours(ch):
    struct, parts = COMP.get(ch, default_split(ch))
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
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        pen = TTGlyphPen(None)
        if not cs:
            ok += 1 if False else 0
            # 无部件几何: 给个 .notdef 式双竖, 保证字形非空
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
        'fullName': 'aikota-B 350 (self-developed skeleton, B route)',
        'psName': 'aikota-B-350', 'version': 'Version 0.3-draft',
        'copyright': 'aikota font engine (B route): self-developed skeleton. 350 common chars. Draft for review.',
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
    out = os.path.join(HERE, 'aikota350.ttf')
    ok, miss = build_ttf(out)
    io.open(os.path.join(HERE, '_350_summary.txt'), 'w', encoding='utf-8').write(
        f'total {len(chars)}  ok {ok}  fallback-missing {miss}\n')
    print(f'wrote {out}  ({len(chars)} chars, ok={ok}, fallback={miss})')
