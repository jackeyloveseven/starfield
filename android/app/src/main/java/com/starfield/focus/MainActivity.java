package com.starfield.focus;

import android.annotation.SuppressLint;
import android.app.WallpaperManager;
import android.content.ComponentName;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.SystemClock;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.os.VibratorManager;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import android.view.Display;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.ViewGroup;
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
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "StarfieldNative";
    private static final String PREFS_NAME = "starfield_ota_prefs";
    private static final String KEY_BUILD = "ota_build_timestamp";
    private static final String KEY_VERSION = "ota_version";
    private static final String KEY_ASSETS_SYNCED_BUILD = "assets_synced_bundled_build";

    private static final String[] OTA_VERSION_URLS = {
        "https://raw.githubusercontent.com/jackeyloveseven/starfield/master/version.json",
        "https://jackeyloveseven.github.io/starfield/version.json"
    };
    private static final String OTA_HTML_URL = "https://raw.githubusercontent.com/jackeyloveseven/starfield/master/starfield.html";
    /** Minimum valid OTA HTML size guard (1 MB allows externalized audio builds while rejecting truncated responses). */
    private static final long MIN_HTML_BYTES = 1_000_000L;
    /** Assets the page resolves relatively; they must sit next to the OTA'd HTML. */
    private static final String[] MIRRORED_ASSETS = {
        "libs/three.min.js", "libs/tween.umd.js", "libs/OrbitControls.js", "libs/GLTFLoader.js",
        "manifest.json", "icon-192.png", "icon-512.png",
        "service-worker.js", "version.json", "planet_studio.html"
    };

    private static final int DEEP_SPACE_BG_COLOR = 0xFF060A10;

    private WebView webView;
    private final ExecutorService otaExecutor = Executors.newSingleThreadExecutor();
    private volatile long cachedBundledBuild = -1L;
    private volatile String cachedBundledVersion = null;
    /** True once the page has finished loading; before that its inline script may
     *  still be parsing and would drop an evaluateJavascript() call. */
    private volatile boolean pageReady = false;
    private volatile boolean keepScreenOnEnabled = true;
    private volatile float activeRefreshRate = 60.0f;
    private String pendingNotify = null;
    private long lastBack = 0L;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Window window = getWindow();
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        window.setFlags(
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED
        );
        window.getDecorView().setBackgroundColor(DEEP_SPACE_BG_COLOR);

        // Negotiate 120Hz+ display mode on high-refresh-rate flagships (e.g. Dimensity 9400+)
        requestHighRefreshRateDisplay();

        // Setup Edge-to-Edge full immersive sticky layout with display cutout support
        setupImmersiveFullscreen();

        // Downward storage permission safety check for legacy devices (API <= 28)
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
            try {
                if (checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                        != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{android.Manifest.permission.WRITE_EXTERNAL_STORAGE}, 101);
                }
            } catch (Throwable ignored) {}
        }

        webView = new WebView(this);
        webView.setBackgroundColor(DEEP_SPACE_BG_COLOR);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setVerticalScrollBarEnabled(false);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
        webView.setKeepScreenOn(true);
        // Do not force LAYER_TYPE_HARDWARE on the WebView root (avoids TBDR FBO blitting stalls;
        // hardware acceleration is active via Window FLAG_HARDWARE_ACCELERATED).
        webView.setLayerType(View.LAYER_TYPE_NONE, null);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            try {
                webView.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_IMPORTANT, true);
            } catch (Throwable ignored) {}
        }

        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                settings.setOffscreenPreRaster(true);
            } catch (Throwable ignored) {}
        }

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                pageReady = true;
                injectNativeBridgeEnhancements(view);
                if (pendingNotify != null) {
                    String js = pendingNotify;
                    pendingNotify = null;
                    view.evaluateJavascript(js, null);
                }
            }
        });

        // Expose Native Bridge for JS In-App Hot Updates, Haptics, Lifecycle & Device Telemetry
        webView.addJavascriptInterface(new StarfieldNativeBridge(), "StarfieldNative");

        // 1. Initial Page Load (Cached active update file or bundled asset fallback)
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        long currentBuild = normalizeBuildNumber(prefs.getLong(KEY_BUILD, 0L));
        long bundledBuild = getBundledBuild();

        File activeHtml = new File(getFilesDir(), "starfield_active.html");
        if (bundledBuild >= currentBuild && activeHtml.exists()) {
            activeHtml.delete();
            prefs.edit().putLong(KEY_BUILD, bundledBuild).apply();
        }

        boolean useActiveOtaFile = activeHtml.exists() && activeHtml.length() >= MIN_HTML_BYTES;
        if (useActiveOtaFile) {
            // OTA HTML lives in filesDir and needs mirrored relative assets immediately
            syncAssets();
            webView.loadUrl("file://" + activeHtml.getAbsolutePath());
        } else {
            // Bundled HTML resolves relative assets directly from android_asset/ with 0ms I/O wait;
            // mirror small assets asynchronously in the background for future OTA readiness.
            webView.loadUrl("file:///android_asset/starfield.html");
            otaExecutor.execute(this::syncAssets);
        }

        // 2. Asynchronously check for Cloud OTA Hot-Updates
        triggerOtaCheck(false);
    }

    /**
     * Requests the highest refresh-rate display mode (e.g., 120Hz / 144Hz on Dimensity 9400+)
     * matching the panel's native physical resolution so Android's SurfaceFlinger does not
     * lock the WebView Activity to a 60Hz compatibility mode.
     */
    private void requestHighRefreshRateDisplay() {
        try {
            Window window = getWindow();
            Display display = null;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                display = getDisplay();
            }
            if (display == null) {
                display = getWindowManager().getDefaultDisplay();
            }
            if (display == null) return;

            activeRefreshRate = display.getRefreshRate();
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                Display.Mode currentMode = display.getMode();
                Display.Mode[] modes = display.getSupportedModes();
                Display.Mode bestMode = currentMode;
                for (Display.Mode mode : modes) {
                    if (mode.getPhysicalWidth() == currentMode.getPhysicalWidth()
                            && mode.getPhysicalHeight() == currentMode.getPhysicalHeight()
                            && mode.getRefreshRate() > bestMode.getRefreshRate()) {
                        bestMode = mode;
                    }
                }
                WindowManager.LayoutParams lp = window.getAttributes();
                if (bestMode != null && bestMode.getModeId() != lp.preferredDisplayModeId) {
                    lp.preferredDisplayModeId = bestMode.getModeId();
                    lp.preferredRefreshRate = bestMode.getRefreshRate();
                    window.setAttributes(lp);
                    activeRefreshRate = bestMode.getRefreshRate();
                }
            }
        } catch (Throwable t) {
            Log.w(TAG, "High refresh rate negotiation skipped", t);
        }
    }

    /**
     * Configures edge-to-edge immersive fullscreen across all Android versions:
     * - Extends layout into display cutout / punch-hole regions (SHORT_EDGES).
     * - Hides status and navigation bars cleanly via WindowInsetsControllerCompat
     *   with transient swipe reveal.
     */
    private void setupImmersiveFullscreen() {
        try {
            Window window = getWindow();
            window.setStatusBarColor(Color.TRANSPARENT);
            window.setNavigationBarColor(Color.TRANSPARENT);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                WindowManager.LayoutParams lp = window.getAttributes();
                if (lp.layoutInDisplayCutoutMode
                        != WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES) {
                    lp.layoutInDisplayCutoutMode =
                            WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
                    window.setAttributes(lp);
                }
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                window.setNavigationBarContrastEnforced(false);
            }

            WindowCompat.setDecorFitsSystemWindows(window, false);
            View decorView = window.getDecorView();
            WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(window, decorView);
            if (controller != null) {
                controller.hide(WindowInsetsCompat.Type.systemBars());
                controller.setSystemBarsBehavior(
                    WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                );
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                WindowInsetsController nativeController = window.getInsetsController();
                if (nativeController != null) {
                    nativeController.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                    nativeController.setSystemBarsBehavior(
                        WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                    );
                }
            } else {
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
            Log.w(TAG, "Fullscreen setup warning", t);
        }
    }

    /**
     * Injects a lightweight JS polyfill that routes standard navigator.vibrate() calls
     * and window.StarfieldNativeHaptics helper methods directly to the native Android
     * haptic engine, and notifies listeners that the native shell is ready.
     */
    private void injectNativeBridgeEnhancements(WebView view) {
        final String js = "(function(){"
                + "if(window.__sfNativeBridgeEnhanced)return;"
                + "window.__sfNativeBridgeEnhanced=true;"
                + "var N=window.StarfieldNative;"
                + "if(!N)return;"
                + "window.StarfieldNativeHaptics={"
                + "trigger:function(s){try{N.triggerHaptic(String(s||'tick'));}catch(e){}},"
                + "tick:function(){try{N.triggerHaptic('tick');}catch(e){}},"
                + "light:function(){try{N.triggerHaptic('light');}catch(e){}},"
                + "medium:function(){try{N.triggerHaptic('medium');}catch(e){}},"
                + "heavy:function(){try{N.triggerHaptic('heavy');}catch(e){}},"
                + "success:function(){try{N.triggerHaptic('success');}catch(e){}},"
                + "warning:function(){try{N.triggerHaptic('warning');}catch(e){}}"
                + "};"
                + "try{"
                + "navigator.vibrate=function(p){"
                + "try{"
                + "if(Array.isArray(p)){N.vibratePattern(p.join(','));return true;}"
                + "var ms=Number(p)||18;"
                + "N.vibrate(ms);"
                + "return true;"
                + "}catch(e){return false;}"
                + "};"
                + "}catch(e){}"
                + "try{window.dispatchEvent(new CustomEvent('starfield:native-ready',{detail:{refreshRate:"
                + activeRefreshRate + "}}));}catch(e){}"
                + "})();";
        view.evaluateJavascript(js, null);
    }

    /**
     * Notifies the WebView JS runtime of native Activity lifecycle changes ('pause' / 'resume')
     * so WebAudio synthesizers and animation timers suspend cleanly in background and reset
     * frame delta clocks on resume without audio pops or dt spikes.
     */
    private void dispatchJsLifecycle(final String state, final boolean hidden) {
        if (webView == null || !pageReady) return;
        final String quoted = JSONObject.quote(state);
        final String js = "(function(){"
                + "try{if(typeof window.onStarfieldAppLifecycle==='function')window.onStarfieldAppLifecycle(" + quoted + ");}catch(e){}"
                + "try{if(typeof window.onStarfieldNativeLifecycle==='function')window.onStarfieldNativeLifecycle(" + quoted + ");}catch(e){}"
                + "try{window.dispatchEvent(new CustomEvent('starfield:lifecycle',{detail:{state:" + quoted + ",hidden:" + hidden + "}}));}catch(e){}"
                + "})();";
        webView.evaluateJavascript(js, null);
    }

    /**
     * Performs crisp native hardware haptics on the UI view and/or system Vibrator.
     */
    private void performNativeHaptic(final String style) {
        final String mode = (style == null ? "tick" : style.trim().toLowerCase());
        runOnUiThread(() -> {
            int feedbackConstant = HapticFeedbackConstants.CLOCK_TICK;
            if ("medium".equals(mode) || "click".equals(mode)) {
                feedbackConstant = HapticFeedbackConstants.CONTEXT_CLICK;
            } else if ("heavy".equals(mode) || "impact".equals(mode) || "warp".equals(mode)) {
                feedbackConstant = HapticFeedbackConstants.LONG_PRESS;
            } else if ("light".equals(mode)) {
                feedbackConstant = HapticFeedbackConstants.KEYBOARD_TAP;
            } else if ("success".equals(mode) || "confirm".equals(mode) || "slingshot".equals(mode) || "unlock".equals(mode)) {
                feedbackConstant = Build.VERSION.SDK_INT >= Build.VERSION_CODES.R
                        ? HapticFeedbackConstants.CONFIRM
                        : HapticFeedbackConstants.VIRTUAL_KEY;
            } else if ("warning".equals(mode) || "hazard".equals(mode) || "error".equals(mode)) {
                feedbackConstant = Build.VERSION.SDK_INT >= Build.VERSION_CODES.R
                        ? HapticFeedbackConstants.REJECT
                        : HapticFeedbackConstants.LONG_PRESS;
            }
            if (webView != null) {
                try {
                    webView.performHapticFeedback(
                        feedbackConstant,
                        HapticFeedbackConstants.FLAG_IGNORE_VIEW_SETTING
                    );
                } catch (Throwable ignored) {}
            }
        });

        try {
            Vibrator vibrator = getSystemVibrator();
            if (vibrator == null || !vibrator.hasVibrator()) return;

            // Check if style is a numeric duration in ms
            try {
                int customMs = Integer.parseInt(mode);
                if (customMs > 0) {
                    vibrateOneShot(vibrator, Math.min(customMs, 1000), 140);
                    return;
                }
            } catch (NumberFormatException ignored) {}

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                if ("tick".equals(mode) || "light".equals(mode)) {
                    vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK));
                    return;
                } else if ("medium".equals(mode) || "click".equals(mode)) {
                    vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK));
                    return;
                } else if ("heavy".equals(mode) || "impact".equals(mode) || "warp".equals(mode)) {
                    vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_HEAVY_CLICK));
                    return;
                } else if ("success".equals(mode) || "confirm".equals(mode) || "slingshot".equals(mode) || "unlock".equals(mode)) {
                    vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_DOUBLE_CLICK));
                    return;
                }
            }

            if ("warning".equals(mode) || "hazard".equals(mode) || "error".equals(mode)) {
                vibrateWaveform(vibrator, new long[]{0, 28, 40, 48});
            } else if ("success".equals(mode) || "confirm".equals(mode) || "slingshot".equals(mode) || "unlock".equals(mode)) {
                vibrateWaveform(vibrator, new long[]{0, 14, 30, 24});
            } else if ("heavy".equals(mode) || "impact".equals(mode) || "warp".equals(mode)) {
                vibrateOneShot(vibrator, 32, 220);
            } else if ("medium".equals(mode) || "click".equals(mode)) {
                vibrateOneShot(vibrator, 18, 160);
            } else {
                vibrateOneShot(vibrator, 10, 110);
            }
        } catch (Throwable ignored) {}
    }

    private Vibrator getSystemVibrator() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                VibratorManager vm = (VibratorManager) getSystemService(Context.VIBRATOR_MANAGER_SERVICE);
                if (vm != null) return vm.getDefaultVibrator();
            }
            return (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
        } catch (Throwable ignored) {
            return null;
        }
    }

    private void vibrateOneShot(Vibrator vibrator, int durationMs, int amplitude) {
        if (vibrator == null || durationMs <= 0) return;
        int clampedMs = Math.max(4, Math.min(durationMs, 1000));
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            int amp = vibrator.hasAmplitudeControl()
                    ? Math.max(1, Math.min(255, amplitude))
                    : VibrationEffect.DEFAULT_AMPLITUDE;
            vibrator.vibrate(VibrationEffect.createOneShot(clampedMs, amp));
        } else {
            vibrator.vibrate(clampedMs);
        }
    }

    private void vibrateWaveform(Vibrator vibrator, long[] pattern) {
        if (vibrator == null || pattern == null || pattern.length == 0) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1));
        } else {
            vibrator.vibrate(pattern, -1);
        }
    }

    /**
     * Normalizes build numbers so legacy 13-digit epoch timestamps (> 1_000_000_000L)
     * do not permanently overshadow canonical integer build numbers (e.g. Build 200).
     */
    private long normalizeBuildNumber(long buildOrTimestamp) {
        if (buildOrTimestamp > 1_000_000_000L) {
            return 0L;
        }
        return Math.max(0L, buildOrTimestamp);
    }

    /**
     * Copies the small assets the page resolves relatively into filesDir, so the
     * OTA'd copy of starfield.html can still find libs/three.min.js, its manifest
     * and its icons. Gated by bundled build number in SharedPreferences to avoid
     * redundant disk writes on subsequent launches.
     */
    private synchronized void syncAssets() {
        long currentBuild = getBundledBuild();
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
                Log.w("StarfieldOTA", "asset " + name + " not mirrored: " + e);
            }
        }
        if (currentBuild > 0) {
            prefs.edit().putLong(KEY_ASSETS_SYNCED_BUILD, currentBuild).apply();
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
        try (RandomAccessFile raf = new RandomAccessFile(f, "r")) {
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

    private void loadBundledVersionMetadata() {
        if (cachedBundledBuild >= 0 && cachedBundledVersion != null) return;
        try (InputStream is = getAssets().open("version.json")) {
            BufferedReader reader = new BufferedReader(new InputStreamReader(is, "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) sb.append(line);
            JSONObject json = new JSONObject(sb.toString());
            cachedBundledBuild = json.optLong("build", 0L);
            cachedBundledVersion = json.optString("version", "");
        } catch (Exception e) {
            Log.w("StarfieldOTA", "Failed to read bundled version.json", e);
            if (cachedBundledBuild < 0) cachedBundledBuild = 0L;
            if (cachedBundledVersion == null) cachedBundledVersion = "";
        }
    }

    private long getBundledBuild() {
        loadBundledVersionMetadata();
        return cachedBundledBuild;
    }

    private String getBundledVersion() {
        loadBundledVersionMetadata();
        return cachedBundledVersion;
    }

    public void triggerOtaCheck(final boolean isManual) {
        otaExecutor.execute(() -> {
            String stage = "版本查询";
            try {
                SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
                long savedBuild = normalizeBuildNumber(prefs.getLong(KEY_BUILD, 0L));
                long currentBuild = Math.max(getBundledBuild(), savedBuild);

                // 1. Fetch remote version descriptor (with multi-mirror fallback)
                JSONObject obj = null;
                String lastError = "";
                for (String vUrlStr : OTA_VERSION_URLS) {
                    try {
                        URL vUrl = new URL(vUrlStr);
                        HttpURLConnection conn = (HttpURLConnection) vUrl.openConnection();
                        conn.setConnectTimeout(15000);
                        conn.setReadTimeout(20000);
                        conn.setRequestMethod("GET");
                        conn.setUseCaches(false);
                        conn.setRequestProperty("Cache-Control", "no-cache");

                        int code = conn.getResponseCode();
                        if (code == 200) {
                            BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                            StringBuilder sb = new StringBuilder();
                            String line;
                            while ((line = reader.readLine()) != null) sb.append(line);
                            reader.close();
                            obj = new JSONObject(sb.toString());
                            break;
                        } else {
                            lastError = "HTTP " + code;
                        }
                    } catch (Exception e) {
                        lastError = e.getMessage();
                    }
                }

                if (obj == null) {
                    fail(isManual, "云端检查失败 (" + lastError + ")");
                    return;
                }

                long remoteBuild = obj.optLong("build", 0L);
                if (remoteBuild <= 0L) {
                    remoteBuild = normalizeBuildNumber(obj.optLong("timestamp", 0L));
                }
                String remoteVersion = obj.optString("version", "2.0.0.0");
                String changelog = obj.optString("changelog", "");

                if (remoteBuild <= currentBuild) {
                    if (isManual) notifyJs("OTA_UP_TO_DATE", JSONObject.quote(remoteVersion));
                    return;
                }

                // Ensure relative assets are mirrored before activating an OTA HTML file
                syncAssets();

                // 2. Download latest starfield.html (with descriptor download_url & fallback)
                stage = "下载更新包";
                String targetHtmlUrl = obj.optString("download_url", OTA_HTML_URL);
                URL htmlUrl = new URL(targetHtmlUrl);
                HttpURLConnection htmlConn = (HttpURLConnection) htmlUrl.openConnection();
                htmlConn.setConnectTimeout(15000);
                htmlConn.setReadTimeout(45000);
                htmlConn.setRequestMethod("GET");
                htmlConn.setUseCaches(false);
                htmlConn.setRequestProperty("Cache-Control", "no-cache");

                if (htmlConn.getResponseCode() != 200) {
                    if (!targetHtmlUrl.equals(OTA_HTML_URL)) {
                        htmlUrl = new URL(OTA_HTML_URL);
                        htmlConn = (HttpURLConnection) htmlUrl.openConnection();
                        htmlConn.setConnectTimeout(15000);
                        htmlConn.setReadTimeout(45000);
                        htmlConn.setRequestMethod("GET");
                        htmlConn.setUseCaches(false);
                        htmlConn.setRequestProperty("Cache-Control", "no-cache");
                    }
                }

                if (htmlConn.getResponseCode() != 200) {
                    fail(isManual, "下载热更新包失败 (HTTP " + htmlConn.getResponseCode() + ")");
                    return;
                }
                long declared = htmlConn.getContentLengthLong();

                File tempFile = new File(getFilesDir(), "starfield_temp.html");
                try (InputStream in = htmlConn.getInputStream()) {
                    copyStream(in, tempFile);
                }

                // 3. Verify download integrity
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
                    try (FileInputStream fis = new FileInputStream(tempFile)) {
                        copyStream(fis, activeFile);
                    }
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
                if (active.exists() && active.length() >= MIN_HTML_BYTES) {
                    webView.loadUrl("file://" + active.getAbsolutePath());
                } else {
                    webView.reload();
                }
            });
        }

        /**
         * Returns the active bundled or APK version string (e.g. "2.0.0.0").
         */
        @JavascriptInterface
        public String getAppVersion() {
            String bundledVer = getBundledVersion();
            if (bundledVer != null && !bundledVer.isEmpty()) {
                return bundledVer;
            }
            try {
                return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "2.0.0.0";
            }
        }

        @JavascriptInterface
        public long getBuildNumber() {
            long bundled = getBundledBuild();
            long pkgCode = 0L;
            try {
                PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
                pkgCode = Build.VERSION.SDK_INT >= 28 ? pi.getLongVersionCode() : pi.versionCode;
            } catch (Exception ignored) {}
            return Math.max(bundled, pkgCode);
        }

        /** Which page build the OTA has landed on, 0 when still on the bundled copy. */
        @JavascriptInterface
        public long getOtaBuild() {
            File activeHtml = new File(getFilesDir(), "starfield_active.html");
            if (!activeHtml.exists() || activeHtml.length() < MIN_HTML_BYTES) {
                return 0L;
            }
            SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            return normalizeBuildNumber(prefs.getLong(KEY_BUILD, 0L));
        }

        /**
         * Triggers crisp native haptic feedback.
         * Supported styles: 'tick' | 'light' | 'medium' | 'heavy' | 'success' | 'warning'
         * (plus aliases 'click', 'impact', 'warp', 'confirm', 'slingshot', 'hazard' or ms string).
         */
        @JavascriptInterface
        public void triggerHaptic(String style) {
            performNativeHaptic(style);
        }

        @JavascriptInterface
        public void vibrate(int durationMs) {
            try {
                Vibrator vibrator = getSystemVibrator();
                if (vibrator != null && vibrator.hasVibrator()) {
                    vibrateOneShot(vibrator, durationMs, 150);
                }
            } catch (Throwable ignored) {}
        }

        @JavascriptInterface
        public void vibratePattern(String csvPattern) {
            try {
                if (csvPattern == null || csvPattern.isEmpty()) return;
                String[] parts = csvPattern.split(",");
                long[] pattern = new long[parts.length + 1];
                pattern[0] = 0L;
                for (int i = 0; i < parts.length; i++) {
                    pattern[i + 1] = Math.max(0L, Math.min(1000L, Long.parseLong(parts[i].trim())));
                }
                Vibrator vibrator = getSystemVibrator();
                if (vibrator != null && vibrator.hasVibrator()) {
                    vibrateWaveform(vibrator, pattern);
                }
            } catch (Throwable ignored) {}
        }

        @JavascriptInterface
        public float getDisplayRefreshRate() {
            return activeRefreshRate;
        }

        @JavascriptInterface
        public void setKeepScreenOn(final boolean enabled) {
            keepScreenOnEnabled = enabled;
            runOnUiThread(() -> {
                try {
                    if (enabled) {
                        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                    } else {
                        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                    }
                    if (webView != null) {
                        webView.setKeepScreenOn(enabled);
                    }
                } catch (Throwable ignored) {}
            });
        }

        @JavascriptInterface
        public boolean isKeepScreenOn() {
            return keepScreenOnEnabled;
        }

        @JavascriptInterface
        public void setImmersiveMode(final boolean enabled) {
            runOnUiThread(() -> {
                if (enabled) {
                    setupImmersiveFullscreen();
                } else {
                    try {
                        WindowInsetsControllerCompat controller =
                                WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
                        if (controller != null) {
                            controller.show(WindowInsetsCompat.Type.systemBars());
                        }
                    } catch (Throwable ignored) {}
                }
            });
        }

        /**
         * Returns comprehensive native container & hardware capabilities JSON.
         */
        @JavascriptInterface
        public String getDeviceInfo() {
            try {
                JSONObject info = new JSONObject();
                info.put("platform", "android");
                info.put("version", getAppVersion());
                info.put("build", getBuildNumber());
                info.put("otaBuild", getOtaBuild());
                info.put("refreshRate", (double) activeRefreshRate);
                info.put("sdkInt", Build.VERSION.SDK_INT);
                info.put("model", Build.MODEL);
                info.put("manufacturer", Build.MANUFACTURER);
                info.put("keepScreenOn", keepScreenOnEnabled);
                info.put("liveWallpaperSupported", true);
                return info.toString();
            } catch (Exception e) {
                return "{\"platform\":\"android\",\"version\":\"2.0.0.0\",\"build\":200,\"refreshRate\":120}";
            }
        }

        @JavascriptInterface
        public String getDeviceStatusJson() {
            return getDeviceInfo();
        }

        /**
         * Launches the Android system Live Wallpaper preview/picker targeting StarfieldWallpaperService.
         */
        @JavascriptInterface
        public boolean openLiveWallpaperPicker() {
            try {
                Intent intent = new Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER);
                intent.putExtra(
                    WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT,
                    new ComponentName(MainActivity.this, StarfieldWallpaperService.class)
                );
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return true;
            } catch (Throwable t1) {
                try {
                    Intent fallback = new Intent(WallpaperManager.ACTION_LIVE_WALLPAPER_CHOOSER);
                    fallback.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(fallback);
                    return true;
                } catch (Throwable t2) {
                    Log.w(TAG, "Unable to launch Live Wallpaper picker", t2);
                    return false;
                }
            }
        }

        @JavascriptInterface
        public void setOrientation(String mode) {
            runOnUiThread(() -> {
                if ("landscape".equalsIgnoreCase(mode)) {
                    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);
                } else if ("portrait".equalsIgnoreCase(mode)) {
                    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
                } else {
                    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
                }
            });
        }

        @JavascriptInterface
        public boolean saveImageToGallery(String base64Data, String filename) {
            try {
                if (base64Data == null || base64Data.isEmpty()) return false;
                if (base64Data.contains(",")) {
                    base64Data = base64Data.substring(base64Data.indexOf(",") + 1);
                }
                byte[] decodedBytes = Base64.decode(base64Data, Base64.DEFAULT);
                if (filename == null || filename.isEmpty()) {
                    filename = "Starfield_Voyage_" + System.currentTimeMillis() + ".png";
                }
                if (!filename.endsWith(".png") && !filename.endsWith(".jpg")) {
                    filename += ".png";
                }

                ContentValues values = new ContentValues();
                values.put(MediaStore.Images.Media.DISPLAY_NAME, filename);
                values.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    values.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/Starfield");
                    values.put(MediaStore.Images.Media.IS_PENDING, 1);
                }

                Uri uri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);
                if (uri != null) {
                    try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                        if (out != null) {
                            out.write(decodedBytes);
                            out.flush();
                        }
                    }
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        values.clear();
                        values.put(MediaStore.Images.Media.IS_PENDING, 0);
                        getContentResolver().update(uri, values, null, null);
                    }
                    return true;
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to save image to gallery", e);
            }
            return false;
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            requestHighRefreshRateDisplay();
            setupImmersiveFullscreen();
        }
    }

    @Override
    public void onBackPressed() {
        if (webView == null) { super.onBackPressed(); return; }
        webView.evaluateJavascript("(window.__sfBack && window.__sfBack())?'1':'0'", value -> {
            if ("\"1\"".equals(value)) {
                performNativeHaptic("tick");
                return;
            }
            long now = SystemClock.uptimeMillis();
            if (now - lastBack < 2000) { finish(); return; }
            lastBack = now;
            performNativeHaptic("light");
            webView.evaluateJavascript(
                "if(window.toast)toast('再按一次退出 · PRESS BACK AGAIN', 1.6)", null);
        });
    }

    @Override
    protected void onPause() {
        dispatchJsLifecycle("pause", true);
        if (webView != null) {
            webView.onPause();
            webView.pauseTimers();
        }
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        requestHighRefreshRateDisplay();
        setupImmersiveFullscreen();
        if (webView != null) {
            webView.onResume();
            webView.resumeTimers();
        }
        dispatchJsLifecycle("resume", false);
    }

    @Override
    public void onTrimMemory(int level) {
        super.onTrimMemory(level);
        if (webView != null && level >= TRIM_MEMORY_RUNNING_LOW) {
            dispatchJsLifecycle("memory_pressure", false);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        otaExecutor.shutdown();
        if (webView != null) {
            webView.onPause();
            if (webView.getParent() instanceof ViewGroup) {
                ((ViewGroup) webView.getParent()).removeView(webView);
            }
            webView.destroy();
            webView = null;
        }
    }
}
