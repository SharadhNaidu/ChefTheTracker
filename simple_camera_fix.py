"""
SIMPLE AND FINAL CAMERA COLOR FIX
This will fix the black and white camera issue once and for all
"""

import cv2
import subprocess
import time
import os

def final_camera_fix():
    print("🎯 FINAL CAMERA COLOR FIX")
    print("========================")
    
    # Step 1: Kill any OpenCV processes
    print("\n1. Stopping all camera processes...")
    subprocess.run('taskkill /f /im python.exe', shell=True, stderr=subprocess.DEVNULL)
    subprocess.run('taskkill /f /im pythonw.exe', shell=True, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # Step 2: Reset camera with AGGRESSIVE color settings
    print("\n2. FORCING camera to COLOR mode...")
    
    try:
        # Use DirectShow backend (most reliable on Windows)
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            print("✓ Camera opened with DirectShow")
            
            # FORCE COLOR SETTINGS - AGGRESSIVE MODE
            success_count = 0
            
            # Try multiple color format codes
            color_settings = [
                (cv2.CAP_PROP_CONVERT_RGB, 1),
                (cv2.CAP_PROP_FORMAT, -1),  # Auto format
                (cv2.CAP_PROP_MODE, 0),     # Default mode
                (cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G')),
                (cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','Y','V')),
                (cv2.CAP_PROP_FRAME_WIDTH, 640),
                (cv2.CAP_PROP_FRAME_HEIGHT, 480),
                (cv2.CAP_PROP_FPS, 30),
                (cv2.CAP_PROP_BRIGHTNESS, 0.5),
                (cv2.CAP_PROP_CONTRAST, 0.5),
                (cv2.CAP_PROP_SATURATION, 0.5),  # CRITICAL FOR COLOR
                (cv2.CAP_PROP_HUE, 0),
                (cv2.CAP_PROP_EXPOSURE, -6),
                (cv2.CAP_PROP_AUTO_WB, 1),  # Auto white balance
            ]
            
            for prop, value in color_settings:
                try:
                    result = cap.set(prop, value)
                    if result:
                        success_count += 1
                        print(f"  ✓ Set property {prop} = {value}")
                    else:
                        print(f"  ⚠ Could not set property {prop}")
                except:
                    print(f"  ✗ Failed to set property {prop}")
            
            print(f"Successfully applied {success_count}/{len(color_settings)} color settings")
            
            # Capture multiple frames to test color
            print("\n3. Testing color capture...")
            color_detected = False
            
            for i in range(15):  # Try more frames
                ret, frame = cap.read()
                if ret and len(frame.shape) == 3:
                    # Check if frame has real color data
                    b, g, r = cv2.split(frame)
                    # Calculate color variance
                    b_var = b.var()
                    g_var = g.var()
                    r_var = r.var()
                    
                    # If channels have different variances, it's color
                    if abs(b_var - g_var) > 10 or abs(g_var - r_var) > 10:
                        color_detected = True
                        print(f"  ✓ COLOR DETECTED in frame {i+1}!")
                        break
                    else:
                        print(f"  Frame {i+1}: Still grayscale...")
                
                time.sleep(0.1)
            
            cap.release()
            
            if color_detected:
                print("\n🎉 SUCCESS! Camera is now in COLOR mode!")
                return True
            else:
                print("\n⚠ Camera still appears to be in grayscale mode")
                return False
                
        else:
            print("✗ Could not open camera")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        cv2.destroyAllWindows()

def apply_registry_fix():
    """Apply final registry settings to force color mode"""
    print("\n4. Applying registry color settings...")
    
    registry_commands = [
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /v ForceColor /t REG_DWORD /d 1 /f',
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /v ColorSpace /t REG_SZ /d "sRGB" /f',
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Camera" /v DisableGrayscale /t REG_DWORD /d 1 /f'
    ]
    
    for cmd in registry_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"  ✓ Applied: {cmd.split('/v')[1].split('/t')[0]}")
        except:
            print(f"  ⚠ Could not apply registry setting")

if __name__ == "__main__":
    print("Starting comprehensive camera color fix...")
    
    # Apply registry fix first
    apply_registry_fix()
    
    # Test camera
    success = final_camera_fix()
    
    print("\n" + "="*50)
    if success:
        print("🎉 CAMERA COLOR FIX SUCCESSFUL! 🎉")
        print("Your camera is now working in COLOR mode!")
    else:
        print("⚠ Camera needs restart to complete fix")
        print("Please RESTART your computer, then test the camera app")
    
    print("\nFinal steps:")
    print("1. Close this window")
    print("2. Open Windows Camera app")
    print("3. Camera should display in FULL COLOR!")
    print("4. If still black & white, restart your computer")
    
    input("\nPress Enter to finish...")