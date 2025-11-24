import { useState, useEffect } from 'react';
import '@/App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState('news');
  const [newsArticles, setNewsArticles] = useState([]);
  const [scripts, setScripts] = useState([]);
  const [videoProjects, setVideoProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [generatingScript, setGeneratingScript] = useState(false);
  const [selectedScript, setSelectedScript] = useState(null);
  const [videoTitle, setVideoTitle] = useState('');

  // Fetch trending news
  const fetchNews = async (category = 'general') => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/news/trending?category=${category}`);
      setNewsArticles(response.data);
    } catch (error) {
      console.error('Error fetching news:', error);
      alert('Error fetching news. Please check if NEWS_API_KEY is configured.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch scripts
  const fetchScripts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/scripts`);
      setScripts(response.data);
    } catch (error) {
      console.error('Error fetching scripts:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch video projects
  const fetchVideoProjects = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/videos`);
      setVideoProjects(response.data);
    } catch (error) {
      console.error('Error fetching video projects:', error);
    } finally {
      setLoading(false);
    }
  };

  // Generate comedy script
  const generateScript = async (article) => {
    setGeneratingScript(true);
    try {
      const response = await axios.post(`${API}/scripts/generate`, {
        articleId: article.id,
        articleTitle: article.title,
        articleDescription: article.description || article.title
      });
      alert('Script generated successfully!');
      fetchScripts();
      setActiveTab('scripts');
    } catch (error) {
      console.error('Error generating script:', error);
      alert('Error generating script: ' + (error.response?.data?.detail || error.message));
    } finally {
      setGeneratingScript(false);
    }
  };

  // Create video project
  const createVideo = async () => {
    if (!videoTitle.trim()) {
      alert('Please enter a video title');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API}/videos/create`, {
        scriptId: selectedScript.id,
        title: videoTitle
      });
      alert('Video project created! Generation started.');
      setVideoTitle('');
      setSelectedScript(null);
      fetchVideoProjects();
      setActiveTab('videos');
    } catch (error) {
      console.error('Error creating video:', error);
      alert('Error creating video: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'news') {
      fetchNews();
    } else if (activeTab === 'scripts') {
      fetchScripts();
    } else if (activeTab === 'videos') {
      fetchVideoProjects();
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-purple-500">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">🐱</div>
              <div>
                <h1 className="text-3xl font-bold text-white" data-testid="app-title">Kitten Comedy Purrfect</h1>
                <p className="text-purple-300 text-sm">AI-Powered Cat Comedy News Channel</p>
              </div>
            </div>
            <div className="text-purple-300 text-sm">
              <span className="px-3 py-1 bg-purple-600 bg-opacity-30 rounded-full">✨ Beta</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="container mx-auto px-4 mt-6">
        <div className="flex space-x-2 bg-black bg-opacity-30 p-2 rounded-lg backdrop-blur-sm">
          <button
            onClick={() => setActiveTab('news')}
            data-testid="news-tab"
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'news'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-purple-300 hover:bg-purple-600 hover:bg-opacity-30'
            }`}
          >
            📰 Trending News
          </button>
          <button
            onClick={() => setActiveTab('scripts')}
            data-testid="scripts-tab"
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'scripts'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-purple-300 hover:bg-purple-600 hover:bg-opacity-30'
            }`}
          >
            📝 Comedy Scripts ({scripts.length})
          </button>
          <button
            onClick={() => setActiveTab('videos')}
            data-testid="videos-tab"
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'videos'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-purple-300 hover:bg-purple-600 hover:bg-opacity-30'
            }`}
          >
            🎬 Video Projects ({videoProjects.length})
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* News Tab */}
        {activeTab === 'news' && (
          <div>
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">Select News for Comedy Script</h2>
              <div className="flex space-x-2">
                {['general', 'technology', 'entertainment', 'sports'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => fetchNews(cat)}
                    data-testid={`category-${cat}`}
                    className="px-4 py-2 bg-purple-600 bg-opacity-50 text-white rounded-lg hover:bg-opacity-70 transition-all capitalize"
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
            {loading ? (
              <div className="text-center text-white text-xl py-12" data-testid="loading-news">Loading news... 🐾</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {newsArticles.map((article, idx) => (
                  <div key={idx} className="bg-black bg-opacity-40 backdrop-blur-sm rounded-xl overflow-hidden border border-purple-500 hover:border-purple-400 transition-all" data-testid="news-article">
                    {article.urlToImage && (
                      <img src={article.urlToImage} alt={article.title} className="w-full h-48 object-cover" />
                    )}
                    <div className="p-4">
                      <h3 className="text-lg font-bold text-white mb-2 line-clamp-2">{article.title}</h3>
                      <p className="text-purple-200 text-sm mb-4 line-clamp-3">{article.description}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-purple-400">{article.source.name}</span>
                        <button
                          onClick={() => generateScript(article)}
                          disabled={generatingScript}
                          data-testid="generate-script-btn"
                          className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all disabled:opacity-50"
                        >
                          {generatingScript ? '⏳ Generating...' : '✨ Generate Script'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Scripts Tab */}
        {activeTab === 'scripts' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Generated Comedy Scripts</h2>
            {loading ? (
              <div className="text-center text-white text-xl py-12" data-testid="loading-scripts">Loading scripts... 🐾</div>
            ) : scripts.length === 0 ? (
              <div className="text-center text-purple-300 py-12" data-testid="no-scripts">
                <div className="text-6xl mb-4">📝</div>
                <p className="text-xl">No scripts yet. Generate one from trending news!</p>
              </div>
            ) : (
              <div className="space-y-6">
                {scripts.map((script, idx) => (
                  <div key={idx} className="bg-black bg-opacity-40 backdrop-blur-sm rounded-xl p-6 border border-purple-500" data-testid="script-item">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-white mb-2">Script #{idx + 1}</h3>
                        <p className="text-xs text-purple-400">Created: {new Date(script.createdAt).toLocaleString()}</p>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedScript(script);
                          setVideoTitle(`Kitten Comedy - ${new Date().toLocaleDateString()}`);
                        }}
                        data-testid="create-video-btn"
                        className="px-4 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-500 hover:to-blue-500 transition-all"
                      >
                        🎬 Create Video
                      </button>
                    </div>
                    <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 text-purple-100 whitespace-pre-wrap font-mono text-sm">
                      {script.script}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Videos Tab */}
        {activeTab === 'videos' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Video Projects</h2>
            {loading ? (
              <div className="text-center text-white text-xl py-12" data-testid="loading-videos">Loading videos... 🐾</div>
            ) : videoProjects.length === 0 ? (
              <div className="text-center text-purple-300 py-12" data-testid="no-videos">
                <div className="text-6xl mb-4">🎬</div>
                <p className="text-xl">No video projects yet. Create one from your scripts!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {videoProjects.map((project, idx) => (
                  <div key={idx} className="bg-black bg-opacity-40 backdrop-blur-sm rounded-xl p-6 border border-purple-500" data-testid="video-project">
                    <h3 className="text-xl font-bold text-white mb-2">{project.title}</h3>
                    <div className="mb-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        project.status === 'completed' ? 'bg-green-600' :
                        project.status === 'generating' ? 'bg-yellow-600' :
                        project.status === 'failed' ? 'bg-red-600' :
                        'bg-gray-600'
                      }`}>
                        {project.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-xs text-purple-400 mb-4">Created: {new Date(project.createdAt).toLocaleString()}</p>
                    {project.status === 'completed' && (
                      <div className="text-center py-8 bg-gray-900 bg-opacity-50 rounded-lg">
                        <div className="text-4xl mb-2">🎥</div>
                        <p className="text-purple-300 text-sm mb-4">Video ready for manual upload to YouTube Studio</p>
                        <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-all" data-testid="download-video-btn">
                          📥 Download Video
                        </button>
                      </div>
                    )}
                    {project.status === 'failed' && (
                      <p className="text-red-400 text-sm">{project.errorMessage}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Video Modal */}
      {selectedScript && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" data-testid="create-video-modal">
          <div className="bg-gray-900 rounded-xl p-8 max-w-2xl w-full mx-4 border-2 border-purple-500">
            <h3 className="text-2xl font-bold text-white mb-4">Create Video Project</h3>
            <div className="mb-6">
              <label className="block text-purple-300 mb-2 font-semibold">Video Title</label>
              <input
                type="text"
                value={videoTitle}
                onChange={(e) => setVideoTitle(e.target.value)}
                data-testid="video-title-input"
                className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-purple-500 focus:border-purple-400 outline-none"
                placeholder="Enter video title..."
              />
            </div>
            <div className="bg-gray-800 rounded-lg p-4 mb-6 max-h-64 overflow-y-auto">
              <p className="text-purple-200 text-sm whitespace-pre-wrap font-mono">{selectedScript.script}</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={createVideo}
                disabled={loading}
                data-testid="confirm-create-video-btn"
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-500 hover:to-blue-500 transition-all disabled:opacity-50 font-semibold"
              >
                {loading ? '⏳ Creating...' : '✨ Create Video'}
              </button>
              <button
                onClick={() => {
                  setSelectedScript(null);
                  setVideoTitle('');
                }}
                data-testid="cancel-create-video-btn"
                className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-all font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;