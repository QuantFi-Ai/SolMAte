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
  const [uploading, setUploading] = useState(false);
  const [profileForm, setProfileForm] = useState({
    bio: '',
    location: '',
    show_twitter: true,
    twitter_username: '',
    trading_experience: '',
    years_trading: 0,
    preferred_tokens: [],
    trading_style: '',
    portfolio_size: '',
    risk_tolerance: '',
    best_trade: '',
    worst_trade: '',
    favorite_project: '',
    trading_hours: '',
    communication_style: '',
    preferred_communication_platform: '',
    preferred_trading_platform: '',
    looking_for: []
  });

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Enhanced trading options
  const EXPERIENCE_OPTIONS = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
  const TOKEN_OPTIONS = ['Meme Coins', 'DeFi', 'GameFi', 'NFTs', 'Blue Chips', 'Layer 1s', 'AI Tokens', 'RWA', 'Infrastructure'];
  const STYLE_OPTIONS = ['Day Trader', 'Swing Trader', 'HODLer', 'Scalper', 'Long-term Investor', 'Arbitrage'];
  const PORTFOLIO_OPTIONS = ['Under $1K', '$1K-$10K', '$10K-$100K', '$100K+', 'Prefer not to say'];
  const RISK_OPTIONS = ['Conservative', 'Moderate', 'Aggressive', 'YOLO'];
  const HOURS_OPTIONS = ['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night Owl', '24/7'];
  const COMMUNICATION_OPTIONS = ['Casual', 'Professional', 'Technical', 'Friendly'];
  const COMMUNICATION_PLATFORM_OPTIONS = ['Discord', 'Telegram', 'Twitter DM', 'Signal', 'WhatsApp', 'In-App Only'];
  const TRADING_PLATFORM_OPTIONS = ['Axiom', 'BullX', 'Photon', 'Padre', 'Jupiter', 'Raydium', 'Birdeye', 'DexScreener', 'Other'];
  const LOOKING_FOR_OPTIONS = ['Learning', 'Teaching', 'Alpha Sharing', 'Research Partner', 'Risk Management', 'Networking'];

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
      if (!user.profile_complete) {
        setProfileForm({
          bio: user.bio || '',
          location: user.location || '',
          show_twitter: user.show_twitter !== undefined ? user.show_twitter : true,
          twitter_username: user.twitter_username || '',
          trading_experience: user.trading_experience || '',
          years_trading: user.years_trading || 0,
          preferred_tokens: user.preferred_tokens || [],
          trading_style: user.trading_style || '',
          portfolio_size: user.portfolio_size || '',
          risk_tolerance: user.risk_tolerance || '',
          best_trade: user.best_trade || '',
          worst_trade: user.worst_trade || '',
          favorite_project: user.favorite_project || '',
          trading_hours: user.trading_hours || '',
          communication_style: user.communication_style || '',
          preferred_communication_platform: user.preferred_communication_platform || '',
          preferred_trading_platform: user.preferred_trading_platform || '',
          looking_for: user.looking_for || []
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
        location: demoUser.location || '',
        show_twitter: demoUser.show_twitter !== undefined ? demoUser.show_twitter : false,
        twitter_username: demoUser.twitter_username || '',
        trading_experience: demoUser.trading_experience || '',
        years_trading: demoUser.years_trading || 0,
        preferred_tokens: demoUser.preferred_tokens || [],
        trading_style: demoUser.trading_style || '',
        portfolio_size: demoUser.portfolio_size || '',
        risk_tolerance: demoUser.risk_tolerance || '',
        best_trade: demoUser.best_trade || '',
        worst_trade: demoUser.worst_trade || '',
        favorite_project: demoUser.favorite_project || '',
        trading_hours: demoUser.trading_hours || '',
        communication_style: demoUser.communication_style || '',
        preferred_communication_platform: demoUser.preferred_communication_platform || '',
        preferred_trading_platform: demoUser.preferred_trading_platform || '',
        looking_for: demoUser.looking_for || []
      });
      setCurrentView('profile-setup');
    } catch (error) {
      console.error('Error creating demo user:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image must be smaller than 5MB');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/api/upload-profile-image/${currentUser.user_id}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload image');
      }

      const result = await response.json();
      
      // Update current user with new avatar URL
      const updatedUser = await fetch(`${API_BASE_URL}/api/user/${currentUser.user_id}`);
      const userData = await updatedUser.json();
      setCurrentUser(userData);
      
      alert('Profile picture updated successfully!');
      
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Failed to upload image. Please try again.');
    } finally {
      setUploading(false);
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
      setCurrentUser(prev => ({ ...prev, ...profileForm, profile_complete: true }));
      
      // Determine where to go next
      if (currentView === 'profile-edit') {
        setCurrentView('discover'); // Go back to discover after editing
      } else {
        setCurrentView('discover'); // First time setup
        fetchDiscoveryCards();
        fetchMatches();
      }
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  const handleEditProfile = () => {
    // Load current user data into form
    setProfileForm({
      bio: currentUser.bio || '',
      location: currentUser.location || '',
      show_twitter: currentUser.show_twitter !== undefined ? currentUser.show_twitter : true,
      twitter_username: currentUser.twitter_username || '',
      trading_experience: currentUser.trading_experience || '',
      years_trading: currentUser.years_trading || 0,
      preferred_tokens: currentUser.preferred_tokens || [],
      trading_style: currentUser.trading_style || '',
      portfolio_size: currentUser.portfolio_size || '',
      risk_tolerance: currentUser.risk_tolerance || '',
      best_trade: currentUser.best_trade || '',
      worst_trade: currentUser.worst_trade || '',
      favorite_project: currentUser.favorite_project || '',
      trading_hours: currentUser.trading_hours || '',
      communication_style: currentUser.communication_style || '',
      preferred_communication_platform: currentUser.preferred_communication_platform || '',
      preferred_trading_platform: currentUser.preferred_trading_platform || '',
      looking_for: currentUser.looking_for || []
    });
    setCurrentView('profile-edit');
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

  const handleLookingForToggle = (item) => {
    setProfileForm(prev => ({
      ...prev,
      looking_for: prev.looking_for.includes(item)
        ? prev.looking_for.filter(t => t !== item)
        : [...prev.looking_for, item]
    }));
  };

  // Login View
  if (currentView === 'login') {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white border border-gray-200 rounded-2xl p-8 shadow-lg">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-black mb-2">SolMatch</h1>
            <p className="text-gray-600">Find your perfect trading partner</p>
          </div>
          
          <div className="space-y-4">
            <div className="text-center">
              <p className="text-gray-700 mb-6">Connect with Solana traders for collaborative trenching sessions</p>
              <button
                onClick={handleTwitterLogin}
                className="w-full bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 mb-4"
              >
                <span>🐦</span>
                <span>Continue with Twitter</span>
              </button>
              <div className="text-gray-400 text-sm mb-4">or</div>
              <button
                onClick={handleDemoLogin}
                className="w-full border border-gray-300 hover:bg-gray-50 text-black font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
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

  // Profile Setup/Edit View
  if (currentView === 'profile-setup' || currentView === 'profile-edit') {
    const isEditing = currentView === 'profile-edit';
    
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-black">
                {isEditing ? 'Edit Your Profile' : 'Complete Your Trading Profile'}
              </h2>
              {isEditing && (
                <button
                  onClick={() => setCurrentView('discover')}
                  className="text-gray-600 hover:text-black px-4 py-2 rounded-lg transition-all"
                >
                  ← Back to Discover
                </button>
              )}
            </div>

            {/* Profile Picture Upload Section */}
            <div className="mb-8 p-6 bg-gray-50 rounded-2xl">
              <h3 className="text-lg font-semibold text-black mb-4">Profile Picture</h3>
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <img
                    src={currentUser?.avatar_url}
                    alt="Profile"
                    className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
                  />
                  {uploading && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
                      <div className="loading-spinner"></div>
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-gray-600 mb-3">Upload a professional photo that represents you as a trader</p>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                      className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-all"
                    >
                      {uploading ? 'Uploading...' : 'Upload New Photo'}
                    </button>
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      accept="image/*"
                      className="hidden"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">JPG, PNG or GIF. Max size 5MB.</p>
                </div>
              </div>
            </div>
            
            <form onSubmit={handleProfileUpdate} className="space-y-8">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Bio</label>
                  <textarea
                    value={profileForm.bio}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, bio: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="Tell other traders about yourself..."
                    rows="3"
                  />
                </div>
                
                <div>
                  <label className="block text-black font-medium mb-2">Location</label>
                  <input
                    type="text"
                    value={profileForm.location}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, location: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="e.g., San Francisco, CA"
                  />
                </div>
              </div>

              {/* Twitter Settings */}
              <div className="p-6 bg-blue-50 rounded-2xl">
                <h3 className="text-lg font-semibold text-black mb-4">Twitter Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-black font-medium mb-2">Twitter Username</label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">@</span>
                      <input
                        type="text"
                        value={profileForm.twitter_username}
                        onChange={(e) => setProfileForm(prev => ({ ...prev, twitter_username: e.target.value }))}
                        className="w-full border border-gray-300 rounded-xl pl-8 pr-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                        placeholder="your_twitter_handle"
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="show_twitter"
                      checked={profileForm.show_twitter}
                      onChange={(e) => setProfileForm(prev => ({ ...prev, show_twitter: e.target.checked }))}
                      className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black focus:ring-2"
                    />
                    <label htmlFor="show_twitter" className="text-black font-medium">
                      Show Twitter account to other traders
                    </label>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  Displaying your Twitter helps other traders verify your identity and connect with you outside the platform.
                </p>
              </div>

              {/* Trading Experience */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Trading Experience</label>
                  <select
                    value={profileForm.trading_experience}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, trading_experience: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                    required
                  >
                    <option value="">Select experience level</option>
                    {EXPERIENCE_OPTIONS.map(exp => (
                      <option key={exp} value={exp}>{exp}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-black font-medium mb-2">Years Trading</label>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    value={profileForm.years_trading}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, years_trading: parseInt(e.target.value) || 0 }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="0"
                  />
                </div>
              </div>

              {/* Trading Style & Portfolio */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Trading Style</label>
                  <select
                    value={profileForm.trading_style}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, trading_style: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                    required
                  >
                    <option value="">Select trading style</option>
                    {STYLE_OPTIONS.map(style => (
                      <option key={style} value={style}>{style}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-black font-medium mb-2">Portfolio Size</label>
                  <select
                    value={profileForm.portfolio_size}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, portfolio_size: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                    required
                  >
                    <option value="">Select portfolio size</option>
                    {PORTFOLIO_OPTIONS.map(size => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Risk & Hours */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Risk Tolerance</label>
                  <select
                    value={profileForm.risk_tolerance}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, risk_tolerance: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                  >
                    <option value="">Select risk tolerance</option>
                    {RISK_OPTIONS.map(risk => (
                      <option key={risk} value={risk}>{risk}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-black font-medium mb-2">Preferred Trading Hours</label>
                  <select
                    value={profileForm.trading_hours}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, trading_hours: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                  >
                    <option value="">Select trading hours</option>
                    {HOURS_OPTIONS.map(hour => (
                      <option key={hour} value={hour}>{hour}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Communication Preferences */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Communication Style</label>
                  <select
                    value={profileForm.communication_style}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, communication_style: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                  >
                    <option value="">Select style</option>
                    {COMMUNICATION_OPTIONS.map(style => (
                      <option key={style} value={style}>{style}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-black font-medium mb-2">Preferred Communication Platform</label>
                  <select
                    value={profileForm.preferred_communication_platform}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, preferred_communication_platform: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                  >
                    <option value="">Select platform</option>
                    {COMMUNICATION_PLATFORM_OPTIONS.map(platform => (
                      <option key={platform} value={platform}>{platform}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Trading Platform */}
              <div>
                <label className="block text-black font-medium mb-2">Preferred Trading Platform</label>
                <select
                  value={profileForm.preferred_trading_platform}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, preferred_trading_platform: e.target.value }))}
                  className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                >
                  <option value="">Select trading platform</option>
                  {TRADING_PLATFORM_OPTIONS.map(platform => (
                    <option key={platform} value={platform}>{platform}</option>
                  ))}
                </select>
              </div>

              {/* Token Preferences */}
              <div>
                <label className="block text-black font-medium mb-2">Preferred Token Categories</label>
                <div className="grid grid-cols-3 gap-2">
                  {TOKEN_OPTIONS.map(token => (
                    <button
                      key={token}
                      type="button"
                      onClick={() => handleTokenToggle(token)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        profileForm.preferred_tokens.includes(token)
                          ? 'bg-black text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {token}
                    </button>
                  ))}
                </div>
              </div>

              {/* Looking For */}
              <div>
                <label className="block text-black font-medium mb-2">Looking For</label>
                <div className="grid grid-cols-3 gap-2">
                  {LOOKING_FOR_OPTIONS.map(item => (
                    <button
                      key={item}
                      type="button"
                      onClick={() => handleLookingForToggle(item)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        profileForm.looking_for.includes(item)
                          ? 'bg-black text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>

              {/* Trading Stories */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Best Trade</label>
                  <textarea
                    value={profileForm.best_trade}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, best_trade: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="Tell us about your best trade..."
                    rows="3"
                  />
                </div>

                <div>
                  <label className="block text-black font-medium mb-2">Worst Trade (Learn from mistakes)</label>
                  <textarea
                    value={profileForm.worst_trade}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, worst_trade: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="Share your biggest lesson..."
                    rows="3"
                  />
                </div>
              </div>

              {/* Favorite Project */}
              <div>
                <label className="block text-black font-medium mb-2">Favorite Project/Protocol</label>
                <input
                  type="text"
                  value={profileForm.favorite_project}
                  onChange={(e) => setProfileForm(prev => ({ ...prev, favorite_project: e.target.value }))}
                  className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                  placeholder="e.g., Jupiter, Magic Eden, Phantom..."
                />
              </div>

              <button
                type="submit"
                disabled={!profileForm.trading_experience || profileForm.preferred_tokens.length === 0 || !profileForm.trading_style || !profileForm.portfolio_size}
                className="w-full bg-black hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
              >
                {isEditing ? 'Update Profile' : 'Start Trading & Matching'}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Main App View
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-black">SolMatch</h1>
          <div className="flex space-x-4">
            <button
              onClick={() => setCurrentView('discover')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                currentView === 'discover' ? 'bg-black text-white' : 'text-gray-600 hover:text-black'
              }`}
            >
              Discover
            </button>
            <button
              onClick={() => setCurrentView('matches')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                currentView === 'matches' ? 'bg-black text-white' : 'text-gray-600 hover:text-black'
              }`}
            >
              Matches ({matches.length})
            </button>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleEditProfile}
              className="group flex items-center space-x-2 hover:bg-gray-50 px-2 py-1 rounded-lg transition-all"
              title="Click to edit profile"
            >
              <img
                src={currentUser?.avatar_url}
                alt="Profile"
                className="w-8 h-8 rounded-full border-2 border-gray-300 group-hover:border-gray-400 transition-all"
              />
              <span className="text-black font-medium group-hover:text-gray-700">{currentUser?.display_name}</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Discover View */}
      {currentView === 'discover' && (
        <div className="max-w-md mx-auto pt-8 px-4">
          {currentCardIndex < discoveryCards.length ? (
            <div className="bg-white rounded-2xl overflow-hidden shadow-lg border border-gray-200">
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
                  <div className="flex items-center space-x-2 mt-1">
                    {discoveryCards[currentCardIndex]?.show_twitter && discoveryCards[currentCardIndex]?.twitter_username && (
                      <p className="text-blue-300 text-sm">
                        🐦 @{discoveryCards[currentCardIndex]?.twitter_username}
                      </p>
                    )}
                    {discoveryCards[currentCardIndex]?.location && (
                      <p className="text-white/90 text-sm">📍 {discoveryCards[currentCardIndex]?.location}</p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <p className="text-gray-700">{discoveryCards[currentCardIndex]?.bio}</p>
                
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Experience:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {discoveryCards[currentCardIndex]?.trading_experience}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Years:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {discoveryCards[currentCardIndex]?.years_trading}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Style:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {discoveryCards[currentCardIndex]?.trading_style}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Risk:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {discoveryCards[currentCardIndex]?.risk_tolerance}
                      </span>
                    </div>
                  </div>

                  {/* Communication Preferences */}
                  {(discoveryCards[currentCardIndex]?.preferred_communication_platform || discoveryCards[currentCardIndex]?.preferred_trading_platform) && (
                    <div className="space-y-2">
                      {discoveryCards[currentCardIndex]?.preferred_communication_platform && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-500">Prefers:</span>
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                            📱 {discoveryCards[currentCardIndex]?.preferred_communication_platform}
                          </span>
                        </div>
                      )}
                      
                      {discoveryCards[currentCardIndex]?.preferred_trading_platform && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-500">Trades on:</span>
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                            ⚡ {discoveryCards[currentCardIndex]?.preferred_trading_platform}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div>
                    <span className="text-sm font-medium text-gray-500 block mb-2">Preferred Tokens:</span>
                    <div className="flex flex-wrap gap-1">
                      {discoveryCards[currentCardIndex]?.preferred_tokens.map(token => (
                        <span key={token} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                          {token}
                        </span>
                      ))}
                    </div>
                  </div>

                  {discoveryCards[currentCardIndex]?.best_trade && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-1">Best Trade:</span>
                      <p className="text-sm text-gray-700 bg-green-50 p-2 rounded-lg">
                        {discoveryCards[currentCardIndex]?.best_trade}
                      </p>
                    </div>
                  )}

                  {discoveryCards[currentCardIndex]?.looking_for?.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-2">Looking For:</span>
                      <div className="flex flex-wrap gap-1">
                        {discoveryCards[currentCardIndex]?.looking_for.map(item => (
                          <span key={item} className="bg-black text-white px-2 py-1 rounded-full text-xs">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
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
                  className="flex-1 bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  ❤️ Like
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-600 py-12">
              <h3 className="text-2xl font-bold mb-4">No more traders to discover!</h3>
              <p className="text-gray-500 mb-6">Check back later for new potential matches.</p>
              <button
                onClick={() => setCurrentView('matches')}
                className="bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
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
          <h2 className="text-3xl font-bold text-black mb-8 text-center">Your Matches</h2>
          
          {matches.length === 0 ? (
            <div className="text-center text-gray-600 py-12">
              <h3 className="text-xl font-semibold mb-4">No matches yet</h3>
              <p className="text-gray-500 mb-6">Start swiping to find your trading buddies!</p>
              <button
                onClick={() => setCurrentView('discover')}
                className="bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
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
                  className="bg-white border border-gray-200 rounded-2xl p-6 cursor-pointer hover:shadow-lg transition-all"
                >
                  <div className="flex items-center space-x-4 mb-4">
                    <img
                      src={match.other_user.avatar_url}
                      alt="Profile"
                      className="w-16 h-16 rounded-full"
                    />
                    <div>
                      <h3 className="text-black font-semibold text-lg">
                        {match.other_user.display_name}
                      </h3>
                      <div className="space-y-1">
                        {match.other_user.show_twitter && match.other_user.twitter_username && (
                          <p className="text-xs text-blue-600">
                            🐦 @{match.other_user.twitter_username}
                          </p>
                        )}
                        {match.other_user.preferred_communication_platform && (
                          <p className="text-xs text-blue-600">
                            📱 {match.other_user.preferred_communication_platform}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {match.other_user.trading_experience}
                      </span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {match.other_user.trading_style}
                      </span>
                    </div>
                    {match.other_user.preferred_trading_platform && (
                      <div className="flex items-center space-x-2">
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                          ⚡ {match.other_user.preferred_trading_platform}
                        </span>
                      </div>
                    )}
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
          <div className="bg-white border border-gray-200 rounded-2xl h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setSelectedMatch(null)}
                  className="text-gray-600 hover:text-black"
                >
                  ← Back
                </button>
                <img
                  src={selectedMatch.other_user.avatar_url}
                  alt="Profile"
                  className="w-10 h-10 rounded-full"
                />
                <div>
                  <h3 className="text-black font-semibold">
                    {selectedMatch.other_user.display_name}
                  </h3>
                  <p className="text-gray-600 text-sm">
                    {selectedMatch.other_user.trading_style} • {selectedMatch.other_user.trading_experience}
                    {selectedMatch.other_user.show_twitter && selectedMatch.other_user.twitter_username && 
                      ` • 🐦 @${selectedMatch.other_user.twitter_username}`
                    }
                    {selectedMatch.other_user.preferred_communication_platform && 
                      ` • 📱 ${selectedMatch.other_user.preferred_communication_platform}`
                    }
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
                        ? 'bg-black text-white'
                        : 'bg-gray-100 text-black'
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
            <form onSubmit={handleSendMessage} className="p-6 border-t border-gray-200">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  className="bg-black hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
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
          <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-2xl font-bold text-black mb-2">It's a Match!</h3>
            <p className="text-gray-600 mb-6">You and another trader liked each other. Start trenching together!</p>
            <button
              onClick={() => {
                setShowMatchModal(false);
                setCurrentView('matches');
              }}
              className="bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
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