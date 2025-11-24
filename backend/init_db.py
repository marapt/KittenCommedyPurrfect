"""
Database initialization script to create indexes
Run this once to optimize database queries
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def init_database():
    """Create necessary indexes for optimal performance"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        print("🔧 Initializing database indexes...")
        
        # Create index on news_articles.title (used in update_one queries)
        await db.news_articles.create_index([("title", 1)], unique=True)
        print("✅ Created index on news_articles.title")
        
        # Create indexes for better query performance
        await db.comedy_scripts.create_index([("articleId", 1)])
        print("✅ Created index on comedy_scripts.articleId")
        
        await db.comedy_scripts.create_index([("createdAt", -1)])
        print("✅ Created index on comedy_scripts.createdAt")
        
        await db.video_projects.create_index([("scriptId", 1)])
        print("✅ Created index on video_projects.scriptId")
        
        await db.video_projects.create_index([("status", 1)])
        print("✅ Created index on video_projects.status")
        
        await db.video_projects.create_index([("createdAt", -1)])
        print("✅ Created index on video_projects.createdAt")
        
        print("\n🎉 Database initialization complete!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
