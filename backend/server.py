from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from newsapi import NewsApiClient
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import shutil
from video_generator import VideoGenerator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Kitten Comedy API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
news_client = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY', ''))
emergent_key = os.environ.get('EMERGENT_LLM_KEY', '')

# Models
class NewsArticle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: str
    source: dict
    content: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ComedyScript(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    articleId: str
    script: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VideoProject(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    scriptId: str
    articleId: str
    status: str = "pending"  # pending, generating, completed, failed
    videoUrl: Optional[str] = None
    errorMessage: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GenerateScriptRequest(BaseModel):
    articleId: str
    articleTitle: str
    articleDescription: str

class CreateVideoRequest(BaseModel):
    scriptId: str
    title: str

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Kitten Comedy Purrfect API", "version": "1.0.0"}

@api_router.get("/news/trending", response_model=List[NewsArticle])
async def get_trending_news(category: str = "general", country: str = "us"):
    """Fetch trending news articles"""
    try:
        if not os.environ.get('NEWS_API_KEY'):
            raise HTTPException(status_code=500, detail="News API key not configured")
        
        # Fetch top headlines
        response = news_client.get_top_headlines(
            category=category,
            country=country,
            page_size=20
        )
        
        if response['status'] != 'ok':
            raise HTTPException(status_code=500, detail="Failed to fetch news")
        
        articles = []
        for article in response['articles']:
            news_article = NewsArticle(
                title=article['title'],
                description=article.get('description', ''),
                url=article['url'],
                urlToImage=article.get('urlToImage'),
                publishedAt=article['publishedAt'],
                source=article['source'],
                content=article.get('content', '')
            )
            articles.append(news_article)
            
            # Save to database
            doc = news_article.model_dump()
            doc['createdAt'] = doc['createdAt'].isoformat()
            await db.news_articles.update_one(
                {'title': news_article.title},
                {'$set': doc},
                upsert=True
            )
        
        return articles
    except Exception as e:
        logging.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/scripts/generate", response_model=ComedyScript)
async def generate_comedy_script(request: GenerateScriptRequest):
    """Generate a comedy script from a news article using AI"""
    try:
        if not emergent_key:
            raise HTTPException(status_code=500, detail="Emergent LLM key not configured")
        
        # Create AI prompt optimized for YouTube Shorts
        prompt = f"""You are a comedy writer for a YouTube Shorts channel called 'Kitten Comedy Purrfect' that creates viral cat-themed comedy news.

News Article:
Title: {request.articleTitle}
Description: {request.articleDescription}

Create a punchy, viral-ready 60-second YouTube Shorts script that:
1. HOOK (first 3 seconds): Start with an attention-grabbing statement
2. NEWS + HUMOR: Present the news with cat-themed comedy twists
3. VISUAL CUES: Include [SCENE: description] markers for each visual scene
4. PACING: Keep sentences short and punchy for fast pacing
5. ENDING: End with a memorable punchline or call-to-action

Format as:
[SCENE: description]
Narrator text here.

[SCENE: description]
Next narrator text.

Requirements:
- Maximum 150 words (60 seconds when spoken)
- 4-6 distinct scenes
- Cat puns and wordplay throughout
- Family-friendly
- Viral potential

Script:"""
        
        # Generate script using OpenAI via Emergent
        chat = LlmChat(
            api_key=emergent_key,
            session_id=f"script_{request.articleId}",
            system_message="You are a professional comedy writer specializing in cat-themed humor."
        ).with_model("openai", "gpt-5.1")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        script_text = response.strip()
        
        # Save script to database
        comedy_script = ComedyScript(
            articleId=request.articleId,
            script=script_text
        )
        
        doc = comedy_script.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.comedy_scripts.insert_one(doc)
        
        return comedy_script
    except Exception as e:
        logging.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/scripts", response_model=List[ComedyScript])
async def get_scripts():
    """Get all comedy scripts"""
    try:
        scripts = await db.comedy_scripts.find({}, {"_id": 0}).sort("createdAt", -1).to_list(100)
        for script in scripts:
            if isinstance(script['createdAt'], str):
                script['createdAt'] = datetime.fromisoformat(script['createdAt'])
        return scripts
    except Exception as e:
        logging.error(f"Error fetching scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/videos/create", response_model=VideoProject)
async def create_video_project(request: CreateVideoRequest):
    """Create a video project (placeholder for video generation)"""
    try:
        # Get the script
        script_doc = await db.comedy_scripts.find_one({"id": request.scriptId}, {"_id": 0})
        if not script_doc:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # Create video project
        video_project = VideoProject(
            title=request.title,
            scriptId=request.scriptId,
            articleId=script_doc['articleId'],
            status="pending"
        )
        
        doc = video_project.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        doc['updatedAt'] = doc['updatedAt'].isoformat()
        await db.video_projects.insert_one(doc)
        
        # Trigger background video generation
        asyncio.create_task(generate_video_background(
            video_project.id,
            script_doc['script'],
            request.title
        ))
        
        return video_project
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating video project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_video_background(project_id: str, script: str, title: str):
    """Background task to generate real video with TTS and images"""
    try:
        # Update status to generating
        await db.video_projects.update_one(
            {"id": project_id},
            {"$set": {"status": "generating", "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Initialize video generator
        video_gen = VideoGenerator()
        
        # Generate real video
        output_path = await video_gen.generate_video(
            project_id=project_id,
            script=script,
            title=title
        )
        
        # Verify file size (must be at least 100KB for valid video)
        file_size = output_path.stat().st_size
        if file_size < 100000:  # 100KB minimum
            raise Exception(f"Generated video too small: {file_size} bytes. Expected >100KB")
        
        logger.info(f"Video file created: {output_path} ({file_size:,} bytes)")
        
        # Update status to completed
        await db.video_projects.update_one(
            {"id": project_id},
            {"$set": {
                "status": "completed",
                "videoUrl": f"/videos/{project_id}/download",
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }}
        )
    except Exception as e:
        logging.error(f"Error generating video: {str(e)}")
        await db.video_projects.update_one(
            {"id": project_id},
            {"$set": {
                "status": "failed",
                "errorMessage": str(e),
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }}
        )

@api_router.get("/videos", response_model=List[VideoProject])
async def get_video_projects():
    """Get all video projects"""
    try:
        projects = await db.video_projects.find({}, {"_id": 0}).sort("createdAt", -1).to_list(100)
        for project in projects:
            if isinstance(project['createdAt'], str):
                project['createdAt'] = datetime.fromisoformat(project['createdAt'])
            if isinstance(project['updatedAt'], str):
                project['updatedAt'] = datetime.fromisoformat(project['updatedAt'])
        return projects
    except Exception as e:
        logging.error(f"Error fetching video projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/videos/{project_id}", response_model=VideoProject)
async def get_video_project(project_id: str):
    """Get a specific video project"""
    try:
        project = await db.video_projects.find_one({"id": project_id}, {"_id": 0})
        if not project:
            raise HTTPException(status_code=404, detail="Video project not found")
        
        if isinstance(project['createdAt'], str):
            project['createdAt'] = datetime.fromisoformat(project['createdAt'])
        if isinstance(project['updatedAt'], str):
            project['updatedAt'] = datetime.fromisoformat(project['updatedAt'])
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching video project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/videos/{project_id}/download")
async def download_video(project_id: str):
    """Download the generated video file"""
    try:
        # Get project details
        project = await db.video_projects.find_one({"id": project_id}, {"_id": 0})
        if not project:
            raise HTTPException(status_code=404, detail="Video project not found")
        
        if project['status'] != 'completed':
            raise HTTPException(status_code=400, detail=f"Video is not ready. Status: {project['status']}")
        
        # Check if video file exists
        video_path = ROOT_DIR / "generated_videos" / f"{project_id}.mp4"
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Return file for download
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=f"{project['title']}.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()