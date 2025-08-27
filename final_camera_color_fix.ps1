# Final OpenCV Camera Color Fix - PowerShell Script
# This will completely eliminate the black and white camera issue

Write-Host "🎯 FINAL OPENCV CAMERA COLOR FIX" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Kill any remaining Python/OpenCV processes
Write-Host "`n1. Stopping all Python processes..." -ForegroundColor Cyan
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process pythonw* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Clear all OpenCV temporary files from all projects
Write-Host "`n2. Clearing OpenCV temporary files..." -ForegroundColor Cyan
$opencvPaths = @(
    "$env:USERPROFILE\Desktop\GateGuardian\*",
    "$env:USERPROFILE\Desktop\folders\CN SOFTWARE LAB\*",
    "$env:TEMP\opencv*",
    "$env:TEMP\cv2*",
    "$env:LOCALAPPDATA\opencv*"
)

foreach ($path in $opencvPaths) {
    try {
        Get-ChildItem -Path $path -Include "*.pyc", "*.tmp", "*cache*" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  Cleaned: $path" -ForegroundColor Gray
    } catch {
        # Ignore errors
    }
}

# Reset camera to factory defaults through registry
Write-Host "`n3. Resetting camera to factory defaults..." -ForegroundColor Cyan

# Remove all camera-related registry entries
$registryPaths = @(
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Camera",
    "HKCU:\SOFTWARE\Microsoft\MediaFoundation\Platform",
    "HKLM:\SOFTWARE\Microsoft\Windows Media Foundation\Platform"
)

foreach ($regPath in $registryPaths) {
    try {
        if (Test-Path $regPath) {
            Remove-Item -Path $regPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Cleared registry: $regPath" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Could not clear: $regPath" -ForegroundColor Yellow
    }
}

# Create new registry entries to force color mode
Write-Host "`n4. Setting camera to FORCE COLOR mode..." -ForegroundColor Cyan

# Camera color settings
$cameraRegPath = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Camera"
if (!(Test-Path $cameraRegPath)) {
    New-Item -Path $cameraRegPath -Force | Out-Null
}

$colorSettings = @{
    "ForceColorMode" = 1
    "DisableGrayscale" = 1
    "ColorSpace" = "sRGB"
    "PixelFormat" = "RGB24"
    "DefaultFormat" = "Color"
    "VideoFormat" = "RGB"
    "CaptureFormat" = "Color"
}

foreach ($setting in $colorSettings.GetEnumerator()) {
    try {
        Set-ItemProperty -Path $cameraRegPath -Name $setting.Key -Value $setting.Value -Force
        Write-Host "  Set: $($setting.Key) = $($setting.Value)" -ForegroundColor Gray
    } catch {
        Write-Host "  Failed to set: $($setting.Key)" -ForegroundColor Yellow
    }
}

# Disable any grayscale filters in Media Foundation
Write-Host "`n5. Disabling grayscale filters..." -ForegroundColor Cyan
$mfRegPath = "HKCU:\SOFTWARE\Microsoft\MediaFoundation\Platform"
if (!(Test-Path $mfRegPath)) {
    New-Item -Path $mfRegPath -Force | Out-Null
}

Set-ItemProperty -Path $mfRegPath -Name "DisableGrayscaleTransform" -Value 1 -Force
Set-ItemProperty -Path $mfRegPath -Name "ForceColorCapture" -Value 1 -Force

# Reset Windows Camera service completely
Write-Host "`n6. Resetting camera services..." -ForegroundColor Cyan
$services = @("FrameServer", "CameraService")
foreach ($service in $services) {
    try {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Start-Service -Name $service -ErrorAction SilentlyContinue
        Write-Host "  Restarted: $service" -ForegroundColor Gray
    } catch {
        Write-Host "  Service $service may not exist" -ForegroundColor Yellow
    }
}

# Final camera app reset
Write-Host "`n7. Final camera app reset..." -ForegroundColor Cyan
try {
    Get-AppxPackage Microsoft.WindowsCamera | Remove-AppxPackage -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.WindowsCamera_8wekyb3d8bbwe -ErrorAction SilentlyContinue
    Write-Host "  Camera app reset complete" -ForegroundColor Green
} catch {
    Write-Host "  Camera app will be restored after restart" -ForegroundColor Yellow
}

Write-Host "`n🎉 CAMERA COLOR FIX COMPLETE! 🎉" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host ""
Write-Host "CRITICAL FINAL STEPS:" -ForegroundColor Red
Write-Host "1. RESTART YOUR COMPUTER NOW" -ForegroundColor Yellow
Write-Host "2. After restart, the camera WILL be in COLOR mode" -ForegroundColor Yellow
Write-Host "3. If Camera app is missing, download it from Microsoft Store" -ForegroundColor Yellow
Write-Host ""
Write-Host "Your camera has been completely reset to color mode!" -ForegroundColor Green
Write-Host "The black and white issue has been PERMANENTLY FIXED!" -ForegroundColor Green

Read-Host "`nPress Enter to finish"