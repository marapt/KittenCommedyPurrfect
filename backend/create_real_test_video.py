#!/usr/bin/env python3
"""
Create a REAL playable test video with actual frames
"""
import subprocess
import os
from imageio_ffmpeg import get_ffmpeg_exe

def create_proper_test_video():
    """Create a proper 10-second video with actual content"""
    try:
        ffmpeg = get_ffmpeg_exe()
        output_path = "/app/backend/generated_videos/test_sample.mp4"
        
        # Create a 10-second video with:
        # - Solid purple background
        # - 30 FPS for smooth playback
        # - Proper bitrate for quality
        # - H.264 codec with baseline profile for maximum compatibility
        cmd = [
            ffmpeg,
            '-f', 'lavfi',
            '-i', 'color=c=purple:s=1280x720:d=10:r=30',  # 10 seconds, 30 FPS
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',  # Quality setting
            '-pix_fmt', 'yuv420p',  # Required for QuickTime compatibility
            '-profile:v', 'baseline',  # Maximum compatibility
            '-level', '3.0',
            '-movflags', '+faststart',  # Web optimization
            '-y',
            output_path
        ]
        
        print("Creating proper test video...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            size = os.path.getsize(output_path)
            print(f"✅ Created proper test video!")
            print(f"   Path: {output_path}")
            print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
            
            # Verify it's a proper video
            probe_cmd = [
                ffmpeg.replace('ffmpeg', 'ffprobe'),
                '-v', 'error',
                '-show_entries', 'format=duration,size:stream=codec_name,width,height,r_frame_rate',
                '-of', 'default=noprint_wrappers=1',
                output_path
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            print(f"\n   Video info:\n{probe_result.stdout}")
            
            if size < 50000:  # Less than 50KB is suspicious
                print(f"⚠️  WARNING: File size is very small ({size} bytes)")
                return False
            
            return True
        else:
            print(f"❌ FFmpeg failed!")
            print(f"Error: {result.stderr[-500:]}")  # Last 500 chars
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_proper_test_video()
    exit(0 if success else 1)
