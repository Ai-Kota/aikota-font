# -*- coding: utf-8 -*-
"""探针: 检查部件码点匹配 (避免 shell 转义干扰), 统计 350 字部件覆盖"""
import unicodedata, io

chars = open(os.path.join(os.path.dirname(__file__), '../data/350chars.txt'), encoding='utf-8').read().split()

# 部件名 → 码点列表 (按 Unicode 字形; 氵 等 3 画部件是单个码点)
RAD = {
    '氵': 0x6C35, '讠': 0x8BB1, '忄': 0x5FC4, '扌': 0x624C, '钅': 0x9485,
    '阝': 0x963F, '犭': 0x73AD, '礻': 0x79BB, '衤': 0x8865, '艹': 0+0,  # 占位
    '米': 0x7C73, '贝': 0x8D1D, '虫': 0x866B, '鱼': 0x9C7C, '鸟': 0x9E1F,
    '马': 0x9A6C, '页': 0x9875, '足': 0x8DB3, '刀': 0x5200, '弓': 0x5F13,
    '矢': 0x77E2, '目': 0x76EE, '耳': 0x8033, '气': 0x6C14, '土': 0x571F,
    '女': 0x5973, '力': 0x529B, '又': 0x53C8, '尸': 0x5C38, '骨': 0x9AA8,
    '雨': 0x96E8, '口': 0x53E3, '亻': 0x4EA3, '王': 0x738B, '车': 0x8F66,
    '金': 0x91D1, '木': 0x6728, '大': 0x5927, '小': 0x5C0F, '二': 0x4E8C,
    '十': 0x5341, '工': 0x5DE5, '广': 0x5E7F, '疒': 0x75E6, '火': 0x706B,
    '日': 0x65E5, '月': 0x6708, '山': 0x5C71, '石': 0x77F3, '田': 0x7530,
    '禾': 0x79BE, '竹': 0x7B92, '纟': 0+0, '立': 0x7ACB,
}
# 艹/纟 码点需确认; 先只测已确认码点的部件
known = {k: v for k, v in RAD.items() if v}
import collections
cnt = collections.Counter()
hits_chars = []
for c in chars:
    cps = set(ord(x) for x in c)
    hit = None
    for name, cp in known.items():
        if cp in cps:
            hit = name; break
    if hit:
        cnt[hit] += 1
        hits_chars.append((c, hit))

out = io.open('E:/AImlyForge/scratch/aikota-font/_probe_result.txt', 'w', encoding='utf-8')
out.write(f'radical-prefixed chars: {len(hits_chars)}/{len(chars)}\n')
out.write('sample: ' + ' '.join(f'{c}←{h}' for c, h in hits_chars[:30]) + '\n')
out.write('counts: ' + str(dict(cnt.most_common(40))) + '\n')
out.close()
print('done, see _probe_result.txt')
