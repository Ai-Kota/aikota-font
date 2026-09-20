# -*- coding: utf-8 -*-
"""
aikota-font · 摆位规则 (B 路线自有 IP: 摆位公式 = 你的设计)
================================================================
把字拆成部件 + 结构类型后, 按 1000upm 网格分配每个部件的坐标盒.
坐标: 原点在左下, y 向上. 基线 y=120, 顶线 y=880 (与 A 路线一致).

结构类型:
  O 独体        部件占满全格
  R 左右        左 40% / 右 60% (窄旁如 氵讠阝 用 30/70)
  L 左中右     30/40/30
  T 上下        上 55% / 下 45% (窄头如 艹 刂 用 40/60)
  B 上中下     上 40% / 中 35% / 下 25%
  F 半包围     口字框 / 门字框 / 厂字框
  W 全包围     囗 (外框 + 内件, 内件占中 55%)

笔画类型 (笔形算法用, 与 style_engine_v2 对齐):
  H=横 V=竖 PIE=撇 NA=捺 DIAN=点 ZHE=折 HOOK=钩
"""

UPM = 1000
BASELINE = 120
TOP = 880
GAP = 30          # 部件间距
NARROW_PARTS = set("氵讠阝犭衤忄礻犭")  # 窄旁, 左右结构占 30%

# 部件宽高比 (用于 T/B 结构定宽度): 部件名 → (宽比, 高比), 相对其占格
def part_box(structure, parts, cx_box, cy_box, cw, ch):
    """按结构把 (cx_box,cy_box,cw,ch) 分给各部件, 返回 [(x,y,w,h), ...]
    坐标为各部件左上角 + 宽高."""
    out = []
    x0, y0 = cx_box, cy_box
    if structure == "O":
        out.append((x0, y0, cw, ch))
    elif structure == "R":
        nw = int(cw * (0.30 if parts[0] in NARROW_PARTS else 0.40))
        out.append((x0, y0, nw, ch))
        out.append((x0 + nw + GAP, y0, cw - nw - GAP, ch))
    elif structure == "L":
        w1 = int(cw * 0.30); w2 = int(cw * 0.40)
        out.append((x0, y0, w1, ch))
        out.append((x0 + w1 + GAP, y0, w2, ch))
        out.append((x0 + w1 + w2 + 2 * GAP, y0, cw - w1 - w2 - 2 * GAP, ch))
    elif structure == "T":
        nh = int(ch * (0.40 if parts[0] in ("艹", "刂", "冖", "宀") else 0.55))
        out.append((x0, y0, cw, nh))
        out.append((x0, y0 + nh + GAP, cw, ch - nh - GAP))
    elif structure == "B":
        nh1 = int(ch * 0.40); nh2 = int(ch * 0.35)
        out.append((x0, y0, cw, nh1))
        out.append((x0, y0 + nh1 + GAP, cw, nh2))
        out.append((x0, y0 + nh1 + nh2 + 2 * GAP, cw, ch - nh1 - nh2 - 2 * GAP))
    elif structure == "F":  # 半包围 (外框类, 内件居中偏下)
        out.append((x0, y0, cw, ch))       # 框
        out.append((x0 + cw // 4, y0 + int(ch * 0.30), cw // 2, int(ch * 0.40)))  # 内件
    elif structure == "W":  # 全包围
        out.append((x0, y0, cw, ch))
        out.append((x0 + cw // 5, y0 + ch // 5, cw * 3 // 5, ch * 3 // 5))
    else:
        raise ValueError("unknown structure " + structure)
    return out


def scale_strokes(strokes, box, full_box_w=UPM):
    """把部件自身坐标系 (0..1000) 的笔画缩放到实际盒子.
    strokes: [(stk, x, y, dx, dy, w)]  部件内部坐标 0..1000
    返回放大平移后的笔画 (坐标 + 宽度)."""
    x0, y0, w, h = box
    sx = w / full_box_w
    sy = h / full_box_w
    scaled = []
    for (stk, px, py, dx, dy, sw) in strokes:
        scaled.append((stk,
                       int(x0 + px * sx),
                       int(y0 + (1000 - py) * sy),  # y 轴翻转
                       int(dx * sx),
                       -int(dy * sy),
                       int(sw * max(sx, sy))))
    return scaled
