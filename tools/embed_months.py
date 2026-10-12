# -*- coding: utf-8 -*-
"""把 12 张月度人像以 base64 形式内嵌进预览页，替换原来的 Unsplash 外链。"""
import json
import os
import re

BASE = r"E:\WorkBuddy工作空间\2026-10-10-16-04-42"
HTML = os.path.join(BASE, "circular-carousel-preview.html")
DATA = os.path.join(BASE, "assets", "months", "final", "months-data.json")

META = [
    ("一月", "初雪", "一月 · 初雪"),
    ("二月", "温室", "二月 · 温室"),
    ("三月", "樱花", "三月 · 樱"),
    ("四月", "新绿", "四月 · 新绿"),
    ("五月", "花野", "五月 · 花野"),
    ("六月", "海", "六月 · 海"),
    ("七月", "盛夏", "七月 · 盛夏"),
    ("八月", "晚霞", "八月 · 晚霞"),
    ("九月", "芦苇", "九月 · 芦苇"),
    ("十月", "枫", "十月 · 枫"),
    ("十一月", "晨雾", "十一月 · 晨雾"),
    ("十二月", "冬夜", "十二月 · 冬夜"),
]

with open(DATA, encoding="utf-8") as fh:
    items = json.load(fh)

with open(HTML, encoding="utf-8") as fh:
    html = fh.read()

# ---- 1. 重建 DEFAULT_ITEMS ----
rows = ["  const DEFAULT_ITEMS = ["]
for idx, it in enumerate(items):
    title, subtitle, alt = META[idx]
    rows.append(
        "    { src: '%s', alt: '%s', title: '%s', subtitle: '%s' },"
        % (it["src"], alt, title, subtitle)
    )
rows[-1] = rows[-1].rstrip(",")
rows.append("  ];")
block = "\n".join(rows)

new_html, n = re.subn(r"  const DEFAULT_ITEMS = \[[\s\S]*?\n  \];", block, html, count=1)
if n != 1:
    raise SystemExit("DEFAULT_ITEMS 未匹配到")
html = new_html

# ---- 2. photo() 函数已不再需要，替换成说明注释 ----
html = html.replace(
    "  const photo = id => `https://images.unsplash.com/${id}?w=900&q=80&auto=format&fit=max&sat=-100`;",
    "  // 原组件此处用 Unsplash 外链生成默认图，本预览页已改为内嵌 12 张本地图片，不再依赖网络"
)

# ---- 3. 更新上传区提示文案 ----
html = html.replace(
    '<div id="upNote">当前使用默认示例图（来自 Unsplash，需联网）。上传后会自动替换。</div>',
    '<div id="upNote">已内置 12 张「十二月」主题人像（base64 内嵌，完全离线可用）。上传自己的图片会替换它们。</div>'
)
html = html.replace(
    "    upNote.textContent = '当前使用默认示例图（来自 Unsplash，需联网）。上传后会自动替换。';",
    "    upNote.textContent = '已恢复内置的 12 张「十二月」主题人像。';"
)

# ---- 4. 底部提示补一句 ----
html = html.replace(
    "横向拖拽或滚轮左右滚动 · 点击卡片聚焦到它 · 悬停会暂停自动旋转",
    "横向拖拽或滚轮左右滚动 · 点击卡片聚焦到它 · 面板里打开「显示标题」可看到月份名"
)

with open(HTML, "w", encoding="utf-8") as fh:
    fh.write(html)

print("已内嵌 %d 张图片" % len(items))
print("HTML 大小: %.2f MB" % (os.path.getsize(HTML) / 1048576))
