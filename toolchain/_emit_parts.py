# -*- coding: utf-8 -*-
"""
aikota-font · 部件几何均值 自动发射器 (B 路线, 第一性原理管线)
================================================================
IP 边界 (真言三件套):
  部件拆分 = 汉字结构常识 (公共知识)
  几何均值 = 数据源 medians 数值 (公共信息)
  我的 IP = 笔形 taper 轮廓算法 + 摆位公式 layout.scale_strokes
管线: 350字 -> 部件拆分 -> 每部件 medians 几何均值 -> _mirror 坐标 -> radicals.py
"""
import json, math, io, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = open(os.path.join(HERE, '../data', '350chars.txt'), encoding='utf-8').read().split()

def stroke_geo(v):
    out = []
    for m in v['medians']:
        pts = [(float(p[0]), float(p[1])) for p in m]
        if len(pts) < 2:
            continue
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        out.append((int(x0), int(y0), int(x1 - x0), int(y1 - y0)))
    return out

# 部件 -> 几何. 独体件取自身字 medians; 偏旁件取 350 里 含该旁 的字 均值.
def part_geo(part):
    samples = []
    # 1) 部件自身是 350 里的字 / 数据源里的字: 直接取
    if part in data:
        samples.append(stroke_geo(data[part]))
    # 2) 偏旁: 找 350 里 首部件==part 的字 (旁在左/上的字)
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

def to_rad(strokes, widths=None):
    """(x0,y0,dx,dy) -> radicals 行 (font y-up), 宽度按笔画类分档.
    类型推断: |dx|>|dy|*2 -> H(0); |dy|>|dx|*2 -> V(1);
    斜: dx<0,dy<0 -> PIE(2); dx>0,dy>0 -> NA(3); 短斜 -> DIAN(4)."""
    out = []
    for i, (x0, y0, dx, dy) in enumerate(strokes):
        ln = math.hypot(dx, dy)
        if abs(dx) > abs(dy) * 2.2 and abs(dx) > 120:
            t = 0; w = 95
        elif abs(dy) > abs(dx) * 2.2 and abs(dy) > 120:
            t = 1; w = 70
        elif ln < 160:
            t = 4; w = 55  # 短斜 = 点
        elif dx < 0 and dy < 0:
            t = 2; w = 65  # 撇
        else:
            t = 3; w = 65   # 捺
        out.append((t, x0, y0, dx, dy, w))
    return out

def mirror(strokes):
    return [(t, x, 1000 - y, dx, -dy, w) for (t, x, y, dx, dy, w) in strokes]

if __name__ == '__main__':
    PARTS = ['一','二','十','土','人','口','日','月','山','水','木','天','大',
             '金','工','立','心','青','白','王','女','手','月','足','耳','田',
             '力','又','尸','氵','讠','扌','忄','宀','广','雨','艹','虫','车']
    lines = []
    for p in PARTS:
        g = part_geo(p)
        if not g:
            lines.append(f"  '{p}': MISSING")
            continue
        strokes = to_rad(g)
        lines.append(f"  '{p}': _mirror([(" +
                    '), ('.join(f'{t}, {x}, {y}, {dx}, {dy}, {w}' for t, x, y, dx, dy, w in strokes) +
                    ")]),")
    code = "\n".join(lines)
    io.open(os.path.join(HERE, '_emit_rad.py'), 'w', encoding='utf-8').write(code)
    print(f'emitted {sum(1 for l in lines if "MISSING" not in l)} parts to _emit_rad.py')
    for l in lines:
        if 'MISSING' in l: print('MISSING:', l.strip())
