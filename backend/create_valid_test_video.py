#!/usr/bin/env python3
"""
Create a proper valid MP4 test video
"""
import subprocess
import os

def create_test_video_with_ffmpeg():
    """Create a simple test video using ffmpeg via imageio-ffmpeg"""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        
        ffmpeg = get_ffmpeg_exe()
        output_path = "/app/backend/generated_videos/test_sample.mp4"
        
        # Create a 5-second video with purple background and text
        cmd = [
            ffmpeg,
            '-f', 'lavfi',
            '-i', 'color=c=purple:s=1280x720:d=5',
            '-f', 'lavfi', 
            '-i', 'color=c=black:s=1280x720:d=5',
            '-filter_complex',
            "[0:v][1:v]blend=all_mode='overlay':all_opacity=0.5,drawtext=text='Kitten Comedy Purrfect\\nTest Video\\n🐱':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-t', '5',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created valid MP4: {output_path}")
            print(f"   Size: {os.path.getsize(output_path)} bytes")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def create_minimal_valid_mp4():
    """Create minimal but playable MP4 as fallback"""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        
        ffmpeg = get_ffmpeg_exe()
        output_path = "/app/backend/generated_videos/test_sample.mp4"
        
        # Simplest possible valid video
        cmd = [
            ffmpeg,
            '-f', 'lavfi',
            '-i', 'color=c=purple:s=640x480:d=3',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            size = os.path.getsize(output_path)
            print(f"✅ Created minimal valid MP4: {output_path}")
            print(f"   Size: {size} bytes")
            return True
        else:
            print(f"❌ Error: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Creating valid test video...")
    
    # Try detailed version first
    if not create_test_video_with_ffmpeg():
        print("\nTrying minimal version...")
        create_minimal_valid_mp4()
