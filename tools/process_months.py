# -*- coding: utf-8 -*-
"""把 12 张月度人像处理成可内嵌的压缩图：
   裁掉右下角 AI 水印 -> 正方形 -> 缩放到 640 -> JPEG -> base64
"""
import base64
import json
import os
import sys

from PIL import Image

BASE = r"E:\WorkBuddy工作空间\2026-10-10-16-04-42\assets\months"
OUT_DIR = os.path.join(BASE, "final")
os.makedirs(OUT_DIR, exist_ok=True)

# 裁剪比例：底部切掉多少、左右各切掉多少（保持正方形）
CUT_BOTTOM = 0.075
CUT_SIDE = 0.038
SIZE = 640
QUALITY = 82

TITLES = [
    ("January", "Winter", "一月 · 初雪"),
    ("February", "Greenhouse", "二月 · 温室"),
    ("March", "Blossom", "三月 · 樱"),
    ("April", "New Green", "四月 · 新绿"),
    ("May", "Meadow", "五月 · 花野"),
    ("June", "Sea", "六月 · 海"),
    ("July", "High Summer", "七月 · 盛夏"),
    ("August", "Dusk", "八月 · 晚霞"),
    ("September", "Reeds", "九月 · 芦苇"),
    ("October", "Maple", "十月 · 枫"),
    ("November", "Fog", "十一月 · 晨雾"),
    ("December", "Winter Night", "十二月 · 冬夜"),
]

items = []
report = []

for i in range(1, 13):
    folder = os.path.join(BASE, "m%02d" % i)
    if not os.path.isdir(folder):
        report.append("m%02d 目录不存在" % i)
        continue
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    if not files:
        report.append("m%02d 没有图片" % i)
        continue

    src = os.path.join(folder, files[0])
    img = Image.open(src).convert("RGB")
    w, h = img.size

    cb = int(h * CUT_BOTTOM)
    cs = int(w * CUT_SIDE)
    img = img.crop((cs, 0, w - cs, h - cb))

    w2, h2 = img.size
    s = min(w2, h2)
    left = (w2 - s) // 2
    top = (h2 - s) // 2
    img = img.crop((left, top, left + s, top + s))
    img = img.resize((SIZE, SIZE), Image.LANCZOS)

    dst = os.path.join(OUT_DIR, "month-%02d.jpg" % i)
    img.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    size = os.path.getsize(dst)

    with open(dst, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")

    en, sub, cn = TITLES[i - 1]
    items.append({
        "n": i,
        "src": "data:image/jpeg;base64," + b64,
        "alt": "Month %02d portrait" % i,
        "title": en,
        "subtitle": sub,
        "cn": cn,
    })
    report.append("m%02d -> %s  %d KB  (原图 %dx%d)" % (i, os.path.basename(dst), size // 1024, w, h))

data_path = os.path.join(OUT_DIR, "months-data.json")
with open(data_path, "w", encoding="utf-8") as fh:
    json.dump(items, fh, ensure_ascii=False)

total = sum(len(it["src"]) for it in items)
print("\n".join(report))
print("---")
print("共 %d 张，base64 合计 %.2f MB" % (len(items), total / 1048576))
print("数据文件: " + data_path)
