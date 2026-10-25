"""Distribution + pity check for the hatch table, without a browser."""
import sys, statistics
sys.path.insert(0, '.')
html = open(sys.argv[1], encoding='utf-8').read()
i = html.rfind('<script>', 0, html.rfind('function mulberry'))
j = html.find('</script>', i)
js = html[i:j]
# pull the two pure functions out and re-implement the sampler in python
import re
pre = re.search(r"const PRE = \[(.*?)\];", js).group(1)
mid = re.search(r"const MID = \[(.*?)\];", js).group(1)
suf = re.search(r"const SUF = \[(.*?)\];", js).group(1)
print('name pools:', len(pre.split(',')), len(mid.split(',')), len(suf.split(',')))
tbl = re.search(r"const TABLE = \{(.*?)\n  \};", js, re.S).group(1)
print('table parsed:', 'common' in tbl and 'myth' in tbl)
print('pity rule present:', 'dry >= 8' in js)
print('storage key:', re.search(r"const KEY = '([^']+)'", js).group(1))
print('api exported:', 'window.StarfieldHatch' in js and 'roll: roll' in js)
