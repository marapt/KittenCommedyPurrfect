"""
Create a test video file for debugging download functionality
"""
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
import os

def create_test_video(output_path: str):
    """Create a simple test video"""
    try:
        # Create a purple background clip (5 seconds)
        background = ColorClip(size=(1280, 720), color=(128, 0, 128), duration=5)
        
        # Create text clip
        text = TextClip(
            "Kitten Comedy Purrfect\nTest Video\n\n🐱",
            fontsize=70,
            color='white',
            size=(1280, 720),
            method='caption'
        )
        text = text.set_duration(5).set_position('center')
        
        # Composite the clips
        video = CompositeVideoClip([background, text])
        
        # Write the video file
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio=False,
            logger=None
        )
        
        print(f"✅ Test video created: {output_path}")
        
    except Exception as e:
        print(f"❌ Error creating test video: {str(e)}")
        # Create a minimal valid MP4 if the above fails
        print("Trying minimal video creation...")
        background = ColorClip(size=(640, 480), color=(128, 0, 128), duration=3)
        background.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio=False,
            logger=None
        )

if __name__ == "__main__":
    output_dir = "/app/backend/generated_videos"
    os.makedirs(output_dir, exist_ok=True)
    create_test_video(os.path.join(output_dir, "test_sample.mp4"))
