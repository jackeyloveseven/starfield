# -*- coding: utf-8 -*-
"""
构建产物一致性校验套件：
1. 根目录 starfield.html 与 android assets 镜像 100% 字节一致；
2. service-worker.js 根目录与 android assets 镜像 100% 字节一致；
3. planet_studio.html 根目录与 android assets 镜像 100% 字节一致；
4. version.json 根目录与 android assets 镜像 100% 字节一致；
5. version.json / service-worker CACHE_VERSION / 设置抽屉版本号 / OTA localBuild 四处版本自洽。
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
STUDIO = BASE / 'planet_studio.html'
STUDIO_MIRROR = BASE / 'android' / 'app' / 'src' / 'main' / 'assets' / 'planet_studio.html'
VERSION = BASE / 'version.json'
VERSION_MIRROR = BASE / 'android' / 'app' / 'src' / 'main' / 'assets' / 'version.json'


def main():
    print('== 1. starfield.html 根目录 vs Android 镜像 ==')
    a = MASTER.read_bytes()
    b = MIRROR.read_bytes()
    assert a == b, f'字节不一致: root={len(a)} android={len(b)}'
    print(f'  ok  {len(a):,} bytes 完全一致')

    print('== 2. service-worker.js 双份一致 ==')
    s1 = SW.read_text(encoding='utf-8')
    s2 = SW_MIRROR.read_text(encoding='utf-8')
    assert s1 == s2, 'service-worker.js 根目录与 Android 镜像不一致'
    print('  ok  两份完全一致')

    print('== 3. planet_studio.html 双份一致 ==')
    p1 = STUDIO.read_bytes()
    p2 = STUDIO_MIRROR.read_bytes()
    assert p1 == p2, f'planet_studio.html 字节不一致: root={len(p1)} android={len(p2)}'
    print(f'  ok  {len(p1):,} bytes 完全一致')

    print('== 4. version.json 双份一致 ==')
    v1 = VERSION.read_bytes()
    v2 = VERSION_MIRROR.read_bytes()
    assert v1 == v2, 'version.json 根目录与 Android 镜像不一致'
    print('  ok  两份完全一致')

    print('== 5. 版本号四处自洽 ==')
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
    # 第 4 处：OTA 比较用的硬编码常量。
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
