package com.starfield.focus;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "starfield_ota_prefs";
    private static final String KEY_BUILD = "ota_build_timestamp";
    private static final String KEY_VERSION = "ota_version";
    private static final String OTA_VERSION_URL = "https://jackeyloveseven.github.io/starfield/version.json";
    private static final String OTA_HTML_URL = "https://jackeyloveseven.github.io/starfield/starfield.html";
    /** The page is ~21 MB. Anything under this is a truncated download, not a build. */
    private static final long MIN_HTML_BYTES = 4_000_000L;
    /** Assets the page resolves relatively; they must sit next to the OTA'd HTML. */
    private static final String[] MIRRORED_ASSETS = {
        "libs/three.min.js", "libs/tween.umd.js", "libs/OrbitControls.js",
        "manifest.json", "icon-192.png", "icon-512.png",
        "service-worker.js", "version.json", "planet_studio.html"
    };

    private WebView webView;
    private final ExecutorService otaExecutor = Executors.newSingleThreadExecutor();
    /** True once the page has finished loading; before that its inline script may
     *  still be parsing and would drop an evaluateJavascript() call. */
    private volatile boolean pageReady = false;
    private String pendingNotify = null;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Keep screen on for ambient desk-clock Pomodoro focus voyage
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        // Setup Edge-to-Edge full immersive sticky layout
        setupImmersiveFullscreen();

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);

        // Hardware acceleration comes from android:hardwareAccelerated="true".
        // Do NOT call setLayerType(LAYER_TYPE_HARDWARE) here: it forces the whole
        // WebView into one hardware layer, so every canvas frame re-uploads the
        // layer instead of going through the normal compositor path, and on many
        // devices that costs more than half the frame rate.
        webView.setBackgroundColor(0xFF0B1118);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                pageReady = true;
                if (pendingNotify != null) {
                    String js = pendingNotify;
                    pendingNotify = null;
                    view.evaluateJavascript(js, null);
                }
            }
        });

        // Expose Native Bridge for JS In-App Hot Updates
        webView.addJavascriptInterface(new StarfieldNativeBridge(), "StarfieldNative");

        // The OTA'd page lives in filesDir, where ./libs/... and ./manifest.json
        // do not exist unless they are copied out of the APK first.
        syncAssets();

        // 1. Initial Page Load (Cached active update file or bundled asset fallback)
        File activeHtml = new File(getFilesDir(), "starfield_active.html");
        if (activeHtml.exists() && activeHtml.length() > 500000) {
            webView.loadUrl("file://" + activeHtml.getAbsolutePath());
        } else {
            webView.loadUrl("file:///android_asset/starfield.html");
        }

        // 2. Asynchronously check for Cloud OTA Hot-Updates
        triggerOtaCheck(false);
    }

    private void setupImmersiveFullscreen() {
        // Kept deliberately boring: the cutout/insets path added in 1.2.x is the
        // newest native code and the prime suspect for the launch crash on a
        // 1280x2772 device. Everything here is wrapped so a display quirk can
        // never take the activity down before the WebView is on screen.
        try {
            Window window = getWindow();
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                window.setDecorFitsSystemWindows(false);
            } else {
                View decorView = window.getDecorView();
                decorView.setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                );
            }
        } catch (Throwable t) {
            Log.w("StarfieldOTA", "fullscreen setup failed", t);
        }
    }

    /**
     * Copies the small assets the page resolves relatively into filesDir, so the
     * OTA'd copy of starfield.html can still find libs/three.min.js, its manifest
     * and its icons. Skipped when already present.
     */
    private void syncAssets() {
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
    }

    private void copyStream(InputStream in, File to) throws Exception {
        try (FileOutputStream out = new FileOutputStream(to)) {
            byte[] buffer = new byte[16384];
            int read;
            while ((read = in.read(buffer)) != -1) out.write(buffer, 0, read);
        }
    }

    /** A truncated download ends mid-JSON or mid-script; a real build ends with </html>. */
    private boolean endsWithHtmlClose(File f) {
        try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(f, "r")) {
            long len = raf.length();
            int n = (int) Math.min(96, len);
            byte[] tail = new byte[n];
            raf.seek(len - n);
            raf.readFully(tail);
            return new String(tail, "UTF-8").toLowerCase().contains("</html");
        } catch (Exception e) {
            return false;
        }
    }

    public void triggerOtaCheck(final boolean isManual) {
        otaExecutor.execute(() -> {
            String stage = "版本查询";
            try {
                SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
                long currentBuild = prefs.getLong(KEY_BUILD, 0L);

                // 1. Fetch remote version descriptor
                URL vUrl = new URL(OTA_VERSION_URL);
                HttpURLConnection conn = (HttpURLConnection) vUrl.openConnection();
                // 4 s was tight for GitHub Pages on a mobile network; a timeout
                // there was reported as "network error" and nothing else.
                conn.setConnectTimeout(15000);
                conn.setReadTimeout(20000);
                conn.setRequestMethod("GET");
                conn.setUseCaches(false);
                conn.setRequestProperty("Cache-Control", "no-cache");

                int code = conn.getResponseCode();
                if (code != 200) {
                    fail(isManual, "云端检查失败 (HTTP " + code + ")");
                    return;
                }

                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) sb.append(line);
                reader.close();

                JSONObject obj = new JSONObject(sb.toString());
                long remoteBuild = obj.optLong("timestamp", obj.optLong("build", 0L));
                String remoteVersion = obj.optString("version", "1.1.0");
                String changelog = obj.optString("changelog", "");

                // A manual check used to re-download 21 MB even when nothing had
                // changed, and then said nothing about it.
                if (remoteBuild <= currentBuild) {
                    if (isManual) notifyJs("OTA_UP_TO_DATE", JSONObject.quote(remoteVersion));
                    return;
                }

                // 2. Download latest starfield.html
                stage = "下载更新包";
                URL htmlUrl = new URL(OTA_HTML_URL);
                HttpURLConnection htmlConn = (HttpURLConnection) htmlUrl.openConnection();
                htmlConn.setConnectTimeout(15000);
                htmlConn.setReadTimeout(45000);
                htmlConn.setRequestMethod("GET");
                htmlConn.setUseCaches(false);
                htmlConn.setRequestProperty("Cache-Control", "no-cache");

                if (htmlConn.getResponseCode() != 200) {
                    fail(isManual, "下载热更新包失败 (HTTP " + htmlConn.getResponseCode() + ")");
                    return;
                }
                long declared = htmlConn.getContentLengthLong();

                File tempFile = new File(getFilesDir(), "starfield_temp.html");
                try (InputStream in = htmlConn.getInputStream()) {
                    copyStream(in, tempFile);
                }

                // 3. Verify download integrity. 500 KB was the old floor, which
                // let a half-downloaded 21 MB page through and brick the app.
                stage = "校验更新包";
                long size = tempFile.length();
                if ((declared > 0 && size != declared) || size < MIN_HTML_BYTES
                        || !endsWithHtmlClose(tempFile)) {
                    tempFile.delete();
                    fail(isManual, "更新包不完整 (" + size + "/" + declared + ")");
                    return;
                }

                // 4. Atomically commit new active version
                stage = "写入新版本";
                File activeFile = new File(getFilesDir(), "starfield_active.html");
                File previous = new File(getFilesDir(), "starfield_prev.html");
                if (previous.exists()) previous.delete();
                if (activeFile.exists()) activeFile.renameTo(previous);
                if (!tempFile.renameTo(activeFile)) {
                    // renameTo fails silently on some devices/filesystems.
                    copyStream(new java.io.FileInputStream(tempFile), activeFile);
                    tempFile.delete();
                }
                if (activeFile.length() < MIN_HTML_BYTES) {
                    fail(isManual, "写入失败，保留旧版本");
                    return;
                }

                prefs.edit().putLong(KEY_BUILD, remoteBuild).putString(KEY_VERSION, remoteVersion).apply();

                // 5. Notify web app of hot update readiness
                JSONObject payload = new JSONObject();
                payload.put("version", remoteVersion);
                payload.put("build", remoteBuild);
                payload.put("changelog", changelog);
                notifyJs("OTA_READY", payload.toString());

            } catch (Exception e) {
                Log.w("StarfieldOTA", "check failed at " + stage, e);
                if (isManual) notifyJs("OTA_ERROR", JSONObject.quote(stage + "时出错: " + e.getMessage()));
            }
        });
    }

    private void fail(boolean isManual, String message) {
        Log.w("StarfieldOTA", message);
        if (isManual) notifyJs("OTA_ERROR", JSONObject.quote(message));
    }

    /** payload is already valid JSON: a quoted string, or an object literal. */
    private void notifyJs(final String type, final String payload) {
        final String js = "if(typeof window.onStarfieldOtaNotify==='function'){window.onStarfieldOtaNotify("
                + JSONObject.quote(type) + "," + payload + ");}";
        runOnUiThread(() -> {
            if (webView == null) return;
            if (pageReady) {
                webView.evaluateJavascript(js, null);
            } else {
                // The page is 21 MB; its inline script can still be parsing when
                // the download finishes. Hold the message for onPageFinished.
                pendingNotify = js;
            }
        });
    }

    public class StarfieldNativeBridge {
        @JavascriptInterface
        public void checkOtaUpdate() {
            triggerOtaCheck(true);
        }

        @JavascriptInterface
        public void reloadApp() {
            runOnUiThread(() -> {
                pageReady = false;
                File active = new File(getFilesDir(), "starfield_active.html");
                if (active.exists() && active.length() > 500000) {
                    webView.loadUrl("file://" + active.getAbsolutePath());
                } else {
                    webView.reload();
                }
            });
        }

        /**
         * The APK's own version, not the OTA state. Reporting the prefs fallback
         * here is why a freshly installed app showed "v1.1.0 (Build 0)".
         */
        @JavascriptInterface
        public String getAppVersion() {
            try {
                return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "1.1.0";
            }
        }

        @JavascriptInterface
        public long getBuildNumber() {
            try {
                android.content.pm.PackageInfo pi =
                        getPackageManager().getPackageInfo(getPackageName(), 0);
                return Build.VERSION.SDK_INT >= 28 ? pi.getLongVersionCode() : pi.versionCode;
            } catch (Exception e) {
                return 0L;
            }
        }

        /** Which page build the OTA has landed on, 0 when still on the bundled copy. */
        @JavascriptInterface
        public long getOtaBuild() {
            SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            return prefs.getLong(KEY_BUILD, 0L);
        }

        @JavascriptInterface
        public void setOrientation(String mode) {
            runOnUiThread(() -> {
                if ("landscape".equalsIgnoreCase(mode)) {
                    setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);
                } else if ("portrait".equalsIgnoreCase(mode)) {
                    setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
                } else {
                    setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
                }
            });
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            setupImmersiveFullscreen();
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        otaExecutor.shutdown();
    }
}
