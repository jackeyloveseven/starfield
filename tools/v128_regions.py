"""V128: the five regions get a star count, not just a hue.

`dense` already varies brightness (core brighter, void dimmer) but the number of
stars drawn was fixed: every region had the same sky, lit differently. Now the
count follows the palette mix, so the abyss is nearly empty and the core is
crowded - the difference you notice without comparing colours.
"""
import sys
src_p,out_p=sys.argv[1],sys.argv[2]
src=open(src_p,encoding="utf-8").read()
old=" const limit=lowQuality?Math.floor(stars.length*.26):stars.length;"
new=(" // star COUNT per region: a dim sky with all its stars is still the same sky.\n"
     " const _pm=(typeof p!=='undefined')?p:{core:.2,shimmer:.2,void:.2};\n"
     " const _rc=clamp(.55+(_pm.core||0)*.95+(_pm.shimmer||0)*.25-(_pm.void||0)*.5,.12,1.4);\n"
     " const limit=Math.floor((lowQuality?stars.length*.26:stars.length)*_rc);")
if src.count(old)!=1: sys.exit('count=%d'%src.count(old))
open(out_p,"w",encoding="utf-8",newline="").write(src.replace(old,new,1))
print("V128 written:",len(src),"chars")
