"""
Real video generation with TTS, images, and assembly
"""
import os
import asyncio
import re
from pathlib import Path
from typing import List, Dict
import logging
from dotenv import load_dotenv
import base64
import requests

from emergentintegrations.llm.openai import OpenAITextToSpeech
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
from moviepy import (
    VideoFileClip, ImageClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, CompositeAudioClip, ColorClip
)

logger = logging.getLogger(__name__)

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class VideoGenerator:
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.tts = OpenAITextToSpeech(api_key=self.api_key)
        self.image_gen = OpenAIImageGeneration(api_key=self.api_key)
        self.output_dir = ROOT_DIR / "generated_videos"
        self.temp_dir = ROOT_DIR / "temp_assets"
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
    
    def parse_script(self, script: str) -> List[Dict]:
        """
        Parse script into scenes with visual cues and narration
        Returns: [{"scene": "description", "text": "narrator text"}, ...]
        """
        scenes = []
        lines = script.strip().split('\n')
        
        current_scene = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a scene marker
            scene_match = re.match(r'\[SCENE:?\s*([^\]]+)\]', line, re.IGNORECASE)
            if scene_match:
                # Save previous scene if exists
                if current_scene and current_text:
                    scenes.append({
                        "scene": current_scene,
                        "text": ' '.join(current_text)
                    })
                
                current_scene = scene_match.group(1).strip()
                current_text = []
            else:
                # It's narration text
                current_text.append(line)
        
        # Add last scene
        if current_scene and current_text:
            scenes.append({
                "scene": current_scene,
                "text": ' '.join(current_text)
            })
        
        # If no scenes found, create one scene with all text
        if not scenes:
            scenes.append({
                "scene": "Main scene",
                "text": script
            })
        
        return scenes
    
    async def generate_audio(self, text: str, output_path: Path) -> float:
        """
        Generate TTS audio and return duration in seconds
        """
        try:
            logger.info(f"Generating TTS for: {text[:50]}...")
            
            audio_bytes = await self.tts.generate_speech(
                text=text,
                model="tts-1",  # Fast model for quick generation
                voice="nova",  # Energetic voice for comedy
                speed=1.1  # Slightly faster for Shorts pacing
            )
            
            # Save audio file
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            # Get duration using moviepy
            audio_clip = AudioFileClip(str(output_path))
            duration = audio_clip.duration
            audio_clip.close()
            
            logger.info(f"Audio generated: {duration:.2f}s")
            return duration
            
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            raise
    
    async def generate_cat_image(self, scene_description: str, output_path: Path) -> bool:
        """
        Generate a cat-themed image for a scene
        """
        try:
            # Enhance prompt for cat comedy
            prompt = f"Digital illustration in vibrant cartoon style: {scene_description}. Include cute, expressive cats. Bright colors, funny, family-friendly, YouTube thumbnail quality."
            
            logger.info(f"Generating image: {prompt[:60]}...")
            
            images = await self.image_gen.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1
            )
            
            if images and len(images) > 0:
                with open(output_path, "wb") as f:
                    f.write(images[0])
                logger.info(f"Image generated: {output_path}")
                return True
            else:
                logger.warning("No image generated")
                return False
                
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return False
    
    def fetch_stock_image(self, query: str, output_path: Path) -> bool:
        """
        Fetch a stock image from Unsplash (free, no API key required)
        """
        try:
            # Use Unsplash's public API (no auth required for basic usage)
            url = f"https://source.unsplash.com/1280x720/?{query.replace(' ', ',')}"
            
            logger.info(f"Fetching stock image: {query}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Stock image fetched: {output_path}")
                return True
            else:
                logger.warning(f"Stock image fetch failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Stock image fetch error: {str(e)}")
            return False
    
    def create_intro_clip(self, duration: float = 2.0) -> VideoFileClip:
        """
        Create a simple intro with text animation
        """
        try:
            # Create text clip with MoviePy 2.x syntax
            txt_clip = TextClip(
                text="Kitten Comedy\nPurrfect",
                font_size=80,
                color='white',
                size=(1080, 1920),
                method='caption'
            ).with_duration(duration).with_position('center')
            
            # Create purple background using ColorClip
            bg_clip = ColorClip(
                size=(1080, 1920),
                color=(139, 0, 255),
                duration=duration
            )
            
            # Composite
            intro = CompositeVideoClip([bg_clip, txt_clip])
            
            return intro
            
        except Exception as e:
            logger.error(f"Intro creation failed: {str(e)}")
            # Return simple colored clip as fallback
            return ColorClip(
                size=(1080, 1920),
                color=(139, 0, 255),
                duration=duration
            )
    
    def create_outro_clip(self, duration: float = 2.0) -> VideoFileClip:
        """
        Create a simple outro with subscribe message
        """
        try:
            txt_clip = TextClip(
                text="Subscribe for more\ncat comedy! 🐱",
                font_size=70,
                color='white',
                size=(1080, 1920),
                method='caption'
            ).with_duration(duration).with_position('center')
            
            bg_clip = ColorClip(
                size=(1080, 1920),
                color=(139, 0, 255),
                duration=duration
            )
            
            outro = CompositeVideoClip([bg_clip, txt_clip])
            
            return outro
            
        except Exception as e:
            logger.error(f"Outro creation failed: {str(e)}")
            return ColorClip(
                size=(1080, 1920),
                color=(139, 0, 255),
                duration=duration
            )
    
    def _create_solid_color_image(self, size: tuple, color: tuple) -> str:
        """Create a solid color image and return path"""
        from PIL import Image
        img = Image.new('RGB', size, color)
        path = self.temp_dir / f"solid_{color[0]}_{color[1]}_{color[2]}.png"
        img.save(path)
        return str(path)
    
    async def generate_video(
        self,
        project_id: str,
        script: str,
        title: str
    ) -> Path:
        """
        Main video generation pipeline
        """
        try:
            logger.info(f"Starting video generation for project: {project_id}")
            
            # Parse script into scenes
            scenes = self.parse_script(script)
            logger.info(f"Parsed {len(scenes)} scenes from script")
            
            # Generate full narration audio first
            full_text = ' '.join([scene['text'] for scene in scenes])
            audio_path = self.temp_dir / f"{project_id}_audio.mp3"
            total_audio_duration = await self.generate_audio(full_text, audio_path)
            
            # Calculate duration per scene (evenly distributed for now)
            scene_duration = total_audio_duration / len(scenes) if scenes else 5.0
            
            # Generate images for each scene
            scene_clips = []
            for i, scene in enumerate(scenes):
                logger.info(f"Processing scene {i+1}/{len(scenes)}: {scene['scene'][:40]}...")
                
                # Determine if this should be AI-generated or stock
                is_cat_scene = any(word in scene['scene'].lower() for word in ['cat', 'kitten', 'feline', 'paw', 'meow'])
                
                image_path = self.temp_dir / f"{project_id}_scene_{i}.png"
                
                if is_cat_scene:
                    # Generate AI cat image
                    success = await self.generate_cat_image(scene['scene'], image_path)
                    if not success:
                        # Fallback to stock
                        self.fetch_stock_image("funny cat", image_path)
                else:
                    # Use stock image for news/general scenes
                    # Extract key words from scene description
                    keywords = scene['scene'].split()[:3]  # First 3 words
                    self.fetch_stock_image(' '.join(keywords), image_path)
                
                # Create image clip
                if image_path.exists():
                    img_clip = ImageClip(str(image_path), duration=scene_duration)
                    # Resize to vertical format (9:16 for Shorts)
                    # In MoviePy 2.x, use with_effects instead of direct resize
                    from moviepy import vfx
                    img_clip = img_clip.with_effects([vfx.Resize(height=1920)])
                    if img_clip.w > 1080:
                        # Crop to center
                        x_start = (img_clip.w - 1080) // 2
                        img_clip = img_clip.with_effects([
                            vfx.Crop(x1=x_start, width=1080, y1=0, height=1920)
                        ])
                    scene_clips.append(img_clip)
                else:
                    # Fallback: solid color with text
                    logger.warning(f"No image for scene {i}, using fallback")
                    fallback = self.create_intro_clip(scene_duration)
                    scene_clips.append(fallback)
            
            # Create intro and outro
            intro_clip = self.create_intro_clip(1.5)
            outro_clip = self.create_outro_clip(2.0)
            
            # Concatenate all video clips
            all_clips = [intro_clip] + scene_clips + [outro_clip]
            final_video = concatenate_videoclips(all_clips, method="compose")
            
            # Add audio to the main content (skip intro/outro)
            audio_clip = AudioFileClip(str(audio_path))
            # In MoviePy 2.x, use with_start instead of set_start
            audio_clip = audio_clip.with_start(1.5)  # Start after intro
            
            # Composite final video with audio
            final_video = final_video.with_audio(audio_clip)
            
            # Export
            output_path = self.output_dir / f"{project_id}.mp4"
            final_video.write_videofile(
                str(output_path),
                fps=30,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4,
                logger=None  # Suppress moviepy logs
            )
            
            # Cleanup
            final_video.close()
            audio_clip.close()
            for clip in all_clips:
                clip.close()
            
            logger.info(f"Video generation complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise
