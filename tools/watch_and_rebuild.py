# -*- coding: utf-8 -*-
"""监视四个组件子页面，任一文件被改动后自动重建四合一页。

只用标准库（mtime 轮询），不需要安装任何依赖。
用法：python tools/watch_and_rebuild.py     按 Ctrl+C 停止
"""
import datetime
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(BASE, "tools", "build_all_in_one.py")
TARGET = os.path.join(BASE, "reactbits-all-in-one.html")

SOURCES = [
    "circular-carousel-preview.html",
    "techtext-preview.html",
    "shinytext-preview.html",
    "crystalized-ball-preview.html",
    "weavesilk-preview.html",
]

POLL = 1.2      # 轮询间隔（秒）
SETTLE = 0.9    # 检测到变化后等待落盘的时间（秒）


def snapshot():
    out = {}
    for name in SOURCES:
        path = os.path.join(BASE, name)
        try:
            out[name] = os.path.getmtime(path)
        except OSError:
            out[name] = None
    return out


def log(msg):
    print("[%s] %s" % (datetime.datetime.now().strftime("%H:%M:%S"), msg), flush=True)


def build():
    proc = subprocess.run([sys.executable, BUILD], capture_output=True)
    out = (proc.stdout or b"").decode("utf-8", "replace").strip()
    err = (proc.stderr or b"").decode("utf-8", "replace").strip()
    return proc.returncode == 0, out, err


def main():
    log("自动重建已启动")
    for name in SOURCES:
        exists = "OK" if os.path.exists(os.path.join(BASE, name)) else "缺失"
        log("  监视 %-32s %s" % (name, exists))
    log("改动以上任一文件后，会自动重建 " + os.path.basename(TARGET))
    log("按 Ctrl+C 停止")

    state = snapshot()
    while True:
        time.sleep(POLL)
        current = snapshot()
        changed = [n for n in SOURCES if current.get(n) != state.get(n)]
        if not changed:
            continue
        time.sleep(SETTLE)
        state = snapshot()
        log("检测到改动：" + "、".join(changed))
        ok, out, err = build()
        if ok:
            size = os.path.getsize(TARGET) / 1048576
            log("已重建 %s（%.2f MB）" % (os.path.basename(TARGET), size))
        else:
            log("重建失败：")
            log("  " + (err or out or "未知错误").replace("\n", "\n  "))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("已停止")
