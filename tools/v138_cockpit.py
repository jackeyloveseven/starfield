"""v138: rebuild the cockpit as a composition, not a caption.

Diagnosis from six frames (20/60/120 s at 1600x900 and 390x844):
  * The hood is invisible. Panels are filled with blend(paper, ink, .11) and
    paper is the DARK colour, so the frame is #1a2432 on a #1c2b3c sky. The
    only visible piece of the cabin was the taped note, because it is drawn
    in ink (light) and half of it sat off-screen.
  * The lead crane is erased. The near-fade starts at 350 units from the eye,
    the eye sits 640 behind the lead, so the lead and the inner formation were
    computed at alpha 0. The fleet read as a ring with a hole in the middle.
  * The dash is an 80 px strip at the very bottom, its labels at alpha .34,
    and on a bright planet they are unreadable.
  * On 390x844 the FOV is H*1.12 (vertical 48 deg, horizontal 23 deg): the
    fleet is cut by the frame edges, and the dash sits on top of the cranes.

What this patch does:
  1. Eye: 580 behind / 100 above the lead, looking 760 ahead and 9 deg down,
     so the formation rises into the window instead of sitting on the dash.
  2. FOV: portrait gets W*1.52 (about 71 deg vertical) instead of H*1.12.
  3. Near-fade: 70..190 units, and the lead is never faded.
  4. Hood redrawn in ink/paper contrast: 4.8 % top beam, 5.2 % posts,
     ~24 % desk, lit rims, inner shadow, reflection ceiling at .055 alpha.
  5. Dash: a real plate with three larger dials, compass ribbon, trip line
     and formation line, at readable contrast, sized separately for portrait.

  python -I v138_cockpit.py <in.html> <out.html>
"""
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: python -I v138_cockpit.py <in.html> <out.html>')
    src_path, out_path = sys.argv[1], sys.argv[2]
    src = open(src_path, encoding='utf-8').read()

    def rep(old, new, label):
        nonlocal src
        n = src.count(old)
        assert n == 1, '%s: expected 1 occurrence, got %d' % (label, n)
        src = src.replace(old, new, 1)

    import re

    def repsub(pat, new, label):
        nonlocal src
        hits = re.findall(pat, src, re.S)
        assert len(hits) == 1, '%s: expected 1 match, got %d' % (label, len(hits))
        src = re.sub(pat, lambda m: new, src, count=1, flags=re.S)

    # ---- 1. the eye -------------------------------------------------------
    rep(' const back=640,rise=118;',
        ' const back=580,rise=100;',
        'eye offset')

    rep(' const look=[routeX(travel+900) + Math.sin(headTurnX)*900, '
        'courseY(travel+900)+26 + Math.sin(headTurnY)*450, travel+900];',
        ' const look=[routeX(travel+760) + Math.sin(headTurnX)*760, '
        'courseY(travel+760)-110 + Math.sin(headTurnY)*420, travel+760];',
        'look target')

    # ---- 2. the lens ------------------------------------------------------
    rep(' camera.focal = H * (1.12 / (1 + effWarp * 0.024));',
        ' camera.focal = (W < H ? W * 1.52 : H * 1.12) / (1 + effWarp * 0.024);',
        'focal')

    # ---- 3. the near fade: tight, and never the lead ----------------------
    rep('nearCraft = cockpitBlend > 0.01 ? (1 - cockpitBlend * '
        'Math.max(0, Math.min(1, (260 - (dcam - 90)) / 260))) : 1;',
        'nearCraft = cockpitBlend > 0.01 ? '
        '(1 - cockpitBlend * (1 - Math.max(0, Math.min(1, (dcam - 70) / 120)))) : 1;\n'
        '          if (b === fleet[LEAD]) nearCraft = 1;',
        'nearCraft (customizer path)')

    rep('const nearCraft=cockpitBlend>.01?mix(1,clamp((dcam-90)/260,0,1),cockpitBlend):1;',
        'const nearCraft=cockpitBlend>.01?mix(1,clamp((dcam-70)/120,0,1),cockpitBlend):1;'
        'if(lead)nearCraft=1;',
        'nearCraft (main path)')

    # ---- 4 + 5. the hood and the dash ------------------------------------
    new_ui = r'''function drawDash(k){
 const ink=currentPalette.ink,paper=currentPalette.paper;
 const portrait=W<H;
 const plate=blend(ink,paper,.40),print=blend(paper,ink,.04);
 const bh=portrait?Math.min(H*.165,142):Math.min(H*.19,172);
 const bw=portrait?W*.92:Math.min(W*.54,864);
 const bx=W*.5-bw*.5,by=H-bh;
 const pad=portrait?16:30,R=portrait?18:28,gap=portrait?54:82;
 const dialY=by+(portrait?50:64);
 ctx.save();ctx.globalAlpha=k;
 // The desk is paper, so it is LIGHT: a dark plate was the same value as the
 // sky on every region and read as a smudge on the bottom of the frame.
 ctx.fillStyle=css(plate,.96);
 ctx.beginPath();
 ctx.moveTo(bx,by+bh*.10);ctx.lineTo(bx+bw*.03,by);
 ctx.lineTo(bx+bw*.97,by);ctx.lineTo(bx+bw,by+bh*.10);
 ctx.lineTo(bx+bw,H);ctx.lineTo(bx,H);ctx.closePath();ctx.fill();
 ctx.strokeStyle=css(blend(paper,ink,.10),.72);ctx.lineWidth=2;ctx.stroke();
 ctx.strokeStyle=css(ink,.45);ctx.lineWidth=1;
 ctx.beginPath();ctx.moveTo(bx+bw*.06,by+8);ctx.lineTo(bx+bw*.94,by+8);ctx.stroke();
 // Three dials that read the running simulation.
 const speed=Math.hypot(wind.x,wind.y)*1.4+
   Math.max(warp,WarpDrive.currentWarp)*1.1+1;
 const vals=[
  {v:clamp(speed/16,0,1)},
  {v:clamp((travel-departure)/240000,0,1)},
  {v:clamp((camera.eye[1]-60)/2400,0,1)}
 ];
 for(let i=0;i<3;i++){
  const cx=bx+pad+R+i*gap,cy=dialY;
  ctx.beginPath();ctx.arc(cx,cy,R,Math.PI*.78,Math.PI*.22,false);
  ctx.strokeStyle=css(print,.68);ctx.lineWidth=1.3;ctx.stroke();
  for(let t=0;t<7;t++){
   const a=Math.PI*.78+(Math.PI*1.44)*(t/6);
   ctx.beginPath();
   ctx.moveTo(cx+Math.cos(a)*R*.82,cy-Math.sin(a)*R*.82);
   ctx.lineTo(cx+Math.cos(a)*R*.96,cy-Math.sin(a)*R*.96);
   ctx.strokeStyle=css(print,.70);ctx.lineWidth=.9;ctx.stroke();
  }
  const a=Math.PI*.78+(Math.PI*1.44)*vals[i].v;
  ctx.beginPath();ctx.moveTo(cx,cy);
  ctx.lineTo(cx+Math.cos(a)*R*.74,cy-Math.sin(a)*R*.74);
  ctx.strokeStyle=css(blend(print,[180,56,44],.45),.92);ctx.lineWidth=2;ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,Math.max(1.6,R*.10),0,TAU);
  ctx.fillStyle=css(print,.62);ctx.fill();
  ctx.font=`${Math.max(8,Math.round(R*.42))}px "Songti SC","Noto Serif SC",serif`;
  ctx.fillStyle=css(print,.72);ctx.textAlign='center';ctx.textBaseline='top';
  ctx.fillText(['速','程','高'][i],cx,cy+R*.34);
 }
 // Compass ribbon.
 const crx=bx+(portrait?180:300),crw=portrait?bw*.40:bw*.19,cry=dialY;
 ctx.strokeStyle=css(print,.55);ctx.lineWidth=1.2;
 ctx.beginPath();ctx.moveTo(crx,cry);ctx.lineTo(crx+crw,cry);ctx.stroke();
 for(let i=0;i<=12;i++){
  const x=crx+crw*(i/12),tall=i%3===0;
  ctx.beginPath();ctx.moveTo(x,cry);ctx.lineTo(x,cry-(tall?R*.72:R*.48));
  ctx.strokeStyle=css(print,tall?.72:.50);ctx.lineWidth=tall?1.2:.9;ctx.stroke();
 }
 const hdg=((camera.yaw*180/Math.PI)%360+360)%360/360;
 ctx.fillStyle=css(blend(print,[180,56,44],.45),.95);
 ctx.fillRect(crx+crw*hdg-1.2,cry-R*1.06,2.4,R*.34);
 // Two registers: the trip, then who is out there.
 ctx.textAlign='left';ctx.textBaseline='alphabetic';
 const tx=bx+(portrait?pad:bw*.60),ty=by+(portrait?bh*.72:bh*.58);
 ctx.font=`${portrait?10:13}px "Songti SC","Noto Serif SC",serif`;
 ctx.fillStyle=css(print,.90);
 ctx.fillText('航程 '+(travel-departure).toFixed(0)+' · 第 '+((cycle|0)+1)+' 段',tx,ty);
 ctx.font=`${portrait?9:11}px "Songti SC","Noto Serif SC",serif`;
 ctx.fillStyle=css(print,.68);
 ctx.fillText('编队 '+fleet.length+' · 领队 '+String(LEAD+1).padStart(2,'0'),tx,ty+(portrait?17:22));
 ctx.restore();ctx.globalAlpha=1;
}
function drawCockpit(t){
 const k=cockpitBlend;if(k<=.01)return;
 const ink=currentPalette.ink,paper=currentPalette.paper;
 const portrait=W<H;
 // Paper again: the hood is a lit fold, not a value close to the sky.
 const board=blend(ink,paper,.46),boardDark=blend(ink,paper,.60);
 const seam=blend(paper,ink,.04),lit=blend(ink,[255,255,255],.55);
 const pw=W*(portrait?.070:.060),topH=H*(portrait?.045:.055);
 ctx.save();ctx.globalAlpha=k;
 // The glass: one soft ceiling of reflection, never more than .055, and a
 // little dust fixed to the canopy rather than to the sky.
 let g=ctx.createLinearGradient(0,0,W*.62,H*.30);
 g.addColorStop(0,css([255,255,255],.032));
 g.addColorStop(.45,css([255,255,255],.012));
 g.addColorStop(1,css([255,255,255],0));
 ctx.fillStyle=g;ctx.fillRect(0,0,W*.74,H*.34);
 ctx.fillStyle=css(blend(ink,[255,255,255],.5),.13);
 for(const d of [[.24,.27,1.7],[.70,.16,1.1],[.81,.46,1.9],[.36,.58,1.2]]){
  ctx.beginPath();ctx.arc(W*d[0],H*d[1],d[2],0,TAU);ctx.fill();
 }
 // The window is set into the hood: shadow along the inside edges first.
 g=ctx.createLinearGradient(0,topH,0,topH+H*.09);
 g.addColorStop(0,css(seam,.55));g.addColorStop(1,css(seam,0));
 ctx.fillStyle=g;ctx.fillRect(0,topH,W,H*.09);
 g=ctx.createLinearGradient(pw,0,pw+W*.04,0);
 g.addColorStop(0,css(seam,.48));g.addColorStop(1,css(seam,0));
 ctx.fillStyle=g;ctx.fillRect(pw,0,W*.04,H);
 g=ctx.createLinearGradient(W-pw,0,W-pw-W*.04,0);
 g.addColorStop(0,css(seam,.48));g.addColorStop(1,css(seam,0));
 ctx.fillStyle=g;ctx.fillRect(W-pw-W*.04,0,W*.04,H);
 // Two posts: a folded panel, lit edge inward, dark edge outward.
 for(const side of [0,1]){
  const sx=side?W:0,sgn=side?-1:1;
  ctx.beginPath();
  ctx.moveTo(sx,0);ctx.lineTo(sx+sgn*pw,0);
  ctx.lineTo(sx+sgn*pw*.80,H);ctx.lineTo(sx,H);ctx.closePath();
  ctx.fillStyle=css(board,.92);ctx.fill();
  // the fold down the middle of the panel
  ctx.beginPath();ctx.moveTo(sx+sgn*pw*.52,0);ctx.lineTo(sx+sgn*pw*.40,H);
  ctx.strokeStyle=css(boardDark,.55);ctx.lineWidth=1.6;ctx.stroke();
  // the inner edge is what makes it read as structure
  ctx.beginPath();ctx.moveTo(sx+sgn*pw,0);ctx.lineTo(sx+sgn*pw*.80,H);
  ctx.strokeStyle=css(lit,.70);ctx.lineWidth=2;ctx.stroke();
  ctx.beginPath();ctx.moveTo(sx+sgn*pw*.995,0);ctx.lineTo(sx+sgn*pw*.795,H);
  ctx.strokeStyle=css(seam,.70);ctx.lineWidth=1.2;ctx.stroke();
 }
 // Stitches: a made thing, not a bezel.
 ctx.fillStyle=css(seam,.30);
 for(let y=topH+12;y<H*.72;y+=14){
  const x=pw-(y/H)*(pw-pw*.80)-5;
  ctx.fillRect(x-1.1,y,2.2,4.2);
  ctx.fillRect(W-x-1.1,y,2.2,4.2);
 }
 // The top beam. One fold under it, no centre visor: the visor read as a
 // patch of different value pasted onto the beam.
 ctx.fillStyle=css(board,.92);ctx.fillRect(0,0,W,topH);
 ctx.strokeStyle=css(lit,.70);ctx.lineWidth=2;
 ctx.beginPath();ctx.moveTo(0,topH);ctx.lineTo(W,topH);ctx.stroke();
 ctx.strokeStyle=css(boardDark,.50);ctx.lineWidth=1;
 ctx.beginPath();ctx.moveTo(0,topH*.42);ctx.lineTo(W,topH*.42);ctx.stroke();
 // A note taped inside, fully on the plate this time.
 const nw=W*(portrait?.11:.042),nh=nw*.62;
 ctx.save();
 ctx.translate(W-pw-14-nw*.5,topH+22+nh*.5);ctx.rotate(-.05);
 ctx.fillStyle=css(blend(ink,[255,255,255],.6),.55);
 ctx.fillRect(-nw/2,-nh/2,nw,nh);
 ctx.fillStyle=css(blend(paper,[180,60,50],.55),.62);
 ctx.fillRect(-nw/2,-nh/2,nw,Math.max(2,nw*.03));
 ctx.strokeStyle=css(paper,.45);ctx.lineWidth=.8;
 ctx.beginPath();ctx.moveTo(-nw*.36,-nh*.06);ctx.lineTo(nw*.10,-nh*.14);ctx.stroke();
 ctx.beginPath();ctx.moveTo(-nw*.36,nh*.12);ctx.lineTo(nw*.24,nh*.05);ctx.stroke();
 ctx.beginPath();ctx.moveTo(-nw*.36,nh*.26);ctx.lineTo(-nw*.06,nh*.22);ctx.stroke();
 ctx.restore();
 ctx.restore();
 ctx.globalAlpha=1;
 drawDash(k);
}
function toggleCockpit(){'''

    repsub(r'function drawDash\(k\)\{.*?\n\}\nfunction toggleCockpit\(\)\{',
           new_ui, 'drawDash + drawCockpit')

    # ---- 6. the seat owns the screen: the flight HUD must not sit on the dash
    css = ('<style id="v138-cockpit">'
           'body.cockpit-on #journey,body.cockpit-on #camera-hud,'
           'body.cockpit-on #hint{'
           'opacity:0!important;pointer-events:none!important}'
           '@media(min-width:760px){body.cockpit-on #controls{'
           'opacity:0!important;pointer-events:none!important}}'
           '</style>')
    rep('</head>', css + '</head>', 'css hook')

    rep(' cockpitMode=!cockpitMode;\n',
        " cockpitMode=!cockpitMode;\n"
        " document.body.classList.toggle('cockpit-on',cockpitMode);\n",
        'body class on toggle')

    rep(" if(cockpitMode){cockpitMode=false;toast('回到外部镜头');}",
        " if(cockpitMode){cockpitMode=false;"
        "document.body.classList.remove('cockpit-on');toast('回到外部镜头');}",
        'body class off camera toggle')

    # ---- 7. a deterministic draw entry for the headless harness -----------
    # seek() only advances the simulation; it never paints. A synchronous
    # probe therefore races the first rAF and sometimes captures an empty
    # canvas (measured: 2 of 3 runs). Exposing one frame costs nothing in the
    # page and makes every acceptance shot reproducible.
    rep(' getCamera:()=>camera,',
        ' drawOnce:()=>{frame(last+1);},\n getCamera:()=>camera,',
        'drawOnce hook')

    open(out_path, 'w', encoding='utf-8', newline='').write(src)
    print('wrote', out_path, len(src), 'chars')


main()
