
# -*- coding: utf-8 -*-
"""v267 - 修作用域：游戏主 IIFE 内的 project/routeX/W/started 外部脚本访问不到，
   改为在 frame() 里把环境注入进来。此前 draw() 因 started undefined 直接 return。"""
import re, sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

# 1) frame() 里的调用：注入环境
old_call = "drawSkyEvents(); if(window.SFPassersby) window.SFPassersby.draw();"
new_call = ("drawSkyEvents(); if(window.SFPassersby) window.SFPassersby.draw({"
            "ctx:ctx, project:project, routeX:routeX, courseY:courseY, "
            "W:W, H:H, travel:travel, CHUNK:CHUNK, hash:hash, started:started});")
assert html.count(old_call) == 1, 'call count=%d' % html.count(old_call)
html = html.replace(old_call, new_call)

# 2) 模块内部：从注入的环境取，不再依赖外部词法作用域
i = html.find('<script id="sf-passersby">')
j = html.find('</script>', i)
assert i > 0 and j > i
body = html[i:j]

# 顶部加环境容器
body = body.replace(
  "  if (window.SFPassersby) return;",
  "  if (window.SFPassersby) return;\n\n  var E = null;   /* 由 frame() 注入的游戏内作用域 */",
  1)

# fadeAtCenter 需要 W
body = body.replace(
  "  function fadeAtCenter(sx) {",
  "  function fadeAtCenter(sx) {\n    var W = E.W;",
  1)

# 三个绘制函数需要 project / ctx
body = body.replace(
  "  function comet(x, y, z, side, seed, fade) {",
  "  function comet(x, y, z, side, seed, fade) {\n    var project = E.project, ctx = E.ctx;",
  1)
body = body.replace(
  "  function darkNebula(x, y, z, seed, fade) {",
  "  function darkNebula(x, y, z, seed, fade) {\n    var project = E.project, ctx = E.ctx;",
  1)
body = body.replace(
  "  function planetaryNebula(x, y, z, seed, fade) {",
  "  function planetaryNebula(x, y, z, seed, fade) {\n    var project = E.project, ctx = E.ctx;",
  1)

# draw 入口：接收 env 并解构
body = body.replace(
  "    draw: function () {\n      if (typeof started === 'undefined' || !started) return;\n      if (typeof travel === 'undefined') return;",
  """    draw: function (env) {
      E = env;
      if (!E || !E.started) return;
      var ctx = E.ctx, project = E.project, routeX = E.routeX, courseY = E.courseY,
          W = E.W, H = E.H, travel = E.travel, CHUNK = E.CHUNK, hash = E.hash;""",
  1)

html = html[:i] + body + html[j:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('scope fixed via dependency injection')
