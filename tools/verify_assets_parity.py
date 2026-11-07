# -*- coding: utf-8 -*-
"""
构建产物一致性（之前散落在已归档的 P0/P1 脚本里，独立出来免得跟着一起消失）：
1. 根目录 starfield.html 与 android assets 里的镜像必须字节一致；
2. service-worker.js 同样必须一致；
3. version.json / service-worker CACHE_VERSION / 设置抽屉里的版本号三处必须自洽。
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MASTER = BASE / 'starfield.html'
MIRROR = BASE / 'android' / 'app' / 'src' / 'main' / 'assets' / 'starfield.html'
SW = BASE / 'service-worker.js'
SW_MIRROR = BASE / 'android' / 'app' / 'src' / 'main' / 'assets' / 'service-worker.js'
VERSION = BASE / 'version.json'


def main():
    print('== 1. starfield.html 根目录 vs Android 镜像 ==')
    a = MASTER.read_bytes()
    b = MIRROR.read_bytes()
    assert a == b, f'字节不一致: root={len(a)} android={len(b)}；先跑 tools/generate_all_expansion_modes.py'
    print(f'  ok  {len(a):,} bytes 完全一致')

    print('== 2. service-worker.js 双份一致 ==')
    s1 = SW.read_text(encoding='utf-8')
    s2 = SW_MIRROR.read_text(encoding='utf-8')
    assert s1 == s2, 'service-worker.js 根目录与 Android 镜像不一致'
    print('  ok  两份一致')

    print('== 3. 版本号四处自洽 ==')
    meta = json.loads(VERSION.read_text(encoding='utf-8'))
    version = str(meta['version'])
    build = str(meta['build'])
    m = re.search(r"CACHE_VERSION\s*=\s*'v([0-9.]+)-b(\d+)'", s1)
    assert m, 'service-worker.js 里找不到 CACHE_VERSION'
    assert m.group(1) == version, f'service-worker 版本 {m.group(1)} != version.json {version}'
    assert m.group(2) == build, f'service-worker build {m.group(2)} != version.json {build}'
    html = MASTER.read_text(encoding='utf-8', errors='ignore')
    tag = re.search(r'id="sf-version-tag">v([0-9.]+) \(Build (\d+)\)', html)
    assert tag, '设置抽屉里找不到版本标签'
    assert tag.group(1) == version and tag.group(2) == build, (
        f'抽屉版本 v{tag.group(1)} (Build {tag.group(2)}) != version.json v{version} (Build {build})'
    )
    # 第 4 处：OTA 比较用的硬编码常量。它和 version.json 不同步的话，
    # 客户端会「拉下来还是旧 localBuild」-> 永远提示有更新，形成更新死循环。
    lb = re.search(r'const localBuild = (\d+);', html)
    assert lb, 'starfield.html 里找不到 OTA 比较常量 localBuild'
    assert lb.group(1) == build, (
        f'OTA 常量 localBuild={lb.group(1)} != version.json build {build}'
        f'（不同步会导致提示有更新但装完仍是旧版）'
    )
    print(f'  ok  v{version} (Build {build}) 四处一致（含 OTA localBuild）')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
    print('\n✅ ASSET PARITY & VERSION SYNC OK')
