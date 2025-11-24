# 🐱 Kitten Comedy Purrfect - AI YouTube Content Generator

An AI-powered content generation system for creating comedy videos that combine trending news with cat-themed humor, inspired by channels like Rankzilla and Kittyrants.

## 🎯 Features

### ✅ Currently Implemented

- **Trending News Fetching**: Pulls real-time news from NewsAPI across multiple categories
- **AI Comedy Script Generation**: Uses OpenAI GPT-5.1 to create hilarious cat-themed comedy scripts from news articles
- **Content Management Dashboard**: Beautiful React interface to manage the entire workflow
- **Video Project Tracking**: Track status of video generation projects
- **MongoDB Storage**: Persistent storage for articles, scripts, and video projects

### 🚀 How It Works

1. **Browse News**: Select trending news articles from various categories (general, technology, entertainment, sports)
2. **Generate Scripts**: AI creates a 60-90 second comedy script combining the news with cat humor
3. **Create Videos**: Initiate video project creation (currently simulated)
4. **Manual Upload**: Download generated videos and upload to YouTube Studio

## 🏗️ Architecture

```
Backend (FastAPI):
├── News Service (NewsAPI integration)
├── AI Script Generator (OpenAI GPT-5.1 via Emergent LLM)
├── Video Project Manager
└── MongoDB Database

Frontend (React):
├── News Browser
├── Script Editor
├── Video Project Dashboard
└── Real-time Status Updates
```

## 📋 API Endpoints

### News
- `GET /api/news/trending?category={category}&country={country}` - Fetch trending news

### Scripts
- `POST /api/scripts/generate` - Generate comedy script from news article
- `GET /api/scripts` - Get all generated scripts

### Videos
- `POST /api/videos/create` - Create video project
- `GET /api/videos` - Get all video projects
- `GET /api/videos/{id}` - Get specific video project

## 🔑 Configuration

### Environment Variables

**Backend (.env):**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-xxx
NEWS_API_KEY=your-newsapi-key
```

**Frontend (.env):**
```
REACT_APP_BACKEND_URL=https://your-domain.preview.emergentagent.com
WDS_SOCKET_PORT=443
```

## 🎨 UI Features

- **Modern Gradient Design**: Purple/blue gradient theme with glassmorphism effects
- **Category Filtering**: Browse news by different categories
- **Real-time Updates**: Live status tracking for video projects
- **Responsive Layout**: Works on desktop and mobile devices
- **Script Preview**: View generated scripts before creating videos

## 🔧 Technical Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **Motor**: Async MongoDB driver
- **NewsAPI**: News aggregation service
- **OpenAI GPT-5.1**: AI script generation (via Emergent integration)
- **MoviePy**: Video editing capabilities (ready for implementation)
- **ElevenLabs**: Text-to-speech (ready for implementation)

### Frontend
- **React 19**: Latest React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Radix UI**: Accessible component primitives

## 📦 Dependencies

See `requirements.txt` for backend dependencies and `package.json` for frontend dependencies.

## 🎯 Next Steps for Full Automation

To implement full video generation and YouTube uploads:

1. **Video Generation**:
   - Implement text-to-speech using ElevenLabs
   - Add image/video compilation with MoviePy
   - Generate cat animations or use stock cat videos
   - Add background music and effects

2. **YouTube Integration**:
   - Set up Google Cloud Console OAuth 2.0
   - Implement YouTube Data API v3 upload
   - Add video metadata management
   - Schedule automatic uploads

3. **Enhanced Features**:
   - Video thumbnail generation
   - SEO-optimized titles and descriptions
   - Analytics integration
   - Content calendar

## 🎬 Content Strategy

The system creates comedy content by:
1. Taking real trending news stories
2. Adding cat-themed humor and wordplay
3. Including stage directions for visuals
4. Keeping content family-friendly and engaging
5. Optimizing for 60-90 second videos (perfect for YouTube Shorts/TikTok)

## 📊 Current Status

- ✅ News fetching: **Working**
- ✅ AI script generation: **Working**
- ✅ Content dashboard: **Working**
- ⏳ Video generation: **Placeholder (ready for implementation)**
- ⏳ YouTube upload: **Manual (automation ready when you set up OAuth)**

## 🚀 Getting Started

1. Get a free NewsAPI key from https://newsapi.org/register
2. The system uses Emergent LLM key for AI (already configured)
3. Access the dashboard to start creating content
4. Generate scripts from trending news
5. Create video projects (currently simulated)
6. Manually upload to your YouTube channel

## 🎯 YouTube Channel

Channel: **Kittencomedypurrfect**
URL: https://www.youtube.com/channel/UCGLA2MIreXH-zaRSAu6IKFA

## 💡 Content Examples

The AI generates scripts like:
- News about space missions → "Cat's Guide to Space (Hint: It's Just a Big Cardboard Box)"
- Tech announcements → "New iPhone Features Cats Actually Want"
- Sports news → "Cats Explain Why They're Better at Every Sport"

## 🔒 Security

- API keys stored in environment variables
- MongoDB connection secured
- CORS properly configured
- No sensitive data exposed to frontend

## 📝 License

This project is created for your personal YouTube channel.

---

Built with ❤️ and 🐱 for Kitten Comedy Purrfect
