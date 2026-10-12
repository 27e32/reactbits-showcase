# -*- coding: utf-8 -*-
"""把四个组件预览页合成一个带顶部标签栏的单文件页面。

做法：四个子页面整体内联成 JS 字符串，运行时交给各自的 iframe 渲染（srcdoc）。
子页面之间样式与脚本完全隔离，但最终只有一个 .html 文件。
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "reactbits-all-in-one.html")

# key, 标签栏显示名（中文）, 标签栏右侧说明（带英文原名）, 文件名
# 顺序 = 标签栏顺序，第一个即默认打开的标签
FILES = [
    ("carousel", "圆环轮播", "CircularCarousel · 3D 圆环图片轮播，内置十二月人像，可上传本地图片", "circular-carousel-preview.html"),
    ("techtext", "技术文字", "TechText · 字母在指针附近溶解为虚线矢量轮廓，可拖离基线", "techtext-preview.html"),
    ("shinytext", "流光文字", "ShinyText · 金属高光带扫过文字，可调角度/宽度/光带数/辉光", "shinytext-preview.html"),
    ("crystalized", "结晶球", "CrystalizedBall · WebGL2 + GPGPU 粒子星云球，指针感应、点击搅散", "crystalized-ball-preview.html"),
    ("weavesilk", "丝绸光绘", "WeaveSilk · 镜像对称的发光丝线，按住鼠标拖动即可绘制", "weavesilk-preview.html"),
]


def encode(html):
    """转成可安全放进 <script> 的 JS 字符串字面量。
    关键：把 </ 变成 <\\/ ，否则字符串里的 </script> 会提前结束外层脚本。"""
    return json.dumps(html, ensure_ascii=False).replace("</", "<\\/")


pages_js = []
meta_js = []
total = 0

for key, name, desc, filename in FILES:
    path = os.path.join(BASE, filename)
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    total += len(html)
    pages_js.append('  "%s": %s' % (key, encode(html)))
    meta_js.append('  "%s": { name: %s, desc: %s }' % (
        key, json.dumps(name, ensure_ascii=False), json.dumps(desc, ensure_ascii=False)))
    print("%-14s %-30s %6.1f KB" % (key, filename, len(html) / 1024))

PAGES = "{\n" + ",\n".join(pages_js) + "\n}"
META = "{\n" + ",\n".join(meta_js) + "\n}"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>React Bits 组件预览台 · 四合一</title>
<style>
  *{box-sizing:border-box}
  html,body{
    height:100%;margin:0;background:#0a0b0d;color:#e8ebef;overflow:hidden;
    font-family:'Inter',ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
  }
  #bar{
    position:fixed;top:0;left:0;right:0;height:48px;z-index:10;
    display:flex;align-items:center;gap:16px;padding:0 16px;
    background:#0c0e12;border-bottom:1px solid rgba(255,255,255,.09);
  }
  #bar .brand{
    font-size:12px;font-weight:600;letter-spacing:.06em;
    color:rgba(255,255,255,.78);flex:0 0 auto;white-space:nowrap;
  }
  #bar .brand em{font-style:normal;color:rgba(255,255,255,.28);font-weight:400;margin-left:7px}
  #tabs{display:flex;gap:4px;flex:0 0 auto}
  #tabs button{
    appearance:none;border:1px solid transparent;background:transparent;
    color:rgba(255,255,255,.5);font:inherit;font-size:12px;
    padding:5px 12px;border-radius:8px;cursor:pointer;
    transition:background .15s,color .15s;white-space:nowrap;
  }
  #tabs button:hover{color:#fff;background:rgba(255,255,255,.06)}
  #tabs button.on{color:#0a0b0d;background:#fff;font-weight:600}
  #desc{
    flex:1;min-width:0;text-align:right;
    font-size:11px;color:rgba(255,255,255,.3);letter-spacing:.02em;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  }
  #view{position:fixed;top:48px;left:0;right:0;bottom:0}
  #view iframe{width:100%;height:100%;border:0;display:block;background:#0a0b0d}
  @media (max-width:900px){
    #bar .brand em,#desc{display:none}
  }
  @media (max-width:820px){
    #bar{height:44px;padding:0 10px;gap:10px}
    #bar .brand{display:none}
    #tabs{flex:1;min-width:0;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
    #tabs::-webkit-scrollbar{display:none}
    #tabs button{padding:4px 10px;font-size:11.5px;flex:0 0 auto}
    #view{top:44px}
  }
</style>
</head>
<body>
<div id="bar">
  <span class="brand">React Bits<em>组件预览台</em></span>
  <nav id="tabs"></nav>
  <span id="desc"></span>
</div>
<div id="view"></div>

<script>
var PAGES = __PAGES__;
var META = __META__;

(function () {
  'use strict';
  var tabsEl = document.getElementById('tabs');
  var viewEl = document.getElementById('view');
  var descEl = document.getElementById('desc');
  var keys = Object.keys(META);
  var frames = {};
  var current = null;

  function bindKeys(doc) {
    doc.addEventListener('keydown', function (e) {
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      var n = parseInt(e.key, 10);
      if (n >= 1 && n <= keys.length) { show(keys[n - 1]); return; }
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        var idx = keys.indexOf(current);
        if (idx < 0) return;
        var next = e.key === 'ArrowRight' ? idx + 1 : idx - 1;
        if (next >= 0 && next < keys.length) show(keys[next]);
      }
    });
  }

  keys.forEach(function (key, i) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = META[key].name;
    btn.dataset.k = key;
    btn.title = '快捷键 ' + (i + 1);
    btn.addEventListener('click', function () { show(key); });
    tabsEl.appendChild(btn);

    var frame = document.createElement('iframe');
    frame.dataset.k = key;
    frame.dataset.loaded = '0';
    frame.style.display = 'none';
    frame.setAttribute('title', META[key].name);
    frame.setAttribute('allow', 'autoplay; fullscreen; clipboard-write');
    frame.addEventListener('load', function () {
      // srcdoc 与外层同源，可以把快捷键接进子页面
      try { bindKeys(frame.contentDocument); } catch (err) {}
    });
    viewEl.appendChild(frame);
    frames[key] = frame;
  });

  function show(key) {
    if (!META[key]) return;
    keys.forEach(function (k) {
      var f = frames[k];
      var on = k === key;
      if (on && f.dataset.loaded === '0') {
        f.srcdoc = PAGES[k];      // 懒加载：第一次切换进来才解析
        f.dataset.loaded = '1';
      }
      f.style.display = on ? 'block' : 'none';
    });
    Array.prototype.forEach.call(tabsEl.children, function (b) {
      b.classList.toggle('on', b.dataset.k === key);
    });
    descEl.textContent = META[key].desc;
    document.title = META[key].name + ' · React Bits 预览台';
    current = key;
    try { history.replaceState(null, '', '#' + key); } catch (e) {}
  }

  bindKeys(document);
  var initial = (location.hash || '').replace('#', '');
  show(META[initial] ? initial : keys[0]);
})();
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__PAGES__", PAGES).replace("__META__", META)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html)

print("---")
print("子页面合计 %d 字节 (%.2f MB)" % (total, total / 1048576))
print("合成文件 %s (%.2f MB)" % (os.path.basename(OUT), os.path.getsize(OUT) / 1048576))
