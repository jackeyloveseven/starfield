package com.starfield.focus;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
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

    private WebView webView;
    private final ExecutorService otaExecutor = Executors.newSingleThreadExecutor();

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

        // Hardware acceleration & 2K WebGL / Canvas rendering performance
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        webView.setBackgroundColor(0xFF0B1118);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient());

        // Expose Native Bridge for JS In-App Hot Updates
        webView.addJavascriptInterface(new StarfieldNativeBridge(), "StarfieldNative");

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
    }

    public void triggerOtaCheck(final boolean isManual) {
        otaExecutor.execute(() -> {
            try {
                SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
                long currentBuild = prefs.getLong(KEY_BUILD, 0L);

                // 1. Fetch remote version descriptor
                URL vUrl = new URL(OTA_VERSION_URL);
                HttpURLConnection conn = (HttpURLConnection) vUrl.openConnection();
                conn.setConnectTimeout(4000);
                conn.setReadTimeout(4000);
                conn.setRequestMethod("GET");
                conn.setUseCaches(false);

                int code = conn.getResponseCode();
                if (code != 200) {
                    if (isManual) notifyJs("OTA_ERROR", "云端检查失败 (HTTP " + code + ")");
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

                if (remoteBuild <= currentBuild && !isManual) {
                    // Up to date
                    return;
                }

                // 2. Download latest starfield.html
                URL htmlUrl = new URL(OTA_HTML_URL);
                HttpURLConnection htmlConn = (HttpURLConnection) htmlUrl.openConnection();
                htmlConn.setConnectTimeout(6000);
                htmlConn.setReadTimeout(12000);
                htmlConn.setRequestMethod("GET");
                htmlConn.setUseCaches(false);

                if (htmlConn.getResponseCode() != 200) {
                    if (isManual) notifyJs("OTA_ERROR", "下载热更新包失败");
                    return;
                }

                File tempFile = new File(getFilesDir(), "starfield_temp.html");
                InputStream in = htmlConn.getInputStream();
                FileOutputStream out = new FileOutputStream(tempFile);

                byte[] buffer = new byte[8192];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    out.write(buffer, 0, read);
                }
                out.flush();
                out.close();
                in.close();

                // 3. Verify download integrity
                if (tempFile.length() < 500000) {
                    tempFile.delete();
                    if (isManual) notifyJs("OTA_ERROR", "更新包校验不完整");
                    return;
                }

                // 4. Atomically commit new active version
                File activeFile = new File(getFilesDir(), "starfield_active.html");
                if (activeFile.exists()) activeFile.delete();
                tempFile.renameTo(activeFile);

                prefs.edit().putLong(KEY_BUILD, remoteBuild).putString(KEY_VERSION, remoteVersion).apply();

                // 5. Notify web app of hot update readiness
                notifyJs("OTA_READY", remoteVersion);

            } catch (Exception e) {
                if (isManual) notifyJs("OTA_ERROR", "网络异常: " + e.getMessage());
            }
        });
    }

    private void notifyJs(final String type, final String payload) {
        runOnUiThread(() -> {
            if (webView != null) {
                String safePayload = payload.replace("'", "\\'");
                webView.evaluateJavascript(
                    "if(typeof window.onStarfieldOtaNotify==='function'){ window.onStarfieldOtaNotify('" + type + "', '" + safePayload + "'); }",
                    null
                );
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
                File active = new File(getFilesDir(), "starfield_active.html");
                if (active.exists() && active.length() > 500000) {
                    webView.loadUrl("file://" + active.getAbsolutePath());
                } else {
                    webView.reload();
                }
            });
        }

        @JavascriptInterface
        public String getAppVersion() {
            SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            return prefs.getString(KEY_VERSION, "1.1.0");
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
