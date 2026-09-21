#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_watermark.py - Verify watermark in TTF font"""
import sys
from fontTools.ttLib import TTFont
import hashlib

CHAN = 0x414B4F01
STRENGTH = 0.5

def wm_offset(idx, chan):
    h = hashlib.sha256(f"aikota:{chan}:{idx}".encode()).digest()
    xs = int.from_bytes(h[:4], 'big')
    ys = int.from_bytes(h[4:8], 'big')
    dx = round((xs / 0xFFFFFFFF) * 2 * STRENGTH - STRENGTH, 2)
    dy = round((ys / 0xFFFFFFFF) * 2 * STRENGTH - STRENGTH, 2)
    return dx, dy

f = TTFont(sys.argv[1] if len(sys.argv) > 1 else "aikota-c-kaiso.ttf")
gs = f.getGlyphSet()

non_empty = [(gn, g) for gn, g in gs.items()
             if hasattr(g, 'coordinates') and len(g.coordinates) > 0]
print(f"Non-empty glyphs: {len(non_empty)}")

for gn, g in non_empty[:3]:
    coords = [(c.x, c.y) for c in g.coordinates]
    print(f"\n{gn}: {len(coords)} pts")
    for i in range(min(5, len(coords))):
        edx, edy = wm_offset(i, CHAN)
        ox = coords[i][0] - edx
        oy = coords[i][1] - edy
        print(f"  v{i}: ({coords[i][0]},{coords[i][1]}) <- orig({ox:.1f},{oy:.1f}) + ({edx:+.2f},{edy:+.2f})")
f.close()
