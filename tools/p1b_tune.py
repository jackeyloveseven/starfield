"""P1b: space lens names, and tuning found by looking at the first render.

- black holes were far too common (2-3 in one view) and too large
- atlas plates read as dark cardboard rather than lit pages
- torn shards read as flat cards
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit(f"expected 1, found {s.count(old)}:\n{old[:140]}")
    s = s.replace(old, new, 1)


# ---- the sixteen lenses, renamed for deep space (yaw/pitch/d unchanged) ----
LENS_OLD = """ {name:'正俯视',en:'OVERHEAD',yaw:-32,pitch:83,d:1490},
 {name:'地图之间',en:'ATLAS',yaw:46,pitch:74,d:1910},
 {name:'俯冲入风',en:'DESCENT',yaw:28,pitch:43,d:1190},
 {name:'贴河掠水',en:'RIVER SKIM',yaw:-8,pitch:-9,d:1010,lane:1},
 {name:'沿河前推',en:'RIVER APPROACH',yaw:37,pitch:19,d:1190,lane:.9},
 {name:'侧向轨道',en:'LATERAL ORBIT',yaw:91,pitch:30,d:1190},
 {name:'低空宽景',en:'LOW HORIZON',yaw:-72,pitch:8,d:1590},
 {name:'环绕纸翼',en:'PAPER ORBIT',yaw:132,pitch:35,d:1120},
 {name:'拉远揭示',en:'REVEAL',yaw:-118,pitch:51,d:2070},
 {name:'正背面',en:'FOLLOWING',yaw:0,pitch:13,d:1020},
 {name:'迎面来风',en:'HEADWIND',yaw:180,pitch:16,d:1090},
 {name:'高空漂移',en:'HIGH DRIFT',yaw:-52,pitch:65,d:1810},
 {name:'沿岸侧写',en:'BANK STUDY',yaw:64,pitch:38,d:1480},
 {name:'逆光上升',en:'INTO THE LIGHT',yaw:138,pitch:60,d:1720},
 {name:'与翼齐行',en:'WING LEVEL',yaw:-88,pitch:3,d:850},
 {name:'大地呼吸',en:'EARTH BREATHING',yaw:79,pitch:77,d:2010}"""
rep(LENS_OLD, """ {name:'俯瞰纸面',en:'SHEET',yaw:-32,pitch:83,d:1490},
 {name:'星图之间',en:'ATLAS',yaw:46,pitch:74,d:1910},
 {name:'坠入墨色',en:'DESCENT',yaw:28,pitch:43,d:1190},
 {name:'掠过尘带',en:'LANE SKIM',yaw:-8,pitch:-9,d:1010,lane:1},
 {name:'沿带前推',en:'LANE APPROACH',yaw:37,pitch:19,d:1190,lane:.9},
 {name:'侧向轨道',en:'LATERAL ORBIT',yaw:91,pitch:30,d:1190},
 {name:'低空宽景',en:'LOW HORIZON',yaw:-72,pitch:8,d:1590},
 {name:'环绕纸鹤',en:'CRANE ORBIT',yaw:132,pitch:35,d:1120},
 {name:'拉远揭示',en:'REVEAL',yaw:-118,pitch:51,d:2070},
 {name:'尾随航行',en:'FOLLOWING',yaw:0,pitch:13,d:1020},
 {name:'迎面星光',en:'STARWARD',yaw:180,pitch:16,d:1090},
 {name:'深空漂移',en:'DEEP DRIFT',yaw:-52,pitch:65,d:1810},
 {name:'尘带侧写',en:'LANE STUDY',yaw:64,pitch:38,d:1480},
 {name:'迎光上升',en:'INTO THE LIGHT',yaw:138,pitch:60,d:1720},
 {name:'与鹤齐行',en:'WING LEVEL',yaw:-88,pitch:3,d:850},
 {name:'深渊呼吸',en:'ABYSS BREATHING',yaw:79,pitch:77,d:2010}""")
rep('<h2 id="camera-name" class="serif">大地呼吸</h2>',
    '<h2 id="camera-name" class="serif">深渊呼吸</h2>')

# ---- black holes: rarer, smaller, at most one per chunk --------------------
rep(""" const zc=z0+CHUNK*.5,pc=region(laneX(zc),zc);
 for(let i=0,n=1+Math.floor(r()*3);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=560+r()*1700,roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(r()<.05+pc.void*.42)kind=4;
  masses.push({x:laneX(z)+side*off,y:150+r()*520,z,kind,r:[150,205,270,340,420][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
 }""",
    """ const zc=z0+CHUNK*.5,pc=region(laneX(zc),zc);
 // One horizon per chunk at most, and rare outside the abyss: an encounter
 // should be an event, not scenery.
 const horizon=r()<.07+pc.void*.40;
 for(let i=0,n=1+Math.floor(r()*3);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=560+r()*1700,roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(horizon&&i===0)kind=4;
  masses.push({x:laneX(z)+side*off,y:150+r()*520,z,kind,r:[110,150,200,260,330][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
 }""")

# ---- plates read as lit pages, shards as paper rather than card ------------
rep("poly([at(-pl.w*.5,-pl.h*.5,0),at(pl.w*.5,-pl.h*.5,0),at(pl.w*.5,pl.h*.5,0),at(-pl.w*.5,pl.h*.5,0)],blend(p.paper,p.wall,.18),{palette:p,alpha:.9});",
    "poly([at(-pl.w*.5,-pl.h*.5,0),at(pl.w*.5,-pl.h*.5,0),at(pl.w*.5,pl.h*.5,0),at(-pl.w*.5,pl.h*.5,0)],blend(p.wall,p.bird,.30),{palette:p,alpha:.9});")
rep("poly([at(-pl.w*.5,-pl.h*.5,-3),at(pl.w*.5,-pl.h*.5,-3),at(pl.w*.5,-pl.h*.5,0),at(-pl.w*.5,-pl.h*.5,0)],shade(p.wall,.8),{palette:p,alpha:.85});",
    "poly([at(-pl.w*.5,-pl.h*.5,-3),at(pl.w*.5,-pl.h*.5,-3),at(pl.w*.5,-pl.h*.5,0),at(-pl.w*.5,-pl.h*.5,0)],shade(p.wall,.62),{palette:p,alpha:.85});")
rep("poly(q,blend(p.wall,p.paper,.12),{palette:p,alpha:.94});",
    "poly(q,blend(p.wall,p.bird,.18),{palette:p,alpha:.94});")
rep("poly([q[0],q[1],mid[1],mid[0]],shade(blend(p.roof,p.paper,.1),.92),{palette:p,alpha:.9});",
    "poly([q[0],q[1],mid[1],mid[0]],shade(blend(p.roof,p.bird,.10),.92),{palette:p,alpha:.9});")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("p1b applied")
