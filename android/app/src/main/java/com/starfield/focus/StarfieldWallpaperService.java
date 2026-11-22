package com.starfield.focus;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.os.Build;
import android.os.SystemClock;
import android.service.wallpaper.WallpaperService;
import android.view.Choreographer;
import android.view.MotionEvent;
import android.view.SurfaceHolder;

import java.util.Random;

/**
 * Native 120Hz VSync-paced Deep Space & Origami Flagship Live Wallpaper Service.
 * Designed with zero per-frame object allocations (Zero-GC hot loop) and
 * hardware-accelerated surface canvas locking on Android 8.0+ (API 26+).
 */
public class StarfieldWallpaperService extends WallpaperService {

    @Override
    public Engine onCreateEngine() {
        return new StarfieldWallpaperEngine();
    }

    private class StarfieldWallpaperEngine extends Engine implements Choreographer.FrameCallback {
        private static final int STAR_COUNT = 220;

        private final float[] starX = new float[STAR_COUNT];
        private final float[] starY = new float[STAR_COUNT];
        private final float[] starZ = new float[STAR_COUNT];
        private final float[] starSize = new float[STAR_COUNT];
        private final int[] starColor = new int[STAR_COUNT];

        private final Paint bgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint nebulaPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint starPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint craftPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint rimPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint trailPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

        private final Path craftLeftWing = new Path();
        private final Path craftRightWing = new Path();
        private final Path craftKeel = new Path();
        private final Path trailPath = new Path();

        private int width = 1080;
        private int height = 2400;
        private boolean visible = false;
        private long lastFrameNanos = 0L;
        private float smoothedDt = 1f / 120f;
        private float parallaxX = 0f;
        private float parallaxY = 0f;
        private float targetParallaxX = 0f;
        private float targetParallaxY = 0f;
        private float warpPulse = 0f;

        StarfieldWallpaperEngine() {
            initStars();
            rimPaint.setStyle(Paint.Style.STROKE);
            rimPaint.setStrokeWidth(1.6f);
            rimPaint.setColor(0xCC7DD3FC);
            setTouchEventsEnabled(true);
        }

        private void initStars() {
            Random rng = new Random(0x5F3759DFL);
            int[] palette = new int[]{
                0xFFE2E8F0, // Ice white
                0xFFbae6fd, // Starlight cyan
                0xFFfef08a, // Solar gold
                0xFFc7d2fe, // Deep indigo white
                0xFF93c5fd  // Crisp blue
            };
            for (int i = 0; i < STAR_COUNT; i++) {
                starX[i] = (rng.nextFloat() - 0.5f) * 2.2f;
                starY[i] = (rng.nextFloat() - 0.5f) * 2.2f;
                starZ[i] = 0.08f + rng.nextFloat() * 0.92f;
                starSize[i] = 1.1f + rng.nextFloat() * 2.4f;
                starColor[i] = palette[i % palette.length];
            }
        }

        private void rebuildShaders() {
            if (width <= 0 || height <= 0) return;
            bgPaint.setShader(new LinearGradient(
                0f, 0f, 0f, height,
                new int[]{0xFF04070C, 0xFF08101C, 0xFF0B1626, 0xFF05080F},
                new float[]{0f, 0.42f, 0.78f, 1f},
                Shader.TileMode.CLAMP
            ));
            nebulaPaint.setShader(new RadialGradient(
                width * 0.52f, height * 0.42f,
                Math.max(width, height) * 0.55f,
                new int[]{0x2838BDF8, 0x14818CF8, 0x00060A10},
                new float[]{0f, 0.52f, 1f},
                Shader.TileMode.CLAMP
            ));
        }

        @Override
        public void onSurfaceChanged(SurfaceHolder holder, int format, int width, int height) {
            super.onSurfaceChanged(holder, format, width, height);
            this.width = Math.max(1, width);
            this.height = Math.max(1, height);
            rebuildShaders();
            drawFrame(SystemClock.elapsedRealtimeNanos());
        }

        @Override
        public void onVisibilityChanged(boolean visible) {
            super.onVisibilityChanged(visible);
            this.visible = visible;
            Choreographer.getInstance().removeFrameCallback(this);
            if (visible) {
                lastFrameNanos = SystemClock.elapsedRealtimeNanos();
                Choreographer.getInstance().postFrameCallback(this);
            }
        }

        @Override
        public void onSurfaceDestroyed(SurfaceHolder holder) {
            super.onSurfaceDestroyed(holder);
            this.visible = false;
            Choreographer.getInstance().removeFrameCallback(this);
        }

        @Override
        public void onOffsetsChanged(float xOffset, float yOffset, float xOffsetStep, float yOffsetStep, int xPixelOffset, int yPixelOffset) {
            targetParallaxX = (xOffset - 0.5f) * 0.35f;
            targetParallaxY = (yOffset - 0.5f) * 0.20f;
        }

        @Override
        public void onTouchEvent(MotionEvent event) {
            super.onTouchEvent(event);
            if (event == null || width <= 0 || height <= 0) return;
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_MOVE) {
                targetParallaxX = ((event.getX() / width) - 0.5f) * 0.42f;
                targetParallaxY = ((event.getY() / height) - 0.5f) * 0.32f;
                if (action == MotionEvent.ACTION_DOWN) {
                    warpPulse = Math.min(1.0f, warpPulse + 0.55f);
                }
            }
        }

        @Override
        public void doFrame(long frameTimeNanos) {
            if (!visible) return;
            drawFrame(frameTimeNanos);
            if (visible) {
                Choreographer.getInstance().postFrameCallback(this);
            }
        }

        private void drawFrame(long frameTimeNanos) {
            SurfaceHolder holder = getSurfaceHolder();
            if (holder == null) return;

            float rawDt = (lastFrameNanos > 0L)
                    ? (frameTimeNanos - lastFrameNanos) * 1e-9f
                    : (1f / 120f);
            lastFrameNanos = frameTimeNanos;
            if (rawDt <= 0f || rawDt > 0.1f) rawDt = 1f / 120f;
            // EMA frame-delta smoothing to prevent jitter on variable refresh rate panels
            smoothedDt = smoothedDt * 0.85f + rawDt * 0.15f;

            parallaxX += (targetParallaxX - parallaxX) * Math.min(1f, smoothedDt * 6.5f);
            parallaxY += (targetParallaxY - parallaxY) * Math.min(1f, smoothedDt * 6.5f);
            warpPulse = Math.max(0f, warpPulse - smoothedDt * 0.65f);

            Canvas canvas = null;
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    canvas = holder.lockHardwareCanvas();
                } else {
                    canvas = holder.lockCanvas();
                }
                if (canvas != null) {
                    renderScene(canvas, frameTimeNanos * 1e-9f, smoothedDt);
                }
            } catch (Throwable ignored) {
            } finally {
                if (canvas != null) {
                    try {
                        holder.unlockCanvasAndPost(canvas);
                    } catch (Throwable ignored) {}
                }
            }
        }

        private void renderScene(Canvas canvas, float timeSec, float dt) {
            final float w = width;
            final float h = height;
            final float cx = w * (0.5f - parallaxX * 0.35f);
            final float cy = h * (0.44f - parallaxY * 0.35f);
            final float scale = Math.max(w, h) * 0.62f;

            // 1. Deep space gradient backdrop & subtle nebula radiance
            canvas.drawRect(0f, 0f, w, h, bgPaint);
            canvas.drawRect(0f, 0f, w, h, nebulaPaint);

            // 2. 3D Projected Starfield with Warp Streak support
            final float speed = (0.14f + warpPulse * 0.55f) * dt;
            for (int i = 0; i < STAR_COUNT; i++) {
                float z = starZ[i] - speed;
                if (z <= 0.05f) {
                    z += 0.95f;
                }
                starZ[i] = z;

                float invZ = 1.0f / z;
                float sx = cx + (starX[i] - parallaxX * 0.4f) * invZ * scale;
                float sy = cy + (starY[i] - parallaxY * 0.4f) * invZ * scale;

                if (sx < -32f || sx > w + 32f || sy < -32f || sy > h + 32f) {
                    continue;
                }

                float depthAlpha = Math.min(1f, Math.max(0.15f, (1.05f - z) * 1.15f));
                float twinkle = 0.78f + 0.22f * (float) Math.sin(timeSec * 2.6f + i * 1.7f);
                int alpha = Math.min(255, Math.max(24, (int) (depthAlpha * twinkle * 245f)));
                int baseColor = starColor[i];
                starPaint.setColor((baseColor & 0x00FFFFFF) | (alpha << 24));

                float radius = starSize[i] * Math.min(2.6f, invZ * 0.45f);
                if (warpPulse > 0.05f) {
                    float prevInvZ = 1.0f / (z + speed * (2.4f + warpPulse * 5.0f));
                    float px = cx + (starX[i] - parallaxX * 0.4f) * prevInvZ * scale;
                    float py = cy + (starY[i] - parallaxY * 0.4f) * prevInvZ * scale;
                    starPaint.setStrokeWidth(Math.max(1.2f, radius * 0.9f));
                    canvas.drawLine(px, py, sx, sy, starPaint);
                } else {
                    canvas.drawCircle(sx, sy, radius, starPaint);
                }
            }

            // 3. Origami Flagship Silhouette & Ion Ribbon Trail
            float shipX = w * 0.5f + parallaxX * w * 0.22f + (float) Math.sin(timeSec * 0.95f) * 14f;
            float shipY = h * 0.68f + parallaxY * h * 0.12f + (float) Math.cos(timeSec * 1.25f) * 9f;
            float bank = parallaxX * -18f + (float) Math.cos(timeSec * 0.95f) * 4.5f;
            float unit = Math.min(w, h) * 0.052f;

            canvas.save();
            canvas.translate(shipX, shipY);
            canvas.rotate(bank);

            // Engine ion trail
            float trailLen = unit * (2.6f + warpPulse * 2.4f + 0.25f * (float) Math.sin(timeSec * 7.0f));
            trailPath.reset();
            trailPath.moveTo(-unit * 0.16f, unit * 0.35f);
            trailPath.lineTo(0f, unit * 0.35f + trailLen);
            trailPath.lineTo(unit * 0.16f, unit * 0.35f);
            trailPath.close();
            trailPaint.setColor(0x6638BDF8);
            canvas.drawPath(trailPath, trailPaint);

            // Left origami wing facet
            craftLeftWing.reset();
            craftLeftWing.moveTo(0f, -unit * 0.95f);
            craftLeftWing.lineTo(-unit * 1.05f, unit * 0.48f);
            craftLeftWing.lineTo(-unit * 0.18f, unit * 0.26f);
            craftLeftWing.close();
            craftPaint.setColor(0xFFE2E8F0);
            canvas.drawPath(craftLeftWing, craftPaint);
            canvas.drawPath(craftLeftWing, rimPaint);

            // Right origami wing facet
            craftRightWing.reset();
            craftRightWing.moveTo(0f, -unit * 0.95f);
            craftRightWing.lineTo(unit * 1.05f, unit * 0.48f);
            craftRightWing.lineTo(unit * 0.18f, unit * 0.26f);
            craftRightWing.close();
            craftPaint.setColor(0xFF94A3B8);
            canvas.drawPath(craftRightWing, craftPaint);
            canvas.drawPath(craftRightWing, rimPaint);

            // Center origami keel facet
            craftKeel.reset();
            craftKeel.moveTo(0f, -unit * 0.95f);
            craftKeel.lineTo(-unit * 0.18f, unit * 0.26f);
            craftKeel.lineTo(0f, unit * 0.56f);
            craftKeel.lineTo(unit * 0.18f, unit * 0.26f);
            craftKeel.close();
            craftPaint.setColor(0xFFCBD5E1);
            canvas.drawPath(craftKeel, craftPaint);
            canvas.drawPath(craftKeel, rimPaint);

            canvas.restore();
        }
    }
}
