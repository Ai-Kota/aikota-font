# -*- coding: utf-8 -*-
"""渲染对比: 本引擎 verify_a8.ttf vs Arphic 数据路线 aikota-regular.ttf (v0.2.0)"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
chars = "日月口国山水木天告"

B = os.path.join(HERE, "verify_a8.ttf")
A = "E:/AImlyForge/releases/cjk-font-foundry/v0.2.0/aikota-regular.ttf"

fB = ImageFont.truetype(B, 140)
fA = ImageFont.truetype(A, 140)

W, H = 560, 380
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
d.text((10, 5), "A route (Arphic data, aikota v0.2.0)", fill="gray")
d.text((10, 195), "B route (aikota scaffold draft)", fill="gray")
x = 10
for c in chars:
    d.text((x, 40), c, font=fA, fill="black")
    d.text((x, 230), c, font=fB, fill="#0033cc")
    x += 58
img.save(os.path.join(HERE, "cmp_8char.png"))
print("wrote cmp_8char.png")
