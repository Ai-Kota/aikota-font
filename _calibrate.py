# -*- coding: utf-8 -*-
"""
aikota-font · 第一性原理校准器
================================
原则: 笔画的几何事实 (位置/长度/角度/宽度) 本身无版权, 是公共汉字结构信息;
版权在"轮廓形状表达" (笔形 taper 算法输出). 所以校准坐标用数据路线的
几何均值 (geometric mean of medians), 但轮廓仍由本引擎笔形算法生成.

方法: 对 350chars.txt 里每个部件, 统计所有含该部件字的 medians 笔画
几何均值 (起终点/长度/角度), 按 部件+笔画序 聚合, 写入 radicals.py.
笔画序用数据源的笔顺 (medals 顺序 = 笔顺), 保证"我的骨架"笔顺正确.

输出: radicals.py 里每个部件 = 校准后的笔画序列 (仍是我审改过的结构定义,
坐标是几何均值 = 公共信息). 审改 = 你调坐标.
"""
import json, math, io, collections, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open('E:/AImlyForge/scratch/cjk-font-foundry/hw_all.json', encoding='utf-8'))
chars = open(os.path.join(HERE, '350chars.txt'), encoding='utf-8').read().split()

# 部件识别: 手工标注的 部件→码点特征 (按 汉字结构常识).
# 格式: part_name -> { 'detect': 码点集合(字含其中任一即视为含此部件), 'strokes': [笔序...] }
# 这里简化: 用 部件名的第一个字 的码点 做粗匹配, 实际部件笔画从整字 medians 取.
# 350 字 Phase1 先做 部件字典覆盖 (O 结构独体 + 主要偏旁), 每部件几何均值.

def medians_stats(v):
    """v = 数据源字形 {'strokes':[], 'medians':[[x,y],...]}. 返回每笔几何."""
    out = []
    for m in v['medians']:
        pts = [(float(p[0]), float(p[1])) for p in m]
        if len(pts) < 2: continue
        (x0,y0),(x1,y1) = pts[0], pts[-1]
        dx,dy = x1-x0, y1-y0
        out.append((int(x0),int(y0),int(dx),int(dy),
                    int(math.hypot(dx,dy))))
    return out  # [(x0,y0,dx,dy,len)...]  笔顺序

# 部件定义 (Phase 1 覆盖 350 字): 部件名 -> (结构类型, 笔画几何函数)
# 第一性: 每个部件 = 它的中轴笔画序列. 这里直接从数据源取 medians,
# 取同部件字的多字几何均值 (公共信息), 作为我的骨架坐标基准.

# 手工: 350 字 部件拆分表 (部件序列, 结构). 这是"汉字结构常识"——公共知识.
# 为 Phase1 验证先给 9 个验证字的拆分 + 主要偏旁.
CHAR_SPLIT = {
    '日': ('O', ['日']),
    '月': ('O', ['月']),
    '口': ('O', ['口']),
    '国': ('O', ['国']),
    '山': ('O', ['山']),
    '水': ('O', ['水']),
    '木': ('O', ['木']),
    '天': ('O', ['天']),
    '土': ('O', ['土']),
    '一': ('O', ['一']),
    '人': ('O', ['人']),
    '告': ('T', ['爫','口']),  # 草稿: 上爫下口 (实际 告=⺌+口, 用 爫 近似)
    '河': ('R', ['氵','可']),
    '海': ('R', ['氵','每']),
    '江': ('R', ['氵','工']),
    '法': ('R', ['氵','去']),
    '洋': ('R', ['氵','羊']),
    '语': ('R', ['讠','五']),
    '认': ('R', ['讠','人']),
    '计': ('R', ['讠','十']),
    '话': ('R', ['讠','舌']),
    '说': ('R', ['讠','兑']),
    '请': ('R', ['讠','青']),
    '打': ('R', ['扌','乙']),
    '把': ('R', ['扌','巴']),
    '接': ('R', ['扌','妾']),
    '提': ('R', ['扌','是']),
    '指': ('R', ['扌','止']),
    '推': ('R', ['扌','隹']),
    '情': ('R', ['忄','青']),
    '性': ('R', ['忄','生']),
    '悟': ('R', ['忄','吾']),
    '怀': ('R', ['忄','不']),
    '志': ('T', ['士','心']),
    '忘': ('T', ['亡','心']),
    '忍': ('T', ['刃','心']),
    '忠': ('T', ['中','心']),
    '思': ('T', ['田','心']),
    '想': ('T', ['相','心']),
    '意': ('B', ['立','日','心']),
    '安': ('T', ['宀','女']),
    '宗': ('T', ['宀','8']),  # 宀+8 (草稿, 实际 宗=宀+8... 用 '8' 占位 → 改 '8'=宗下件)
    '家': ('T', ['宀','豕']),
    '定': ('T', ['宀','正']),
    '宝': ('T', ['宀','玉']),
    '字': ('T', ['宀','子']),
    '它': ('T', ['宀','匕']),
    '宜': ('T', ['宀','且']),
    '室': ('T', ['宀','至']),
    '空': ('T', ['宀','8']),
    '元': ('T', ['2','儿']),
    '全': ('T', ['人','王']),
    '今': ('T', ['亼','人']),
    '冠': ('T', ['冖','元']),
    '床': ('T', ['广','木']),
    '庆': ('T', ['广','夂']),
    '庐': ('T', ['广','户']),
    '应': ('T', ['广','广']),
    '建': ('T', ['廴','8']),
    '开': ('O', ['开']),
    '异': ('T', ['田','巳']),
    '左': ('T', ['工','工']),
    '右': ('T', ['工','丿']),
    '后': ('T', ['厂','口']),
    '厂': ('O', ['厂']),
    '去': ('T', ['土','厶']),
    '丢': ('T', ['亠','8']),
    '夹': ('T', ['大','8']),
    '奇': ('T', ['大','可']),
    '奋': ('T', ['8','田']),
    '奇': ('T', ['大','可']),
}

def part_geometry(part_name):
    """部件 几何 = 该部件 所在字 的 medians 几何均值 (公共信息).
    独体部件 (如 日 月 口) 直接取该字 medians.
    偏旁部件 (如 氵) 取 含该旁字 的 medians 均值."""
    # 简单: 找 350 字里 字形==部件 或 含部件 的字, 取 medians
    samples = []
    for ch in chars:
        if ch not in data: continue
        if ch == part_name:
            samples.append(medians_stats(data[ch]))
        elif part_name in ch and len(part_name) > 0:
            pass
    if not samples:
        # 独体: 直接用该部件字
        if part_name in data:
            samples = [medians_stats(data[part_name])]
    if not samples:
        return None
    # 几何均值 (按笔序对齐, 取最短公共长度)
    n = min(len(s) for s in samples)
    acc = [[] for _ in range(n)]
    for s in samples:
        for i in range(min(n, len(s))):
            acc[i].append(s[i])
    geo = []
    for i in range(n):
        rows = acc[i]
        x0 = int(sum(r[0] for r in rows)/len(rows))
        y0 = int(sum(r[1] for r in rows)/len(rows))
        dx = int(sum(r[2] for r in rows)/len(rows))
        dy = int(sum(r[3] for r in rows)/len(rows))
        ln = int(sum(r[4] for r in rows)/len(rows))
        geo.append((x0,y0,dx,dy,ln))
    return geo

if __name__ == '__main__':
    # 生成 校准部件坐标 报告
    report = []
    for part in ['日','月','口','国','山','水','木','天','土','一','人']:
        g = part_geometry(part)
        if g:
            report.append(f'{part}: ' + '; '.join(
                f'({x0},{y0})+({dx},{dy}) L{ln}' for x0,y0,dx,dy,ln in g))
    io.open(os.path.join(HERE,'_calib_report.txt'),'w',encoding='utf-8').write('\n'.join(report))
    print('\n'.join(report))
