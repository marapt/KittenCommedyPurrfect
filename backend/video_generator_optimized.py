"""
Memory-optimized video generation for preview environment
"""
import os
import asyncio
import re
from pathlib import Path
from typing import List, Dict
import logging
from dotenv import load_dotenv
from PIL import Image

from emergentintegrations.llm.openai import OpenAITextToSpeech
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
from moviepy import (
    ImageClip, AudioFileClip, ColorClip,
    concatenate_videoclips
)

logger = logging.getLogger(__name__)

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class VideoGeneratorOptimized:
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found")
        
        self.tts = OpenAITextToSpeech(api_key=self.api_key)
        self.image_gen = OpenAIImageGeneration(api_key=self.api_key)
        self.output_dir = ROOT_DIR / "generated_videos"
        self.temp_dir = ROOT_DIR / "temp_assets"
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
    
    def parse_script(self, script: str, max_scenes: int = 4) -> List[Dict]:
        """Parse script and limit to max_scenes for memory efficiency"""
        scenes = []
        lines = script.strip().split('\n')
        
        current_scene = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            scene_match = re.match(r'\[SCENE:?\s*([^\]]+)\]', line, re.IGNORECASE)
            if scene_match:
                if current_scene and current_text:
                    scenes.append({
                        "scene": current_scene,
                        "text": ' '.join(current_text)
                    })
                
                current_scene = scene_match.group(1).strip()
                current_text = []
            else:
                current_text.append(line)
        
        if current_scene and current_text:
            scenes.append({
                "scene": current_scene,
                "text": ' '.join(current_text)
            })
        
        if not scenes:
            scenes.append({"scene": "Main scene", "text": script})
        
        # Limit scenes for memory
        if len(scenes) > max_scenes:
            logger.info(f"Limiting from {len(scenes)} to {max_scenes} scenes for memory")
            scenes = scenes[:max_scenes]
        
        return scenes
    
    async def generate_audio(self, text: str, output_path: Path) -> float:
        """Generate TTS audio"""
        try:
            logger.info(f"Generating TTS ({len(text)} chars)...")
            
            audio_bytes = await self.tts.generate_speech(
                text=text,
                model="tts-1",
                voice="nova",
                speed=1.1
            )
            
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            audio_clip = AudioFileClip(str(output_path))
            duration = audio_clip.duration
            audio_clip.close()
            
            logger.info(f"✅ Audio: {duration:.1f}s")
            return duration
            
        except Exception as e:
            logger.error(f"TTS failed: {str(e)}")
            raise
    
    def downscale_image(self, image_path: Path, target_width: int = 720) -> Path:
        """Downscale image to reduce memory usage"""
        try:
            img = Image.open(image_path)
            
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = img.height / img.width
            new_width = target_width
            new_height = int(target_width * aspect_ratio)
            
            # Resize
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save downscaled version
            downscaled_path = image_path.parent / f"{image_path.stem}_small{image_path.suffix}"
            img_resized.save(downscaled_path, optimize=True, quality=85)
            
            img.close()
            img_resized.close()
            
            logger.info(f"Downscaled: {image_path.name} -> {new_width}x{new_height}")
            return downscaled_path
            
        except Exception as e:
            logger.error(f"Downscale failed: {str(e)}")
            return image_path
    
    async def generate_cat_image(self, scene_description: str, output_path: Path) -> bool:
        """Generate and downscale cat image"""
        try:
            prompt = f"Simple cartoon illustration: {scene_description}. Cute cat, vibrant colors, family-friendly."
            
            logger.info(f"🎨 Generating: {scene_description[:40]}...")
            
            images = await self.image_gen.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1
            )
            
            if images and len(images) > 0:
                with open(output_path, "wb") as f:
                    f.write(images[0])
                
                # Immediately downscale to save memory
                downscaled = self.downscale_image(output_path, target_width=720)
                
                # Delete original high-res version
                if downscaled != output_path and output_path.exists():
                    output_path.unlink()
                    downscaled.rename(output_path)
                
                logger.info(f"✅ Image ready")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return False
    
    def create_solid_clip(self, duration: float, color: tuple = (139, 0, 255)) -> ColorClip:
        """Create simple solid color clip for intro/outro"""
        return ColorClip(size=(720, 1280), color=color, duration=duration)
    
    async def generate_video(self, project_id: str, script: str, title: str) -> Path:
        """Optimized video generation pipeline"""
        try:
            logger.info(f"🎬 Starting optimized video generation: {project_id}")
            
            # Parse script (max 4 scenes)
            scenes = self.parse_script(script, max_scenes=4)
            logger.info(f"📝 Processing {len(scenes)} scenes")
            
            # Generate audio first
            full_text = ' '.join([s['text'] for s in scenes])
            audio_path = self.temp_dir / f"{project_id}_audio.mp3"
            total_duration = await self.generate_audio(full_text, audio_path)
            
            scene_duration = total_duration / len(scenes)
            
            # Generate images one by one and create clips immediately
            video_clips = []
            
            # Simple intro (1 second)
            intro = self.create_solid_clip(1.0)
            video_clips.append(intro)
            
            # Process each scene
            for i, scene in enumerate(scenes):
                logger.info(f"[{i+1}/{len(scenes)}] {scene['scene'][:50]}...")
                
                is_cat_scene = any(w in scene['scene'].lower() for w in ['cat', 'kitten', 'feline'])
                image_path = self.temp_dir / f"{project_id}_scene_{i}.png"
                
                if is_cat_scene:
                    success = await self.generate_cat_image(scene['scene'], image_path)
                    if not success:
                        # Fallback to solid color
                        clip = self.create_solid_clip(scene_duration, color=(100, 50, 150))
                        video_clips.append(clip)
                        continue
                else:
                    # For non-cat scenes, use simple colored background
                    clip = self.create_solid_clip(scene_duration, color=(50, 50, 100))
                    video_clips.append(clip)
                    continue
                
                # Create image clip (smaller resolution for memory)
                if image_path.exists():
                    try:
                        img_clip = ImageClip(str(image_path), duration=scene_duration)
                        
                        # Simple resize to vertical format (720x1280 for Shorts)
                        from moviepy import vfx
                        
                        # Scale to fit height
                        target_height = 1280
                        scale_factor = target_height / img_clip.h
                        new_width = int(img_clip.w * scale_factor)
                        
                        img_clip = img_clip.with_effects([vfx.Resize(width=new_width)])
                        
                        # Crop to center if too wide
                        if img_clip.w > 720:
                            x_start = (img_clip.w - 720) // 2
                            img_clip = img_clip.with_effects([
                                vfx.Crop(x1=x_start, width=720, y1=0, height=1280)
                            ])
                        
                        video_clips.append(img_clip)
                        
                        # Delete image file immediately to free memory
                        image_path.unlink()
                        
                    except Exception as e:
                        logger.error(f"Clip creation failed: {str(e)}")
                        clip = self.create_solid_clip(scene_duration)
                        video_clips.append(clip)
            
            # Simple outro (1 second)
            outro = self.create_solid_clip(1.0)
            video_clips.append(outro)
            
            # Concatenate all clips
            logger.info("🎞️ Assembling video...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Add audio (start after 1s intro)
            audio_clip = AudioFileClip(str(audio_path))
            audio_clip = audio_clip.with_start(1.0)
            final_video = final_video.with_audio(audio_clip)
            
            # Export with optimized settings
            output_path = self.output_dir / f"{project_id}.mp4"
            logger.info("💾 Encoding video...")
            
            final_video.write_videofile(
                str(output_path),
                fps=24,  # Lower FPS for smaller file
                codec='libx264',
                audio_codec='aac',
                preset='ultrafast',  # Fast encoding
                threads=2,  # Limit threads for memory
                bitrate='500k',  # Lower bitrate
                logger=None
            )
            
            # Cleanup
            final_video.close()
            audio_clip.close()
            for clip in video_clips:
                try:
                    clip.close()
                except:
                    pass
            
            # Delete temp audio
            if audio_path.exists():
                audio_path.unlink()
            
            file_size = output_path.stat().st_size
            logger.info(f"✅ Video complete: {file_size:,} bytes")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Video generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
