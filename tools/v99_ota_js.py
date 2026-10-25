"""V99: the OTA handshake, from the page's side.

What was wrong (all of it visible in the Android build):

1. The native side reported failures with type 'OTA_ERROR' and the page only
   handled 'OTA_READY'. Every failure was therefore silent: the manual check
   showed "正在向 GitHub Pages 查询..." and then nothing, ever. That is what
   "热更新总是失败" looks like from the outside.
2. The native side sends the version as a bare string ('1.1.2'), but
   showOtaNotification() reads payload.version / payload.changelog, so the pill
   always announced the hard-coded fallback v1.1.0 - it looked stale even when
   the update had worked.
3. Settings called window.StarfieldNative.getBuildNumber(), which the bridge
   never defined, so the version tag threw and never updated.
4. A manual check with nothing new re-downloaded 21 MB and gave no confirmation.

Run:  python -I v99_ota_js.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()


def rep(a, b):
    global src
    n = src.count(a)
    if n != 1:
        sys.exit("count=%d (want 1): %r" % (n, a[:120]))
    src = src.replace(a, b, 1)


# 1. the payload may be a string (old APK) or an object (new APK)
rep("""    const version = payload && payload.version ? payload.version : 'v1.1.0';
    const desc = payload && payload.changelog ? payload.changelog : '核心视觉与2K清晰度已优化，轻触立即热更新生效';""",
    """    // The native bridge used to send a bare string, the new one sends
    // {version, build, changelog}. Accept both.
    const info = (payload && typeof payload === 'object') ? payload : { version: payload };
    const rawVer = info.version ? String(info.version) : '1.1.0';
    const version = 'v' + rawVer.replace(/^v/i, '');
    const desc = info.changelog || '核心视觉与2K清晰度已优化，轻触立即热更新生效';""")

# 2. every terminal state of the handshake gets a voice
rep("""    if (type === 'OTA_READY') {
      showOtaNotification(payload);
    }
  };""",
    """    if (type === 'OTA_READY') {
      showOtaNotification(payload);
    } else if (type === 'OTA_ERROR') {
      // A silent failure is indistinguishable from a dead button: the manual
      // check said "querying" and then never said anything again.
      if (window.toast) window.toast('热更新失败 · ' + (payload || '未知原因'), 7);
      console.warn('[OTA] failed:', payload);
    } else if (type === 'OTA_UP_TO_DATE') {
      if (window.toast) window.toast('已是最新版本 · v' + String(payload).replace(/^v/i, ''), 4);
    }
  };""")

# 3. the bridge has no getBuildNumber()
rep("""    if (window.StarfieldNative && typeof window.StarfieldNative.getAppVersion === 'function') {
      const vTag = $('sf-version-tag');
      if (vTag) vTag.textContent = `v${window.StarfieldNative.getAppVersion()} (Build ${window.StarfieldNative.getBuildNumber()})`;
    }""",
    """    if (window.StarfieldNative && typeof window.StarfieldNative.getAppVersion === 'function') {
      const vTag = $('sf-version-tag');
      if (vTag) {
        // getBuildNumber() did not exist on the bridge, so this line threw and
        // the tag stayed at its hard-coded value forever.
        let build = '';
        try {
          if (typeof window.StarfieldNative.getBuildNumber === 'function') {
            build = ' (Build ' + window.StarfieldNative.getBuildNumber() + ')';
          }
        } catch (e) { /* older APK */ }
        vTag.textContent = 'v' + window.StarfieldNative.getAppVersion() + build;
      }
    }""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V99 written:", len(src), "chars")
