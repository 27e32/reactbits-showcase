# -*- coding: utf-8 -*-
"""给 5 个组件预览页注入移动端适配：窄屏时右侧面板变底部抽屉。

幂等：重复运行不会重复注入（靠 MOBILE_MARK 标记判断）。
"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    "techtext-preview.html",
    "shinytext-preview.html",
    "crystalized-ball-preview.html",
    "circular-carousel-preview.html",
    "weavesilk-preview.html",
]

MOBILE_MARK = "mobile-adapt-v1"

CSS = r"""
  /* ================= 移动端适配 (mobile-adapt-v1) ================= */
  @media (max-width: 820px){
    /* 画布吃满整个视口，并接管触摸手势（几个页面都是全屏交互画布，不需要页面滚动） */
    #stage{
      height: 100vh;
      height: 100dvh;
      touch-action: none;
    }
    /* 底部提示在窄屏会换行挡内容，直接隐藏 */
    #hint{ display: none; }
    /* 诊断信息移到顶部，抽屉展开时也能看到 */
    #stats{
      top: 10px;
      bottom: auto;
      left: 12px;
      right: 12px;
      font-size: 9.5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    /* 控制面板改造成底部抽屉：默认只露出顶部 50px */
    #panel{
      top: auto;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100%;
      height: 64vh;
      height: 64dvh;
      max-height: none;
      border-radius: 16px 16px 0 0;
      border-left: 0;
      border-right: 0;
      border-bottom: 0;
      transform: translateY(calc(100% - 50px));
      transition: transform .3s cubic-bezier(.22,1,.36,1);
      padding-bottom: env(safe-area-inset-bottom, 0);
    }
    #panel.open{ transform: translateY(0); }
    #panel header{
      position: relative;
      padding-top: 17px;
      cursor: pointer;
      -webkit-user-select: none;
      user-select: none;
    }
    /* 抽屉把手 */
    #panel header::before{
      content: '';
      position: absolute;
      top: 7px;
      left: 50%;
      transform: translateX(-50%);
      width: 40px;
      height: 4px;
      border-radius: 99px;
      background: rgba(255,255,255,.22);
    }
  }
"""

JS = r"""
  /* ================= 移动端：点面板标题栏展开/收起抽屉 (mobile-adapt-v1) ================= */
  (function(){
    var panel = document.getElementById('panel');
    if (!panel) return;
    var header = panel.querySelector('header');
    if (!header) return;
    header.addEventListener('click', function(e){
      // 别抢走「折叠」按钮的点击
      if (e.target && e.target.closest && e.target.closest('button')) return;
      panel.classList.toggle('open');
    });
  })();
"""


def main():
    for name in FILES:
        path = os.path.join(BASE, name)
        if not os.path.exists(path):
            print("跳过（不存在）: " + name)
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()

        if MOBILE_MARK in html:
            print("已注入过，跳过: " + name)
            continue

        if "</style>" not in html or "</script>" not in html:
            print("结构异常，跳过: " + name)
            continue

        html = html.replace("</style>", CSS + "\n</style>", 1)
        html = html.replace("</script>", JS + "\n</script>", 1)

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("已注入: %-32s %6.1f KB" % (name, len(html) / 1024))


if __name__ == "__main__":
    main()
