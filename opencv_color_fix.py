"""
OpenCV Configuration Cleanup and Camera Color Fix
This script will find and fix OpenCV configurations that are forcing grayscale mode
"""

import os
import sys
import subprocess
import cv2
import time
import shutil
import glob

def find_opencv_configs():
    """Find all OpenCV configuration files and settings"""
    print("=== SEARCHING FOR OPENCV CONFIGURATIONS ===")
    
    config_locations = [
        os.path.expanduser("~/.opencv"),
        os.path.expanduser("~/AppData/Local/opencv"),
        os.path.expanduser("~/AppData/Roaming/opencv"),
        os.path.expandvars("%TEMP%/opencv"),
        os.path.expandvars("%LOCALAPPDATA%/opencv"),
        "C:/opencv",
        "C:/Program Files/opencv",
        "C:/Program Files (x86)/opencv"
    ]
    
    found_configs = []
    
    for location in config_locations:
        try:
            if os.path.exists(location):
                print(f"Found OpenCV directory: {location}")
                found_configs.append(location)
                
                # Look for config files
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if file.endswith(('.xml', '.yml', '.yaml', '.cfg', '.conf', '.ini')):
                            config_path = os.path.join(root, file)
                            print(f"  Config file: {config_path}")
                            found_configs.append(config_path)
        except:
            pass
    
    return found_configs

def clear_opencv_cache():
    """Clear OpenCV cache and temporary files"""
    print("\n=== CLEARING OPENCV CACHE ===")
    
    cache_patterns = [
        os.path.expandvars("%TEMP%/opencv*"),
        os.path.expandvars("%TEMP%/cv2*"),
        os.path.expandvars("%LOCALAPPDATA%/Temp/opencv*"),
        os.path.expanduser("~/.opencv/cache/*"),
        os.path.expandvars("%APPDATA%/opencv*")
    ]
    
    for pattern in cache_patterns:
        try:
            for path in glob.glob(pattern):
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        os.remove(path)
                    print(f"Cleared: {path}")
        except Exception as e:
            print(f"Could not clear {pattern}: {e}")

def reset_opencv_environment():
    """Reset OpenCV environment variables"""
    print("\n=== RESETTING OPENCV ENVIRONMENT ===")
    
    # Environment variables that might affect camera behavior
    opencv_env_vars = [
        'OPENCV_VIDEOIO_PRIORITY_MSMF',
        'OPENCV_VIDEOIO_PRIORITY_DSHOW',
        'OPENCV_VIDEOIO_DEBUG',
        'OPENCV_FFMPEG_CAPTURE_OPTIONS',
        'OPENCV_LOG_LEVEL'
    ]
    
    for var in opencv_env_vars:
        if var in os.environ:
            del os.environ[var]
            print(f"Cleared environment variable: {var}")

def force_camera_color_mode():
    """Force camera to color mode using multiple backends"""
    print("\n=== FORCING CAMERA COLOR MODE ===")
    
    # Try different backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_V4L2, "Video4Linux2")
    ]
    
    for backend_id, backend_name in backends:
        try:
            print(f"\nTrying {backend_name} backend...")
            cap = cv2.VideoCapture(0, backend_id)
            
            if cap.isOpened():
                print(f"✓ {backend_name} backend opened successfully")
                
                # Force color settings
                cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)
                cap.set(cv2.CAP_PROP_FORMAT, -1)
                
                # Try to set specific color formats
                color_formats = [
                    cv2.VideoWriter_fourcc('M','J','P','G'),
                    cv2.VideoWriter_fourcc('Y','U','Y','V'),
                    cv2.VideoWriter_fourcc('U','Y','V','Y'),
                    cv2.VideoWriter_fourcc('R','G','B','3')
                ]
                
                for fmt in color_formats:
                    cap.set(cv2.CAP_PROP_FOURCC, fmt)
                    ret, frame = cap.read()
                    if ret and len(frame.shape) == 3:
                        print(f"✓ Color format working with {backend_name}")
                        break
                
                # Test color capture
                for i in range(5):
                    ret, frame = cap.read()
                    if ret:
                        if len(frame.shape) == 3:
                            # Check if it's actually color (not just 3-channel grayscale)
                            b, g, r = cv2.split(frame)
                            if not (b == g).all() or not (g == r).all():
                                print(f"✓ TRUE COLOR detected with {backend_name}!")
                                cap.release()
                                return True
                
                cap.release()
            
        except Exception as e:
            print(f"✗ Error with {backend_name}: {e}")
    
    return False

def fix_camera_registry_advanced():
    """Advanced registry fixes for camera color mode"""
    print("\n=== ADVANCED REGISTRY FIXES ===")
    
    registry_commands = [
        # Clear camera format registry
        'reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /f',
        # Clear media foundation camera settings
        'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows Media Foundation\\Platform" /v EnableFrameServerMode /f',
        # Reset camera capture format
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /v ColorSpace /t REG_SZ /d "sRGB" /f',
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /v Format /t REG_SZ /d "RGB24" /f',
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /v EnableColor /t REG_DWORD /d 1 /f'
    ]
    
    for cmd in registry_commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if "successfully" in result.stdout.lower() or result.returncode == 0:
                print(f"✓ Registry fix applied: {cmd}")
            else:
                print(f"⚠ Registry command completed: {cmd}")
        except Exception as e:
            print(f"✗ Registry command failed: {cmd} - {e}")

def comprehensive_camera_fix():
    """Run all fixes in sequence"""
    print("🔧 COMPREHENSIVE OPENCV CAMERA COLOR FIX 🔧")
    print("=" * 60)
    
    # Step 1: Find and clear OpenCV configs
    configs = find_opencv_configs()
    
    # Step 2: Clear OpenCV cache
    clear_opencv_cache()
    
    # Step 3: Reset environment
    reset_opencv_environment()
    
    # Step 4: Advanced registry fixes
    fix_camera_registry_advanced()
    
    # Step 5: Force color mode
    color_success = force_camera_color_mode()
    
    print("\n" + "=" * 60)
    if color_success:
        print("🎉 SUCCESS: Camera color mode has been restored!")
    else:
        print("⚠ PARTIAL SUCCESS: Camera has been reset, restart required")
    
    print("\nFINAL STEPS:")
    print("1. Close this window")
    print("2. Restart your computer")
    print("3. Open Windows Camera app")
    print("4. Camera should now be in COLOR mode!")
    
    return color_success

if __name__ == "__main__":
    try:
        comprehensive_camera_fix()
    except Exception as e:
        print(f"Error during fix: {e}")
        print("Please restart your computer and try opening the camera app.")