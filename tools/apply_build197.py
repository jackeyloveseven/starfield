# tools/apply_build197.py
import os
import json
import shutil
import hashlib

BASE_DIR = r'd:\items\code\projects\starfield\starfield-pub'
HTML_FILE = os.path.join(BASE_DIR, 'starfield.html')
MAIN_JAVA = os.path.join(BASE_DIR, 'android', 'app', 'src', 'main', 'java', 'com', 'starfield', 'focus', 'MainActivity.java')
VERSION_JSON = os.path.join(BASE_DIR, 'version.json')
SW_FILE = os.path.join(BASE_DIR, 'service-worker.js')

print('Starting Build 197 application...')

# ==============================================================================
# 1. Update starfield.html
# ==============================================================================
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

replacements = [
    # Version tag
    (
        '<span class="shortcut-key" id="sf-version-tag">v1.9.9.9.9.8 (Build 196)</span>',
        '<span class="shortcut-key" id="sf-version-tag">v1.9.9.9.9.9 (Build 197)</span>',
        'Version tag update'
    ),
    # Fix 3: UI shortcuts Tab -> J
    (
        '<button class="control" id="codex-toggle" title="星图手札 · 天体探索图鉴 (Tab / J)" aria-label="星图手札">',
        '<button class="control" id="codex-toggle" title="星图手札 · 天体探索图鉴 (J)" aria-label="星图手札">',
        'Codex button title Tab removal'
    ),
    (
        '<div class="shortcut-row"><span>Tab / J</span><span class="shortcut-key">星图手札与图鉴</span></div>',
        '<div class="shortcut-row"><span>J</span><span class="shortcut-key">星图手札与图鉴</span></div>\n      <div class="shortcut-row"><span>K</span><span class="shortcut-key">旗舰特写 / 驾驶舱视角</span></div>',
        'Codex shortcut dialog hint update'
    ),
    (
        '<button class="victory-btn primary mono" id="tuner-view-codex-btn">查阅星图手札 <span class="kbd-hint">[Tab]</span></button>',
        '<button class="victory-btn primary mono" id="tuner-view-codex-btn">查阅星图手札 <span class="kbd-hint">[J]</span></button>',
        'Victory screen codex shortcut Tab -> J'
    ),
    # Fix 2: WarpDrive.cycle hull < 25
    (
        '''  cycle() {
    if (window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
      this.gearIndex = 0;
      this.updateUI();
      if (typeof showToast === 'function') showToast('反物质能源耗尽 · 光帆微速漂流中，无法启动跃迁引擎', 3);
      else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 光帆微速漂流中，无法启动跃迁引擎', 3);
      return;
    }''',
        '''  cycle() {
    if (window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
      this.gearIndex = 0;
      this.updateUI();
      if (typeof showToast === 'function') showToast('反物质能源耗尽 · 光帆微速漂流中，无法启动跃迁引擎', 3);
      else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 光帆微速漂流中，无法启动跃迁引擎', 3);
      return;
    }
    if (window.SFHazard && window.SFHazard.state && window.SFHazard.state().hull < 25) {
      this.gearIndex = 0;
      this.updateUI();
      if (typeof showToast === 'function') showToast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
      else if (typeof window.toast === 'function') window.toast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
      return;
    }''',
        'Fix 2: WarpDrive.cycle hull < 25 check'
    ),
    # Fix 2: WarpDrive.setHold hull < 25
    (
        '''  setHold(holding) {
    if (holding && window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
      if (typeof showToast === 'function') showToast('反物质能源耗尽 · 无法超频充能', 2.5);
      else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 无法超频充能', 2.5);
      return;
    }''',
        '''  setHold(holding) {
    if (holding) {
      if (window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
        if (typeof showToast === 'function') showToast('反物质能源耗尽 · 无法超频充能', 2.5);
        else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 无法超频充能', 2.5);
        return;
      }
      if (window.SFHazard && window.SFHazard.state && window.SFHazard.state().hull < 25) {
        if (typeof showToast === 'function') showToast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
        else if (typeof window.toast === 'function') window.toast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
        return;
      }
    }''',
        'Fix 2: WarpDrive.setHold hull < 25 check'
    ),
    # Fix 12: Grain toggle
    (
        '''    $('btn-toggle-grain').addEventListener('click', () => {
      const b = $('btn-toggle-grain');
      const isOn = b.classList.toggle('active');
      b.textContent = isOn ? '开' : '关';
      grainCanvas.style.display = isOn ? '' : 'none';
    });''',
        '''    $('btn-toggle-grain').addEventListener('click', () => {
      const b = $('btn-toggle-grain');
      const isOn = b.classList.toggle('active');
      b.textContent = isOn ? '开' : '关';
      window.grainOn = isOn;
      toast(isOn ? '胶片噪点已开启' : '胶片噪点已关闭 · 纯净画面');
    });''',
        'Fix 12: btn-toggle-grain actual window.grainOn toggle'
    ),
    # Fix 4: Camera ultrawide cx and focal
    (
        ''' // 9. Cinematic IMAX Centering: smoothly shifts from cruise offset (0.385, 0.465) to majestic center (0.485, 0.495)
 const centerWeight = Math.max(captureCamPose ? captureCamPose.blend : 0, curSkimW, hm ? horizonW : 0);
 const isPortrait = H > W;
 camera.cx = W * (isPortrait ? 0.50 : mix(0.385, 0.485, centerWeight));
 camera.cy = H * (isPortrait ? 0.48 : mix(0.465, 0.495, centerWeight));

 const effWarpF = Math.max(warp, WarpDrive.currentWarp);
 const warpFactor = clamp(effWarpF / 28, 0, 1.2);
 const fovWarp = 1 / (1 + warpFactor * 0.35 - WarpDrive.reverseR * 0.22);
 camera.focal = (isPortrait ? Math.min(W, H) * 1.25 : H * 1.12) * fovWarp * (captureCamPose ? mix(1, captureCamPose.focal, captureCamPose.blend) : 1);''',
        ''' // 9. Cinematic IMAX Centering: smoothly shifts from cruise offset (0.385, 0.465) to majestic center (0.485, 0.495)
 const centerWeight = Math.max(captureCamPose ? captureCamPose.blend : 0, curSkimW, hm ? horizonW : 0);
 const isPortrait = H > W;
 const aspect = W / (H || 1);
 const ultrawideT = isPortrait ? 0 : clamp((aspect - 1.78) / (2.35 - 1.78), 0, 1);
 const baseDeskCx = mix(0.385, 0.50, ultrawideT);
 camera.cx = W * (isPortrait ? 0.50 : mix(baseDeskCx, 0.50, centerWeight));
 camera.cy = H * (isPortrait ? 0.48 : mix(0.465, 0.495, centerWeight));

 const effWarpF = Math.max(warp, WarpDrive.currentWarp);
 const warpFactor = clamp(effWarpF / 28, 0, 1.2);
 const fovWarp = 1 / (1 + warpFactor * 0.35 - WarpDrive.reverseR * 0.22);
 let baseFocal = isPortrait ? Math.min(W, H) * 1.25 : H * 1.12;
 if (!isPortrait && aspect > 1.85) {
   const minFocalUltrawide = (W * 0.5) / Math.tan(46 * Math.PI / 180);
   baseFocal = Math.max(baseFocal, minFocalUltrawide);
 }
 camera.focal = baseFocal * fovWarp * (captureCamPose ? mix(1, captureCamPose.focal, captureCamPose.blend) : 1);''',
        'Fix 4: Ultrawide dynamic cx and FOV clamp'
    ),
    # Fix 11: Particle popping
    (
        'function sprite(world,size,c,kind,alpha=1,rotation=0){const p=project(world);if(!p||p[0]<-40||p[0]>W+40||p[1]<-40||p[1]>H+40)return;queue.push({type:2,p,d:p[2],s:clamp(size*p[3],.4,60),c:css(haze(c,p[2])),alpha,kind,rotation});}',
        'function sprite(world,size,c,kind,alpha=1,rotation=0){const p=project(world);if(!p)return;const s=clamp(size*p[3],.4,60);const m=kind===\'firefly\'?s*4:Math.max(40,s*1.8);if(p[0]<-m||p[0]>W+m||p[1]<-m||p[1]>H+m)return;queue.push({type:2,p,d:p[2],s:clamp(size*p[3],.4,60),c:css(haze(c,p[2])),alpha,kind,rotation});}',
        'Fix 11: Dynamic particle culling bounds'
    ),
    # Fix 5: Cockpit steering in updateWind
    (
        ''' const targetX=input((wind.filteredX-.42)/.55)*energy,targetY=input((wind.filteredY-.5)/.5)*energy;
 wind.x=expStep(wind.x,autoCamera?targetX:0,1.4,dt);wind.y=expStep(wind.y,autoCamera?targetY:0,1.4,dt);''',
        ''' const targetX=input((wind.filteredX-.42)/.55)*energy,targetY=input((wind.filteredY-.5)/.5)*energy;
 const allowSteer = autoCamera || cockpitMode;
 wind.x=expStep(wind.x,allowSteer?targetX:0,1.4,dt);wind.y=expStep(wind.y,allowSteer?targetY:0,1.4,dt);''',
        'Fix 5: Allow steering in cockpitMode'
    ),
    # Fix 12: paperFinish grainPattern check
    (
        '''function paperFinish(){
 if(!coarse){
  ctx.save();ctx.globalAlpha=.40;ctx.fillStyle=grainPattern;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1;''',
        '''function paperFinish(){
 if(!coarse && (window.grainOn !== false)){
  ctx.save();ctx.globalAlpha=.40;ctx.fillStyle=grainPattern;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1;''',
        'Fix 12: paperFinish window.grainOn gating'
    ),
    # Fix 5 & 6: Pointer handlers for cockpit steering and pinch rotation exclusion
    (
        ''' else if(autoCamera)feedWind(p);else canvas.classList.add('dragging');
}
function onPointerMove(e){
 if(!started)return;
 const p=logicalPoint(e);let previous=pointers.get(e.pointerId);
 if(!previous&&(e.buttons===1||e.pointerType==='touch')){pointers.set(e.pointerId,p);previous=p;}
 if(!previous)return;
 pointers.set(e.pointerId,p);
 if(!autoCamera){
  const dx=p.x-previous.x,dy=p.y-previous.y;
  if(Math.abs(dx)>0||Math.abs(dy)>0){
   manual.yaw-=(dx)*.0045;
   manual.pitch=clamp(manual.pitch+(dy)*.004,-0.35,1.50);
   manual.lane=0;
   canvas.classList.add('dragging');
  }
 }else if(autoCamera&&(e.pointerType==='mouse'||previous))feedWind(p);
}''',
        ''' else if(autoCamera||cockpitMode)feedWind(p);else canvas.classList.add('dragging');
}
function onPointerMove(e){
 if(!started)return;
 const p=logicalPoint(e);let previous=pointers.get(e.pointerId);
 if(!previous&&(e.buttons===1||e.pointerType==='touch')){pointers.set(e.pointerId,p);previous=p;}
 if(!previous)return;
 pointers.set(e.pointerId,p);
 if(!autoCamera && !cockpitMode){
  if(pointers.size > 1) return;
  const dx=p.x-previous.x,dy=p.y-previous.y;
  if(Math.abs(dx)>0||Math.abs(dy)>0){
   manual.yaw-=(dx)*.0045;
   manual.pitch=clamp(manual.pitch+(dy)*.004,-0.35,1.50);
   manual.lane=0;
   canvas.classList.add('dragging');
  }
 }else if((autoCamera||cockpitMode)&&(e.pointerType==='mouse'||previous))feedWind(p);
}''',
        'Fix 5 & 6: Pointer move mutual exclusion & cockpit steering'
    ),
    # Fix 13: window.addEventListener pointercancel
    (
        '''canvas.addEventListener('pointerup',releasePointer);
canvas.addEventListener('pointercancel',releasePointer);
window.addEventListener('pointerup',e=>{
 if(pointers.has(e.pointerId)||e.buttons===0){releasePointer(e);}
});''',
        '''canvas.addEventListener('pointerup',releasePointer);
canvas.addEventListener('pointercancel',releasePointer);
window.addEventListener('pointerup',e=>{
 if(pointers.has(e.pointerId)||e.buttons===0){releasePointer(e);}
});
window.addEventListener('pointercancel',releasePointer);''',
        'Fix 13: Global window pointercancel registration'
    ),
    # Fix 1: Escape key sf-hatch .on support & safe hide
    (
        "   else if($('sf-hatch') && $('sf-hatch').classList.contains('active'))$('sf-hatch').classList.remove('active');",
        '''   else if($('sf-hatch') && ($('sf-hatch').classList.contains('on') || $('sf-hatch').classList.contains('active'))){
     if(window.StarfieldHatch && typeof window.StarfieldHatch.hide === 'function') window.StarfieldHatch.hide();
     else { $('sf-hatch').classList.remove('on'); $('sf-hatch').classList.remove('active'); }
   }''',
        'Fix 1: Escape key sf-hatch .on support & safe hide'
    ),
    # Fix 3: Remove Tab hijacking and add KeyK cockpit mode
    (
        " else if(e.key.toLowerCase()==='j'||e.key==='Tab'){",
        ''' else if(e.key.toLowerCase()==='j'||e.code==='KeyJ'){
    if($('codex-modal')?.classList?.contains('open'))Codex.close();
    else{if(window.Starfield&&window.Starfield.closeModal)window.Starfield.closeModal();Codex.open();}
    return;
  }
  else if(e.key.toLowerCase()==='k'||e.code==='KeyK'){
    toggleCockpit();
    return;
  }
  else if(false){''',
        'Fix 3: Remove Tab hijacking and add KeyK cockpit shortcut'
    ),
    # Fix 8: visibilitychange & blur narrator audio pause
    (
        '''document.addEventListener('visibilitychange',()=>{last=performance.now();if(document.hidden){sound.suspend();if(wakeLock)wakeLock.release().catch(()=>{});}else{if(!paused)sound.resume();requestWake();}});
window.addEventListener('blur',()=>{wind.active=false;wind.last=time;pointers.clear();});''',
        '''document.addEventListener('visibilitychange',()=>{last=performance.now();if(document.hidden){sound.suspend();if(window.Narrator&&window.Narrator.currentAudio&&!window.Narrator.currentAudio.paused){try{window.Narrator.currentAudio.pause();}catch(_){}}if(wakeLock)wakeLock.release().catch(()=>{});}else{if(!paused)sound.resume();requestWake();}});
window.addEventListener('blur',()=>{wind.active=false;wind.last=time;pointers.clear();if(window.Narrator&&window.Narrator.currentAudio&&!window.Narrator.currentAudio.paused){try{window.Narrator.currentAudio.pause();}catch(_){}}});''',
        'Fix 8: Narrator pause on visibilitychange & blur'
    ),
    # Fix 2: Starfield.throttleUp hull check
    (
        ''' throttleUp:()=>{
  if (window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
    if (typeof showToast === 'function') showToast('反物质能源耗尽 · 光帆微速漂流中，无法加速', 2.5);
    else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 光帆微速漂流中，无法加速', 2.5);
    return;
  }
  if(WarpDrive.gearIndex<WarpDrive.gears.length-1){''',
        ''' throttleUp:()=>{
  if (window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
    if (typeof showToast === 'function') showToast('反物质能源耗尽 · 光帆微速漂流中，无法加速', 2.5);
    else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 光帆微速漂流中，无法加速', 2.5);
    return;
  }
  if (window.SFHazard && window.SFHazard.state && window.SFHazard.state().hull < 25) {
    if (typeof showToast === 'function') showToast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
    else if (typeof window.toast === 'function') window.toast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
    return;
  }
  if(WarpDrive.gearIndex<WarpDrive.gears.length-1){''',
        'Fix 2: Starfield.throttleUp hull < 25 check'
    ),
    # Fix 1: Engine.isModalOpen hatch .on support
    (
        "  const hatchOpen = ($('sf-hatch')?.classList?.contains('active')) || ($('sf-hatch-list')?.classList?.contains('on'));",
        "  const hatchOpen = ($('sf-hatch')?.classList?.contains('on') || $('sf-hatch')?.classList?.contains('active')) || ($('sf-hatch-list')?.classList?.contains('on'));",
        'Fix 1: isModalOpen hatch .on support'
    ),
    # Fix 1: Engine.closeModal hatch .on support & safe hide
    (
        "  else if($('sf-hatch')?.classList?.contains('active'))$('sf-hatch').classList.remove('active');",
        '''  else if($('sf-hatch')?.classList?.contains('on') || $('sf-hatch')?.classList?.contains('active')){
    if(window.StarfieldHatch && typeof window.StarfieldHatch.hide === 'function') window.StarfieldHatch.hide();
    else { $('sf-hatch').classList.remove('on'); $('sf-hatch').classList.remove('active'); }
  }''',
        'Fix 1: closeModal hatch .on support & safe hide'
    ),
    # Fix 2: Starfield.setWarpGear hull check
    (
        ' setWarpGear:(i)=>{WarpDrive.gearIndex=i;WarpDrive.updateUI();},',
        ''' setWarpGear:(i)=>{
   if (i > 0) {
     if (window.StarfieldFuelEngine && window.StarfieldFuelEngine.isDrifting) {
       if (typeof showToast === 'function') showToast('反物质能源耗尽 · 无法切换曲率档位', 2.5);
       else if (typeof window.toast === 'function') window.toast('反物质能源耗尽 · 无法切换曲率档位', 2.5);
       return;
     }
     if (window.SFHazard && window.SFHazard.state && window.SFHazard.state().hull < 25) {
       if (typeof showToast === 'function') showToast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
       else if (typeof window.toast === 'function') window.toast('船体严重受损 · 动力总线锁定 (POWER LOSS)', 2.5);
       return;
     }
   }
   WarpDrive.gearIndex=i;WarpDrive.updateUI();
 },''',
        'Fix 2: Starfield.setWarpGear hull check'
    ),
    # Fix 3: MobileVirtualControls dispatch KeyJ instead of Tab
    (
        '''      } else {
        const btn = document.getElementById('codex-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', code: 'Tab', bubbles: true }));
      }''',
        '''      } else {
        const btn = document.getElementById('codex-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'j', code: 'KeyJ', bubbles: true }));
      }''',
        'Fix 3: MobileVirtualControls toggleCodex dispatch KeyJ'
    ),
    # Fix 9: Long press speed exclusion zone (remove .sf-touch-joy-zone)
    (
        "      if (t && t.closest && t.closest('button, .sf-touch-cluster, .sf-touch-joy-zone, .sf-touch-more-tray, #settings-drawer, #codex-modal, #sf-contract-hud, #sf-descent-btn, #sf-sonar-capsule')) return;",
        "      if (t && t.closest && t.closest('button, .sf-touch-cluster, .sf-touch-more-tray, #settings-drawer, #codex-modal, #sf-contract-hud, #sf-descent-btn, #sf-sonar-capsule')) return;",
        'Fix 9: Remove sf-touch-joy-zone from long press speed exclusion'
    ),
    # Fix 7: LivingPlanet WebGL raster return
    (
        '''        if (isMob) {
          return this.canvas;
        }
      }
      return (isMob && refreshInterval === 1) ? this.canvas : (model.canvas || this.canvas);''',
        '''        if (isMob) {
          return (model.canvas || this.canvas);
        }
      }
      return (model.canvas || this.canvas);''',
        'Fix 7: Avoid leaking singleton this.canvas in LivingPlanet raster'
    ),
    # Fix 1: __sfBack Android back key logic
    (
        '''  window.__sfBack=function(){
    var h=document.getElementById('sf-hatch'); if(h&&h.classList.contains('on')){h.classList.remove('on');return true;}
    var l=document.getElementById('sf-hatch-list'); if(l&&l.classList.contains('on')){l.classList.remove('on');return true;}
    var c=document.getElementById('codex-modal'); if(c&&c.classList.contains('open')){var b=c.querySelector('.codex-close');if(b){b.click();return true;}}
    var d=document.getElementById('settings-drawer'); if(d&&d.classList.contains('open')){var s=document.getElementById('settings-close-btn');if(s){s.click();return true;}}
    return false;
  };''',
        '''  window.__sfBack=function(){
    var tray=document.getElementById('sf-touch-more-tray');
    if(tray&&tray.classList.contains('open')){
      tray.classList.remove('open');
      var moreBtn=document.getElementById('sf-touch-more-btn');
      if(moreBtn)moreBtn.setAttribute('aria-expanded','false');
      return true;
    }
    if(window.StarfieldShipUpgrades && window.StarfieldShipUpgrades.isOpen){ window.StarfieldShipUpgrades.closeModal(); return true; }
    if(typeof PhotoStudio !== 'undefined' && PhotoStudio.active){ PhotoStudio.close(); return true; }
    if(typeof FleetCustomizer !== 'undefined' && FleetCustomizer.isOpen){ FleetCustomizer.close(); return true; }
    var hangar=document.getElementById('hangar-modal'); if(hangar&&hangar.classList.contains('open')){hangar.classList.remove('open'); return true;}
    var h=document.getElementById('sf-hatch'); if(h&&(h.classList.contains('on')||h.classList.contains('active'))){
      if(window.StarfieldHatch && typeof window.StarfieldHatch.hide === 'function') window.StarfieldHatch.hide();
      else { h.classList.remove('on'); h.classList.remove('active'); }
      return true;
    }
    var l=document.getElementById('sf-hatch-list'); if(l&&l.classList.contains('on')){l.classList.remove('on');return true;}
    var c=document.getElementById('codex-modal'); if(c&&c.classList.contains('open')){var b=c.querySelector('.codex-close');if(b){b.click();return true;}}
    var d=document.getElementById('settings-drawer'); if(d&&d.classList.contains('open')){var s=document.getElementById('settings-close-btn');if(s){s.click();return true;}}
    if(window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen){ window.StarfieldFocusEngine.closeDashboard(); return true; }
    return false;
  };''',
        'Fix 1: __sfBack full modal hierarchy & tray closing'
    ),
    # Fix 8: Ambience bus connection
    (
        '''    var sfxDest = (window.StarfieldAudio && window.StarfieldAudio.sfxBus) ? window.StarfieldAudio.sfxBus : c.destination;
    master.connect(sfxDest);''',
        '''    var ambDest = (window.StarfieldAudio && (window.StarfieldAudio.ambienceBus || window.StarfieldAudio.sfxBus)) ? (window.StarfieldAudio.ambienceBus || window.StarfieldAudio.sfxBus) : c.destination;
    master.connect(ambDest);''',
        'Fix 8: Surface ambience connects to ambienceBus'
    )
]

for orig, repl, desc in replacements:
    count = html.count(orig)
    if count == 1:
        html = html.replace(orig, repl)
        print(f'[OK] {desc}')
    else:
        print(f'[ERROR] {desc}: count={count}')
        raise RuntimeError(f'Replacement failed for {desc}')

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print('starfield.html updated successfully.')


# ==============================================================================
# 2. Update MainActivity.java (Fix 10 & Fix 14)
# ==============================================================================
with open(MAIN_JAVA, 'r', encoding='utf-8') as f:
    java_code = f.read()

# Fix 10: syncAssets flash write storm
orig_sync = '''    private void syncAssets() {
        for (String name : MIRRORED_ASSETS) {
            try {
                File out = new File(getFilesDir(), name);
                long assetLen = -1;
                try (InputStream probe = getAssets().open(name)) { assetLen = probe.available(); }
                catch (Exception ignored) {}
                // Copy when the asset changed: the old "skip if it exists" left the
                // previous icon and version.json in place forever after an upgrade.
                if (out.exists() && out.length() > 0 && (assetLen <= 0 || out.length() == assetLen)) continue;
                if (out.getParentFile() != null) out.getParentFile().mkdirs();
                try (InputStream in = getAssets().open(name)) {
                    copyStream(in, out);
                }
            } catch (Exception e) {
                // Not packaged, or not copyable: the page has a CDN fallback for
                // three.js and degrades quietly for the rest.
                Log.w("StarfieldOTA", "asset " + name + " not mirrored: " + e);
            }
        }
    }'''

repl_sync = '''    private static final String KEY_ASSETS_SYNCED_BUILD = "assets_synced_bundled_build";

    /**
     * Copies the small assets the page resolves relatively into filesDir, so the
     * OTA'd copy of starfield.html can still find libs/three.min.js, its manifest
     * and its icons.
     * Build 197 optimization: Gated by bundled build timestamp in SharedPreferences to prevent
     * repeating 1MB uncompressed disk write storm on every cold startup.
     */
    private void syncAssets() {
        long currentBuild = readBundledBuild();
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        long lastSyncedBuild = prefs.getLong(KEY_ASSETS_SYNCED_BUILD, -1L);
        boolean needsSync = (currentBuild <= 0 || currentBuild != lastSyncedBuild);

        for (String name : MIRRORED_ASSETS) {
            try {
                File out = new File(getFilesDir(), name);
                if (!needsSync && out.exists() && out.length() > 0) {
                    continue;
                }
                if (out.getParentFile() != null) out.getParentFile().mkdirs();
                try (InputStream in = getAssets().open(name)) {
                    copyStream(in, out);
                }
            } catch (Exception e) {
                // Not packaged, or not copyable: the page has a CDN fallback for
                // three.js and degrades quietly for the rest.
                Log.w("StarfieldOTA", "asset " + name + " not mirrored: " + e);
            }
        }
        if (currentBuild > 0) {
            prefs.edit().putLong(KEY_ASSETS_SYNCED_BUILD, currentBuild).apply();
        }
    }'''

if java_code.count(orig_sync) == 1:
    java_code = java_code.replace(orig_sync, repl_sync)
    print('[OK] Fix 10: MainActivity.syncAssets flash write storm resolved')
else:
    raise RuntimeError('Fix 10: orig_sync not found or duplicate in MainActivity.java')

# Fix 14: Downward compatibility permission check stub for Android 7.0-9.0
orig_perm_hook = '''        // Setup Edge-to-Edge full immersive sticky layout
        setupImmersiveFullscreen();'''

repl_perm_hook = '''        // Setup Edge-to-Edge full immersive sticky layout
        setupImmersiveFullscreen();

        // Build 197: Downward storage permission safety check for legacy devices (API <= 28)
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
            try {
                if (checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                        != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{android.Manifest.permission.WRITE_EXTERNAL_STORAGE}, 101);
                }
            } catch (Throwable ignored) {}
        }'''

if java_code.count(orig_perm_hook) == 1:
    java_code = java_code.replace(orig_perm_hook, repl_perm_hook)
    print('[OK] Fix 14: MainActivity downward permission check added')
else:
    raise RuntimeError('Fix 14: orig_perm_hook not found or duplicate in MainActivity.java')

with open(MAIN_JAVA, 'w', encoding='utf-8') as f:
    f.write(java_code)
print('MainActivity.java updated successfully.')


# ==============================================================================
# 3. Update version.json (Build 197)
# ==============================================================================
version_data = {
  "version": "1.9.9.9.9.9",
  "build": 197,
  "updated_at": "2026-11-20T08:00:00+08:00",
  "min_native_version": "1.0.0",
  "is_beta": False,
  "title": "跨端对抗实测全景收敛与架构韧性修复：超宽带鱼屏视口纠偏、模态返回键闭环、机体动力防穿透与原生冷启闪存加速 (Build 197)",
  "changelog": "1. 根治抽卡档案模态窗状态脱节与安卓物理返回键闪退（P0）：重构isModalOpen与closeModal支持.on类名，__sfBack补齐更多托盘、抽卡、改装与专注弹窗层级，并联动StarfieldHatch.hide()优雅切断音效；\n2. 封堵主动力丧失POWER LOSS加速穿透漏洞（P0）：在setHold、throttleUp、cycle与setWarpGear中全面注入SFHazard.hull < 25与isDrifting动力总线锁定检查，彻底阻断危态强行跃迁漏洞；\n3. 归还键盘Tab焦点导航键与a11y无障碍（P0）：移除Tab对星图手札的强行劫持，保留KeyJ图鉴，并将KeyK专属赋予旗舰特写/驾驶舱视角快捷切换；\n4. 纠偏21:9与32:9超宽带鱼屏视口与消解FOV透视畸变（P1）：动态映射宽高比计算baseDeskCx，并根据宽高比实施水平FOV不超过92°的最小焦距几何约束，根治马鞍形拉伸与偏心；\n5. 恢复驾驶舱特写视角操舵控制（P1）：修正updateWind中wind.x/y的autoCamera判断，允许cockpitMode操舵转向，并联动触控手势响应；\n6. 根治移动端双指捏合缩放横滚撕裂（P1）：在onPointerMove中引入多指互斥锁，多指缩放时严格屏蔽单指视角俯仰与偏航旋转；\n7. 消除移动端3D活体星球纹理串色与画布劫持（P1）：禁止移动端直出单例WebGL canvas，统一通过model.canvas隔离回贴，杜绝跨星体贴图污染；\n8. 音频拓扑纠偏与旁白后台暂停（P1）：将地表与天体氛围白噪从sfxBus重定向接入专用ambienceBus，并在visibilitychange与blur失焦时主动挂起原生Narrator解说音频；\n9. 瓦解虚拟摇杆左下角45vw x 55vh隐形触控盲区（P1）：从长按加速排除区解绑sf-touch-joy-zone，实现摇杆静触跃迁加速与滑移转向的无缝兼顾；\n10. 根治Android冷启动主线程资产刷写风暴（P1）：引入assets_synced_bundled_build首启版本记忆，避免每次启动重写1MB闪存，显著降低冷启延迟与磨损；\n11. 解决深空粒子边界硬裁剪突兀消失Popping（P2）：根据萤火粒子实际光晕半径（s*4）动态扩展剔除安全边距，杜绝边缘骤灭闪烁；\n12. 彻底激活胶片噪点安慰剂开关（P2）：建立window.grainOn引擎响应，在主管线paperFinish中真正拦截grainPattern全屏绘制，释放低端机渲染负载；\n13. 补齐全局window.pointercancel监听（P2）：防止多任务与系统边缘手势切出时触控指针常驻导致交互冻结；\n14. 注入Android 7.0~9.0存储权限向下兼容桩（P2）：确保老旧系统媒体与截图导出安全无崩。",
  "entry": "starfield.html",
  "download_url": "https://jackeyloveseven.github.io/starfield/starfield.html",
  "apk_release_url": "https://github.com/jackeyloveseven/starfield/releases/tag/v1.19.1-focus-apk"
}

with open(VERSION_JSON, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('version.json updated successfully.')


# ==============================================================================
# 4. Update service-worker.js
# ==============================================================================
with open(SW_FILE, 'r', encoding='utf-8') as f:
    sw = f.read()

orig_sw = "const CACHE_VERSION = 'v1.9.9.9.9.8-b196';"
repl_sw = "const CACHE_VERSION = 'v1.9.9.9.9.9-b197';"

if sw.count(orig_sw) == 1:
    sw = sw.replace(orig_sw, repl_sw)
    with open(SW_FILE, 'w', encoding='utf-8') as f:
        f.write(sw)
    print('[OK] service-worker.js cache version bumped to v1.9.9.9.9.9-b197')
else:
    raise RuntimeError('service-worker.js CACHE_VERSION replacement failed')


# ==============================================================================
# 5. Mirror Parity to Android Assets
# ==============================================================================
android_assets_dir = os.path.join(BASE_DIR, 'android', 'app', 'src', 'main', 'assets')

files_to_sync = [
    'starfield.html',
    'version.json',
    'service-worker.js'
]

print('\nMirroring synced assets to Android assets directory...')
for filename in files_to_sync:
    src = os.path.join(BASE_DIR, filename)
    dst = os.path.join(android_assets_dir, filename)
    shutil.copy2(src, dst)
    
    # SHA256 parity verification
    with open(src, 'rb') as f:
        src_h = hashlib.sha256(f.read()).hexdigest()
    with open(dst, 'rb') as f:
        dst_h = hashlib.sha256(f.read()).hexdigest()
    
    if src_h == dst_h:
        print(f'[PARITY 100%] {filename}: SHA256={src_h[:16]}...')
    else:
        raise RuntimeError(f'Hash mismatch for {filename}: {src_h} vs {dst_h}')

print('\nAll Build 197 updates applied and verified successfully!')
