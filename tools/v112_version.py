"""V112: show the APK's version, and the page build beside it.

The bridge reported `prefs[KEY_VERSION]` with a "1.1.0" fallback and
`prefs[KEY_BUILD]` with 0, so a freshly installed app announced
"v1.1.0 (Build 0)" no matter what it was. Those prefs describe the *ota* state,
not the app. The app version now comes from the package itself, and the OTA
build is appended when one has landed.

Also bumps the version tag to 1.1.9 / Build 111.

Run:  python -I v112_version.py <in.html> <out.html>
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


rep("v1.1.8 (Build 110)", "v1.1.9 (Build 111)")

rep("""        } catch (e) { /* older APK */ }
        vTag.textContent = 'v' + window.StarfieldNative.getAppVersion() + build;""",
    """        } catch (e) { /* older APK */ }
        // The page can be newer than the APK (that is the whole point of OTA),
        // so say which page is running when one has been installed.
        let ota = '';
        try {
          if (typeof window.StarfieldNative.getOtaBuild === 'function') {
            const b = window.StarfieldNative.getOtaBuild();
            if (b > 0) ota = ' · 页面 ' + b;
          }
        } catch (e) { /* older APK */ }
        vTag.textContent = 'v' + window.StarfieldNative.getAppVersion() + build + ota;""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V112 written:", len(src), "chars")
