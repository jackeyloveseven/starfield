import os
import sys

def apply_patch():
    file_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        src = f.read()

    def rep(old, new, desc=""):
        nonlocal src
        count = src.count(old)
        if count != 1:
            raise ValueError(f"Patch failed for '{desc}': found {count} occurrences (expected 1)")
        src = src.replace(old, new, 1)
        print(f"Applied: {desc}")

    # 1. Uncap getTargetFps in STARFIELD_QUALITY
    old_fps = """  getTargetFps() {
    if (this.profile === 'powersave') return 45;
    if (this.profile === 'balanced' || _isMobileDevice) return 60;
    return 0; // 0 = native display refresh rate (Desktop 2K mode)
  },"""

    new_fps = """  getTargetFps() {
    // 帧率不设人为上限：全模式畅享屏幕原生刷新率 (60Hz/90Hz/120Hz/144Hz/240Hz 满血高刷)
    if (this.profile === 'powersave') return 45;
    return 0; // 0 = 无上限，跟随屏幕物理硬件最高刷新率
  },"""
    rep(old_fps, new_fps, "Uncap targetFps to 0 (Native screen refresh rate)")

    # 2. Update toast & labels in setProfile
    old_labels = """      const labels = { '2k': '2K 极清视网膜 (Retina Ultra)', 'balanced': '均衡高清模式 (Smooth 60fps)', 'powersave': '能效省电模式 (Battery Saver)' };"""
    new_labels = """      const labels = { '2k': '2K 极清视网膜 (Retina Ultra)', 'balanced': '极速高刷模式 (Native High Hz)', 'powersave': '能效省电模式 (Battery Saver)' };"""
    rep(old_labels, new_labels, "Update profile labels for uncapped high-refresh")

    # 3. Cache CSS filter strings in gradeFor(p)
    old_grade = """let gradeCache='',gradeKey=-1;
let smoothGradeV0 = 14.0;
function gradeFor(p){
 const L = .2126*p.sky[0] + .7152*p.sky[1] + .0722*p.sky[2];
 const v0 = clamp(L * .62, 4, 30);
 smoothGradeV0 += (v0 - smoothGradeV0) * 0.08;
 const A = 1.40;
 const c = clamp(1 + 2 * A * smoothGradeV0 / 255, .02, 3), k = A / c;
 return 'brightness(' + k.toFixed(3) + ') contrast(' + c.toFixed(3) + ') saturate(1.14)';
}"""

    new_grade = """let gradeCache='',gradeKey=-1;
let smoothGradeV0 = 14.0;
let lastGradeStr = '';
let lastGradeV0 = -1;
function gradeFor(p){
 const L = .2126*p.sky[0] + .7152*p.sky[1] + .0722*p.sky[2];
 const v0 = clamp(L * .62, 4, 30);
 smoothGradeV0 += (v0 - smoothGradeV0) * 0.08;
 if (Math.abs(smoothGradeV0 - lastGradeV0) < 0.02 && lastGradeStr) return lastGradeStr;
 lastGradeV0 = smoothGradeV0;
 const A = 1.40;
 const c = clamp(1 + 2 * A * smoothGradeV0 / 255, .02, 3), k = A / c;
 lastGradeStr = 'brightness(' + k.toFixed(3) + ') contrast(' + c.toFixed(3) + ') saturate(1.14)';
 return lastGradeStr;
}"""
    rep(old_grade, new_grade, "gradeFor filter string caching for high-fps throughput")

    # 4. Adaptive downscaler threshold smoothing
    old_scaler = """  const is2k = (window.STARFIELD_QUALITY && window.STARFIELD_QUALITY.profile === '2k');
  const downFloor = is2k ? 32 : Math.min(42, Math.max(30, refreshHz * 0.5));
  const recCeil = is2k ? 45 : Math.min(54, refreshHz * 0.88);
  if(fps<downFloor&&qualityScale>.8){qualityScale=Math.max(.8,qualityScale-.1);resize();}
  else if(fps>recCeil&&qualityScale<1&&++fastWindows>2){qualityScale=Math.min(1,qualityScale+.1);fastWindows=0;resize();}
  if(fps<=recCeil)fastWindows=0;"""

    new_scaler = """  const is2k = (window.STARFIELD_QUALITY && window.STARFIELD_QUALITY.profile === '2k');
  // 高刷自适应平滑：降级阈值设为绝对卡顿红线 (2K: 30fps, 均衡: 38fps)，避免高刷波动被误降质
  const downFloor = is2k ? 30 : Math.min(38, Math.max(28, refreshHz * 0.40));
  const recCeil = is2k ? 45 : Math.min(50, refreshHz * 0.75);
  if(fps < downFloor && qualityScale > .8){qualityScale = Math.max(.8, qualityScale - .1); resize();}
  else if(fps > recCeil && qualityScale < 1 && ++fastWindows > 2){qualityScale = Math.min(1, qualityScale + .1); fastWindows = 0; resize();}
  if(fps <= recCeil) fastWindows = 0;"""
    rep(old_scaler, new_scaler, "Adaptive downscaler threshold smoothing for uncapped high-refresh")

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("SUCCESS: starfield.html updated for uncapped high-refresh & pipeline optimization!")

if __name__ == "__main__":
    apply_patch()
