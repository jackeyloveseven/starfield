# ==============================================================================
# STARFIELD FOCUS // ANDROID APK BUILD & PACKAGING HELPER
# ==============================================================================

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$AndroidDir = Join-Path $ProjectRoot "android"
$AssetsDir = Join-Path $AndroidDir "app\src\main\assets"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " STARFIELD FOCUS // PACKAGING ANDROID APK & WEB ASSETS" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Sync web app files to Android assets directory
Write-Host "`n1. Synchronizing web assets into Android project..." -ForegroundColor Yellow
if (-not (Test-Path $AssetsDir)) {
    New-Item -ItemType Directory -Path $AssetsDir -Force | Out-Null
}

Copy-Item (Join-Path $ProjectRoot "starfield.html") (Join-Path $AssetsDir "starfield.html") -Force
Copy-Item (Join-Path $ProjectRoot "manifest.json") (Join-Path $AssetsDir "manifest.json") -Force
Copy-Item (Join-Path $ProjectRoot "service-worker.js") (Join-Path $AssetsDir "service-worker.js") -Force

Write-Host "   >>> Assets synchronized: starfield.html, manifest.json, service-worker.js" -ForegroundColor Green

# 2. Check for Android SDK / Gradle
Write-Host "`n2. Checking build environment..." -ForegroundColor Yellow
$GradleCmd = Get-Command "gradle" -ErrorAction SilentlyContinue
$HasAndroidStudio = Test-Path "C:\Program Files\Android\Android Studio"

if ($GradleCmd) {
    Write-Host "   >>> Found local Gradle installation! Executing build..." -ForegroundColor Green
    Push-Location $AndroidDir
    try {
        gradle assembleDebug
        Write-Host "`n   >>> APK Built Successfully!" -ForegroundColor Green
        Write-Host "   Output location: $AndroidDir\app\build\outputs\apk\debug\app-debug.apk" -ForegroundColor Cyan
    } finally {
        Pop-Location
    }
} else {
    Write-Host "   >>> Android Studio / Gradle Command Line:" -ForegroundColor Yellow
    Write-Host "   - The complete native Android project is ready in: $AndroidDir" -ForegroundColor White
    Write-Host "   - You can open the 'android' folder directly in Android Studio, click 'Build' -> 'Build Bundle(s) / APK(s)' -> 'Build APK(s)' to generate the .apk in 1 click!" -ForegroundColor White
    Write-Host "   - Alternatively, install Starfield as a PWA directly from mobile Chrome/Edge via '添加到主屏幕 / Install App'." -ForegroundColor White
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host " PACKAGING PREPARATION COMPLETE!" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
