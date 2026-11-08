
# -*- coding: utf-8 -*-
"""v256 - 彻底去掉旧的分隔 box-shadow（它在别的样式层里，优先级更高）。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = """#sf-hatch .sf-card-act-btn + .sf-card-act-btn{
  position:relative !important;
}"""
new = """#sf-hatch .sf-card-actions .sf-card-act-btn{
  box-shadow:none !important;
  border:0 !important;
}
#sf-hatch .sf-card-actions .sf-card-act-btn + .sf-card-act-btn{
  position:relative !important;
  box-shadow:none !important;
  border:0 !important;
}"""
assert html.count(old) == 1
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('box-shadow cleared')
