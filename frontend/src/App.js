import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [discoveryCards, setDiscoveryCards] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [matches, setMatches] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [profileForm, setProfileForm] = useState({
    bio: '',
    trading_experience: '',
    preferred_tokens: [],
    trading_style: '',
    portfolio_size: ''
  });

  const messagesEndRef = useRef(null);

  // Trading options
  const EXPERIENCE_OPTIONS = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
  const TOKEN_OPTIONS = ['Meme Coins', 'DeFi', 'GameFi', 'NFTs', 'Blue Chips', 'Layer 1s', 'AI Tokens'];
  const STYLE_OPTIONS = ['Day Trader', 'Swing Trader', 'HODLer', 'Scalper', 'Long-term Investor'];
  const PORTFOLIO_OPTIONS = ['Under $1K', '$1K-$10K', '$10K-$100K', '$100K+', 'Prefer not to say'];

  // Handle auth callback on page load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_success') === 'true') {
      const userId = urlParams.get('user_id');
      const isDemo = urlParams.get('demo') === 'true';
      
      if (userId) {
        if (isDemo) {
          // Create a demo user first
          createDemoUser().then(() => {
            fetchUserProfile(userId);
          });
        } else {
          fetchUserProfile(userId);
        }
      }
    } else if (urlParams.get('auth_error') === 'true') {
      alert('Authentication failed. Please try again.');
    }
  }, []);

  // Setup WebSocket when user is logged in
  useEffect(() => {
    if (currentUser && !ws) {
      // Convert HTTPS URL to WSS for WebSocket
      const wsUrl = API_BASE_URL.replace('https://', 'wss://') + `/api/ws/${currentUser.user_id}`;
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'new_match') {
          setShowMatchModal(true);
          fetchMatches();
        } else if (data.type === 'chat_message') {
          setMessages(prev => [...prev, data.message]);
        }
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      setWs(websocket);
      
      return () => {
        websocket.close();
      };
    }
  }, [currentUser, ws]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const createDemoUser = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/create-demo-user`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Failed to create demo user');
      }
    } catch (error) {
      console.error('Error creating demo user:', error);
    }
  };

  const fetchUserProfile = async (userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/${userId}`);
      const user = await response.json();
      setCurrentUser(user);
      
      // Check if profile is complete
      if (!user.trading_experience || user.preferred_tokens.length === 0 || !user.trading_style || !user.portfolio_size) {
        setProfileForm({
          bio: user.bio || '',
          trading_experience: user.trading_experience || '',
          preferred_tokens: user.preferred_tokens || [],
          trading_style: user.trading_style || '',
          portfolio_size: user.portfolio_size || ''
        });
        setCurrentView('profile-setup');
      } else {
        setCurrentView('discover');
        fetchDiscoveryCards();
        fetchMatches();
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchDiscoveryCards = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/discover/${currentUser.user_id}`);
      const cards = await response.json();
      setDiscoveryCards(cards);
      setCurrentCardIndex(0);
    } catch (error) {
      console.error('Error fetching discovery cards:', error);
    }
  };

  const fetchMatches = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/matches/${currentUser.user_id}`);
      const matchesData = await response.json();
      setMatches(matchesData);
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const fetchMessages = async (matchId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/messages/${matchId}`);
      const messagesData = await response.json();
      setMessages(messagesData);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleTwitterLogin = () => {
    window.location.href = `${API_BASE_URL}/api/login/twitter`;
  };

  const handleDemoLogin = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/create-demo-user`, {
        method: 'POST'
      });
      const demoUser = await response.json();
      setCurrentUser(demoUser);
      setProfileForm({
        bio: demoUser.bio || '',
        trading_experience: demoUser.trading_experience || '',
        preferred_tokens: demoUser.preferred_tokens || [],
        trading_style: demoUser.trading_style || '',
        portfolio_size: demoUser.portfolio_size || ''
      });
      setCurrentView('profile-setup');
    } catch (error) {
      console.error('Error creating demo user:', error);
    }
  };

  const handleSwipe = async (action) => {
    if (currentCardIndex >= discoveryCards.length) return;
    
    const currentCard = discoveryCards[currentCardIndex];
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/swipe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          swiper_id: currentUser.user_id,
          target_id: currentCard.user_id,
          action: action
        })
      });
      
      const result = await response.json();
      if (result.matched) {
        setShowMatchModal(true);
        fetchMatches();
      }
      
      setCurrentCardIndex(prev => prev + 1);
      
      // Load more cards if running low
      if (currentCardIndex >= discoveryCards.length - 2) {
        fetchDiscoveryCards();
      }
    } catch (error) {
      console.error('Error swiping:', error);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    
    try {
      await fetch(`${API_BASE_URL}/api/user/${currentUser.user_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileForm)
      });
      
      // Update current user state
      setCurrentUser(prev => ({ ...prev, ...profileForm }));
      setCurrentView('discover');
      fetchDiscoveryCards();
      fetchMatches();
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedMatch || !ws) return;
    
    ws.send(JSON.stringify({
      type: 'chat_message',
      match_id: selectedMatch.match_id,
      content: newMessage.trim()
    }));
    
    setNewMessage('');
  };

  const handleTokenToggle = (token) => {
    setProfileForm(prev => ({
      ...prev,
      preferred_tokens: prev.preferred_tokens.includes(token)
        ? prev.preferred_tokens.filter(t => t !== token)
        : [...prev.preferred_tokens, token]
    }));
  };

  // Login View
  if (currentView === 'login') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">SolMatch</h1>
            <p className="text-blue-200">Find your perfect trading buddy</p>
          </div>
          
          <div className="space-y-6">
            <div className="text-center">
              <p className="text-white/80 mb-6">Connect with Solana traders for collaborative trenching sessions</p>
              <button
                onClick={handleTwitterLogin}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 mb-4"
              >
                <span>🐦</span>
                <span>Continue with Twitter</span>
              </button>
              <div className="text-white/60 text-sm mb-4">or</div>
              <button
                onClick={handleDemoLogin}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <span>🎮</span>
                <span>Try Demo Mode</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Profile Setup View
  if (currentView === 'profile-setup') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Complete Your Trading Profile</h2>
            
            <form onSubmit={handleProfileUpdate} className="space-y-6">
              <div>
                <label className="block text-white font-medium mb-2">Bio</label>
                <textarea
                  value={profileForm.bio}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, bio: e.target.value }))}
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/50"
                  placeholder="Tell other traders about yourself..."
                  rows="3"
                />
              </div>

              <div>
                <label className="block text-white font-medium mb-2">Trading Experience</label>
                <select
                  value={profileForm.trading_experience}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, trading_experience: e.target.value }))}
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white"
                  required
                >
                  <option value="">Select experience level</option>
                  {EXPERIENCE_OPTIONS.map(exp => (
                    <option key={exp} value={exp} className="bg-gray-800">{exp}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-white font-medium mb-2">Preferred Token Categories</label>
                <div className="grid grid-cols-2 gap-2">
                  {TOKEN_OPTIONS.map(token => (
                    <button
                      key={token}
                      type="button"
                      onClick={() => handleTokenToggle(token)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        profileForm.preferred_tokens.includes(token)
                          ? 'bg-blue-500 text-white'
                          : 'bg-white/10 text-white/70 hover:bg-white/20'
                      }`}
                    >
                      {token}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-white font-medium mb-2">Trading Style</label>
                <select
                  value={profileForm.trading_style}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, trading_style: e.target.value }))}
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white"
                  required
                >
                  <option value="">Select trading style</option>
                  {STYLE_OPTIONS.map(style => (
                    <option key={style} value={style} className="bg-gray-800">{style}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-white font-medium mb-2">Portfolio Size</label>
                <select
                  value={profileForm.portfolio_size}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, portfolio_size: e.target.value }))}
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white"
                  required
                >
                  <option value="">Select portfolio size</option>
                  {PORTFOLIO_OPTIONS.map(size => (
                    <option key={size} value={size} className="bg-gray-800">{size}</option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                disabled={!profileForm.trading_experience || profileForm.preferred_tokens.length === 0 || !profileForm.trading_style || !profileForm.portfolio_size}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
              >
                Start Trading & Matching
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Main App View
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Navigation */}
      <nav className="bg-white/10 backdrop-blur-lg border-b border-white/20 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">SolMatch</h1>
          <div className="flex space-x-4">
            <button
              onClick={() => setCurrentView('discover')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                currentView === 'discover' ? 'bg-blue-500 text-white' : 'text-white/70 hover:text-white'
              }`}
            >
              Discover
            </button>
            <button
              onClick={() => setCurrentView('matches')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                currentView === 'matches' ? 'bg-blue-500 text-white' : 'text-white/70 hover:text-white'
              }`}
            >
              Matches ({matches.length})
            </button>
          </div>
          <div className="flex items-center space-x-3">
            <img
              src={currentUser?.avatar_url}
              alt="Profile"
              className="w-8 h-8 rounded-full border-2 border-white/30"
            />
            <span className="text-white font-medium">{currentUser?.display_name}</span>
          </div>
        </div>
      </nav>

      {/* Discover View */}
      {currentView === 'discover' && (
        <div className="max-w-md mx-auto pt-8 px-4">
          {currentCardIndex < discoveryCards.length ? (
            <div className="bg-white rounded-3xl overflow-hidden shadow-2xl">
              <div className="relative">
                <img
                  src={discoveryCards[currentCardIndex]?.avatar_url}
                  alt="Profile"
                  className="w-full h-96 object-cover"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                  <h3 className="text-2xl font-bold text-white">
                    {discoveryCards[currentCardIndex]?.display_name}
                  </h3>
                  <p className="text-white/80">@{discoveryCards[currentCardIndex]?.username}</p>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <p className="text-gray-700">{discoveryCards[currentCardIndex]?.bio}</p>
                
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-500">Experience:</span>
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                      {discoveryCards[currentCardIndex]?.trading_experience}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-500">Style:</span>
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {discoveryCards[currentCardIndex]?.trading_style}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-500">Portfolio:</span>
                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                      {discoveryCards[currentCardIndex]?.portfolio_size}
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium text-gray-500 block mb-2">Preferred Tokens:</span>
                    <div className="flex flex-wrap gap-2">
                      {discoveryCards[currentCardIndex]?.preferred_tokens.map(token => (
                        <span key={token} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                          {token}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-4 p-6 pt-0">
                <button
                  onClick={() => handleSwipe('pass')}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  ❌ Pass
                </button>
                <button
                  onClick={() => handleSwipe('like')}
                  className="flex-1 bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  ❤️ Like
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-white py-12">
              <h3 className="text-2xl font-bold mb-4">No more traders to discover!</h3>
              <p className="text-white/70 mb-6">Check back later for new potential matches.</p>
              <button
                onClick={() => setCurrentView('matches')}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
              >
                View Your Matches
              </button>
            </div>
          )}
        </div>
      )}

      {/* Matches View */}
      {currentView === 'matches' && !selectedMatch && (
        <div className="max-w-4xl mx-auto pt-8 px-4">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Your Matches</h2>
          
          {matches.length === 0 ? (
            <div className="text-center text-white py-12">
              <h3 className="text-xl font-semibold mb-4">No matches yet</h3>
              <p className="text-white/70 mb-6">Start swiping to find your trading buddies!</p>
              <button
                onClick={() => setCurrentView('discover')}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
              >
                Start Discovering
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {matches.map(match => (
                <div
                  key={match.match_id}
                  onClick={() => {
                    setSelectedMatch(match);
                    fetchMessages(match.match_id);
                  }}
                  className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 cursor-pointer hover:bg-white/15 transition-all"
                >
                  <div className="flex items-center space-x-4 mb-4">
                    <img
                      src={match.other_user.avatar_url}
                      alt="Profile"
                      className="w-16 h-16 rounded-full"
                    />
                    <div>
                      <h3 className="text-white font-semibold text-lg">
                        {match.other_user.display_name}
                      </h3>
                      <p className="text-white/70">@{match.other_user.username}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full text-xs">
                        {match.other_user.trading_experience}
                      </span>
                      <span className="bg-green-500/20 text-green-300 px-2 py-1 rounded-full text-xs">
                        {match.other_user.trading_style}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Chat View */}
      {currentView === 'matches' && selectedMatch && (
        <div className="max-w-4xl mx-auto pt-8 px-4">
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/20">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setSelectedMatch(null)}
                  className="text-white/70 hover:text-white"
                >
                  ← Back
                </button>
                <img
                  src={selectedMatch.other_user.avatar_url}
                  alt="Profile"
                  className="w-10 h-10 rounded-full"
                />
                <div>
                  <h3 className="text-white font-semibold">
                    {selectedMatch.other_user.display_name}
                  </h3>
                  <p className="text-white/70 text-sm">
                    {selectedMatch.other_user.trading_style} • {selectedMatch.other_user.trading_experience}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map(message => (
                <div
                  key={message.message_id}
                  className={`flex ${message.sender_id === currentUser.user_id ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                      message.sender_id === currentUser.user_id
                        ? 'bg-blue-500 text-white'
                        : 'bg-white/20 text-white'
                    }`}
                  >
                    <p>{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="p-6 border-t border-white/20">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/50"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Match Modal */}
      {showMatchModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">It's a Match!</h3>
            <p className="text-gray-600 mb-6">You and another trader liked each other. Start trenching together!</p>
            <button
              onClick={() => {
                setShowMatchModal(false);
                setCurrentView('matches');
              }}
              className="bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
            >
              Start Chatting
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;