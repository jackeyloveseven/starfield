"""V144: gravitational time dilation for the deep-space focus timer.

Near Gargantua the focus clock runs on proper time:

    d = sqrt(1 - rs / r)

with r the distance from the lead craft to the hole and rs the Schwarzschild
radius implied by the artwork's shadow. The GLSL hole shader integrates null
geodesics with rs = 1 and paints the shadow at CRIT = 2.598 (the critical
impact parameter b = 3*sqrt(3)*M = 2.598 rs). drawMass() feeds the shader a
screen radius of m.r * focal / dist, and the shader maps that radius onto
2.598, so one rs is m.r / 2.598 world units (m.r = 3500 -> rs ~= 1347.2).

The focus engine therefore advances its elapsed proper time by wall-clock
dt * d. The requested 15/30/60 minute targets stay in proper time: beside the
horizon a 25-minute session simply takes longer outside. window.SF_TIME_DILATION
defaults to true; setting it to false makes d = 1 everywhere and restores the
pre-patch timing/UI.

Every replacement is asserted to occur exactly once.

Run:  python -I v144_dilation.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v144_dilation.py <in.html> <out.html>")

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8", newline="").read()

if "sfFocusDilation" in src or "SF_TIME_DILATION" in src:
    sys.exit("v144 already present in input")

out = src
reps = 0


def rep(label, old, new):
    global out, reps
    n = out.count(old)
    assert n == 1, f"{label}: expected 1 occurrence, found {n}"
    out = out.replace(old, new, 1)
    reps += 1


# 1. Pure, testable timing helpers + the live distance/dilation probe. These
#    sit in the same module scope as craftWorld/fleet/activeMasses, before the
#    frozen Starfield API object is built.
rep(
    "time-dilation helpers",
    "window.Starfield=Object.freeze({\n"
    " version:'v68-true-nadir-zenith-master',",
    """/* v144: gravitational time dilation at the Gargantua horizon.
 * d = sqrt(1 - rs/r) is the proper-time rate beside the hole relative to a
 * distant clock. The shader's rs is 1 and its shadow radius is 2.598, while
 * the sprite radius is m.r * focal / dist, so rs_world = m.r / 2.598. */
if (typeof window.SF_TIME_DILATION === 'undefined') window.SF_TIME_DILATION = true;
window.sfTimeDilation = function(rsRatio){
 const x = Number(rsRatio);
 if (!isFinite(x) || x <= 0) return 1;
 if (x >= 1) return 0;
 return Math.sqrt(1 - x);
};
window.sfFocusDilation = function(rsRatio){
 if (window.SF_TIME_DILATION === false) return 1;
 return window.sfTimeDilation(rsRatio);
};
window.sfFocusAdvance = function(elapsedSec, dtSec, d){
 const e = Number(elapsedSec), dt = Number(dtSec), k = Number(d);
 if (!isFinite(e)) return 0;
 if (!isFinite(dt) || dt <= 0) return e;
 const scale = isFinite(k) ? Math.max(0, Math.min(1, k)) : 1;
 return e + dt * scale;
};
window.sfDilationInfo = function(){
 const lw = craftWorld(fleet[LEAD]);
 let best = null, bd = 1e9;
 for (const m of activeMasses) {
  if (m.kind !== 4) continue;
  const dist = Math.hypot(lw[0] - m.x, lw[1] - m.y, lw[2] - m.z);
  if (dist < bd) { bd = dist; best = m; }
 }
 if (!best) return { d: 1, ratio: 0, r: Infinity, rs: 0, active: false, enabled: window.SF_TIME_DILATION !== false };
 const rs = (best.r || 3500) / 2.598;
 const ratio = rs / Math.max(bd, 1e-9);
 return { d: window.sfFocusDilation(ratio), ratio, r: bd, rs, active: true, enabled: window.SF_TIME_DILATION !== false };
};
window.Starfield=Object.freeze({
 version:'v68-true-nadir-zenith-master',
 getDilationInfo:()=>window.sfDilationInfo(),
 getTimeDilation:()=>window.sfDilationInfo().d,""",
)

# 2. Focus HUD/panel styling for the dilation readout.
rep(
    "focus dilation css",
    "@keyframes focusPulse {",
    """/* v144: dilation readout in the focus HUD and panels. */
.sf-focus-ticker-dilation {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(136, 192, 255, 0.13);
  color: #9ecbff;
  letter-spacing: 0.06em;
}
.sf-focus-ticker-warn {
  font-size: 9px;
  color: #ffb86b;
  letter-spacing: 0.06em;
}
.sf-focus-dilation-note {
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 184, 107, 0.35);
  background: rgba(255, 184, 107, 0.08);
  color: #ffcf9a;
  font-size: 11px;
  line-height: 1.55;
  letter-spacing: 0.04em;
  text-align: center;
}
@keyframes focusPulse {""",
)

# 3. Timer state: wall-clock anchor and last displayed d.
rep(
    "focus constructor",
    "      this.selectedPresetIndex = 2; // Default 30min\n"
    "      this.isDashboardOpen = false;\n"
    "\n"
    "      this.stats = this.loadStats();",
    """      this.selectedPresetIndex = 2; // Default 30min
      this.isDashboardOpen = false;
      // v144: wall-clock anchor and the last dilation factor used.
      this.lastTickMs = 0;
      this.dilation = 1;

      this.stats = this.loadStats();""",
)

# 4. Anchor the wall clock when a mission starts.
rep(
    "focus startMission",
    "      this.elapsedSec = 0;\n      this.state = 'RUNNING';\n",
    """      this.elapsedSec = 0;
      this.state = 'RUNNING';
      // v144: ticks integrate wall-clock dt * d, so anchor on start.
      this.lastTickMs = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
      this.dilation = this.currentDilation();
""",
)

# 5. The timer itself: dt is wall-clock; elapsed is proper time.
rep(
    "focus tick",
    """    tick() {
      if (this.state !== 'RUNNING') return;

      this.elapsedSec++;
      this.updateTickerHUD(true);

      // Check for mission completion
      if (this.elapsedSec >= this.targetDurationSec) {
        this.completeMission();
      }
    }
""",
    """    tick() {
      if (this.state !== 'RUNNING') return;

      // v144: advance proper (in-hole) time by wall-clock dt * d. A minute
      // beside the horizon is a longer minute outside; the target stays in
      // proper time, so 15/30/60 still mean the minutes you experience.
      const nowMs = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
      let dt = this.lastTickMs ? (nowMs - this.lastTickMs) / 1000 : 1;
      this.lastTickMs = nowMs;
      if (!isFinite(dt) || dt < 0) dt = 0;
      const d = this.currentDilation();
      this.dilation = d;
      this.elapsedSec = (typeof window.sfFocusAdvance === 'function')
        ? window.sfFocusAdvance(this.elapsedSec, dt, d)
        : this.elapsedSec + dt * d;
      this.updateTickerHUD(true);

      // Check for mission completion
      if (this.elapsedSec >= this.targetDurationSec) {
        this.completeMission();
      }
    }

    currentDilation() {
      if (window.SF_TIME_DILATION === false) return 1;
      const SF = window.Starfield;
      const d = (SF && SF.getTimeDilation) ? SF.getTimeDilation() : 1;
      return isFinite(d) ? Math.max(0, Math.min(1, d)) : 1;
    }
""",
)

# 6. Warning seconds are ordinary wall-clock, not focus time.
rep(
    "focus clearWarning",
    "      this.state = 'RUNNING';\n      showToast('[GRAVITY STABILIZED]",
    """      this.state = 'RUNNING';
      // v144: the warning seconds were wall-clock but not focus time; do not
      // dump that gap into the next tick.
      this.lastTickMs = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
      showToast('[GRAVITY STABILIZED]""",
)

# 7. Ticker HUD: show d, and a compact caution when d < 0.95.
rep(
    "focus ticker hud",
    """      ticker.innerHTML = `
        <div class="sf-focus-pulse-dot"></div>
        <span class="sf-focus-ticker-tag">FOCUS</span>
        <span class="sf-focus-ticker-time">${timeStr}</span>
        <span class="sf-focus-ticker-sub">AUTONOMOUS CRUISE</span>
      `;
""",
    """      const dilationOn = (window.SF_TIME_DILATION !== false);
      const dNow = this.dilation || 1;
      const dilTag = dilationOn
        ? `<span class="sf-focus-ticker-dilation">引力时间 ×${dNow.toFixed(2)}</span>`
        : '';
      const dilWarn = (dilationOn && dNow < 0.95)
        ? `<span class="sf-focus-ticker-warn">洞外时间更快</span>`
        : '';
      ticker.title = (dilationOn && dNow < 0.95) ? '你正在黑洞旁专注，洞外时间流逝更快' : '';
      ticker.innerHTML = `
        <div class="sf-focus-pulse-dot"></div>
        <span class="sf-focus-ticker-tag">FOCUS</span>
        <span class="sf-focus-ticker-time">${timeStr}</span>
        <span class="sf-focus-ticker-sub">AUTONOMOUS CRUISE</span>
        ${dilTag}${dilWarn}
      `;
""",
)

# 8. Pre-flight dashboard: show the current rate and the full caution.
rep(
    "focus dashboard line",
    """      content.innerHTML = `
        <div class="sf-focus-badge">FOCUS EXPEDITION // CHRONO FLOW</div>
        <h2>深空专注远征 · 番茄钟心流</h2>
""",
    """      const _dil = (window.SF_TIME_DILATION !== false && window.Starfield && window.Starfield.getDilationInfo)
        ? window.Starfield.getDilationInfo() : null;
      const _dilLine = (_dil && _dil.active)
        ? `<div class="sf-focus-dilation-note">当前引力时间 ×${_dil.d.toFixed(2)}${_dil.d < 0.95 ? '<br>你正在黑洞旁专注，洞外时间流逝更快' : ''}</div>`
        : '';
      content.innerHTML = `
        <div class="sf-focus-badge">FOCUS EXPEDITION // CHRONO FLOW</div>
        <h2>深空专注远征 · 番茄钟心流</h2>
        ${_dilLine}
""",
)

# 9. Active status dialog: read the live rate when it opens.
rep(
    "focus active dialog readout",
    "      const distance = (travelVal * 0.001).toFixed(1);\n",
    """      const distance = (travelVal * 0.001).toFixed(1);
      // v144: the live gravitational time rate, read at panel open.
      const dilationOn = (window.SF_TIME_DILATION !== false);
      const dilInfo = (dilationOn && window.Starfield && window.Starfield.getDilationInfo)
        ? window.Starfield.getDilationInfo() : { d: 1 };
      const dilD = (dilInfo && isFinite(dilInfo.d)) ? dilInfo.d : 1;
      const dilRow = dilationOn ? `<div><span>引力时间</span><b>×${dilD.toFixed(2)}</b></div>` : '';
      const dilNote = (dilationOn && dilD < 0.95)
        ? '<div class="sf-focus-dilation-note">你正在黑洞旁专注，洞外时间流逝更快</div>' : '';
""",
)

# 10. Active status dialog: the fourth stat and the full caution.
rep(
    "focus active dialog stats",
    """        <div class="sf-focus-stats-row">
          <div><span>剩余时间</span><b style="font-size:20px;color:#fff3a8;">${timeStr}</b></div>
          <div><span>当前里程</span><b>${distance} KLY</b></div>
          <div><span>目标时长</span><b>${Math.round(this.targetDurationSec / 60)} 分钟</b></div>
        </div>
""",
    """        <div class="sf-focus-stats-row">
          <div><span>剩余时间</span><b style="font-size:20px;color:#fff3a8;">${timeStr}</b></div>
          <div><span>当前里程</span><b>${distance} KLY</b></div>
          <div><span>目标时长</span><b>${Math.round(this.targetDurationSec / 60)} 分钟</b></div>
          ${dilRow}
        </div>
        ${dilNote}
""",
)

open(out_p, "w", encoding="utf-8", newline="").write(out)
print(f"v144 wrote {out_p} ({len(src)} -> {len(out)} chars, {reps} replacements)")
