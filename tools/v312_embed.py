
# -*- coding: utf-8 -*-
"""v312 - GLB 转 base64 内嵌，用 GLTFLoader.parse 避免 file:// CORS。"""
import base64, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
GLB = BASE / 'models' / 'mothership.glb'
HTML = BASE / 'starfield.html'

b64 = base64.b64encode(GLB.read_bytes()).decode('ascii')
print('glb base64 length =', len(b64))

html = HTML.read_text(encoding='utf-8')

# 把 base64 存为 window 变量
inject = '<script>window.__mothershipGLB = "' + b64 + '";</script>\n'
head_end = html.find('</head>')
assert head_end > 0
html = html[:head_end] + inject + html[head_end:]

# 把 load() 改为 parse()
old = """      if (env.dock && THREE.GLTFLoader) {
        new THREE.GLTFLoader().load('models/mothership.glb', function (gltf) {"""
new = """      if (env.dock && THREE.GLTFLoader && window.__mothershipGLB) {
        (function () {
          var bin = atob(window.__mothershipGLB);
          var bytes = new Uint8Array(bin.length);
          for (var bi = 0; bi < bin.length; bi++) bytes[bi] = bin.charCodeAt(bi);
          new THREE.GLTFLoader().parse(bytes.buffer, '', function (gltf) {"""
assert html.count(old) == 1, 'load count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('GLB embedded as base64, parse() instead of load()')
