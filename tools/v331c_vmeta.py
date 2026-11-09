# -*- coding: utf-8 -*-
"""v331c - 修正 version.json 的双重转义，并写入 Build 181 的更新文案。"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
VER = Path(r'D:\items\code\projects\starfield\starfield-pub') / 'version.json'
meta = json.loads(VER.read_text(encoding='utf-8'))
assert meta['build'] == 181, meta['build']
meta['title'] = '母舰与城市集群：沙盘模型重做'
meta['changelog'] = ('修好了 3D 模型发黑：色彩空间回正、金属度钳位、自发光不再二次提亮。'
                     '母舰改为地表悬停、舰艏迎向镜头；城市集群重建为退台主塔 + 八栋副塔 + 空中连廊 + 楼层光带。')
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
print(VER.read_text(encoding='utf-8'))