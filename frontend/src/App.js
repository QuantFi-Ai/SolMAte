import React, { useState, useEffect, useRef, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import { ConnectionProvider, WalletProvider, useWallet } from '@solana/wallet-adapter-react';
import { WalletModalProvider, WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { clusterApiUrl } from '@solana/web3.js';
import PublicProfile from './PublicProfile';
import ProfileManager from './ProfileManager';
import LandingPage from './LandingPage';
import './App.css';

// Import wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Solana wallet configuration
const endpoint = clusterApiUrl('mainnet-beta');

function AppContent() {
  // Wallet setup
  const { publicKey, signMessage, connected, connect, disconnect } = useWallet();
  
  // Wallet adapters (moved inside component to avoid SSR issues)
  const wallets = useMemo(() => [
    new PhantomWalletAdapter(),
    new SolflareWalletAdapter(),
  ], []);
  // Wallet setup
  const { publicKey, signMessage, connected, connect, disconnect } = useWallet();
  
  // Wallet adapters (moved inside component to avoid SSR issues)
  const wallets = useMemo(() => [
    new PhantomWalletAdapter(),
    new SolflareWalletAdapter(),
  ], []);
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [discoveryCards, setDiscoveryCards] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [currentAiIndex, setCurrentAiIndex] = useState(0);
  const [matches, setMatches] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [discoveryMode, setDiscoveryMode] = useState('browse'); // 'browse' or 'ai'
  const [profileForm, setProfileForm] = useState({
    bio: '',
    location: '',
    timezone: '',
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
    looking_for: [],
    show_twitter: true,
    twitter_username: '',
    interested_in_token_launch: false,
    token_launch_experience: '',
    launch_timeline: '',
    launch_budget: ''
  });

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Options for profile form
  const EXPERIENCE_OPTIONS = ["Beginner", "Intermediate", "Advanced", "Expert"];
  const STYLE_OPTIONS = ["Day Trader", "Swing Trader", "HODLer", "Scalper", "Long-term Investor"];
  const PORTFOLIO_OPTIONS = ["Under $1K", "$1K-$10K", "$10K-$100K", "$100K+", "Prefer not to say"];
  const RISK_OPTIONS = ["Conservative", "Moderate", "Aggressive", "YOLO"];
  const HOURS_OPTIONS = ["Early Morning", "Morning", "Afternoon", "Evening", "Night Owl", "24/7"];
  const COMMUNICATION_OPTIONS = ["Casual", "Professional", "Technical", "Friendly"];
  const COMMUNICATION_PLATFORM_OPTIONS = ["Discord", "Telegram", "Twitter DM", "Signal", "WhatsApp", "In-App Only"];
  const TRADING_PLATFORM_OPTIONS = ["Axiom", "BullX", "Photon", "Padre", "Jupiter", "Raydium", "Magic Eden", "Other"];
  const TOKEN_OPTIONS = ["Meme Coins", "DeFi", "GameFi", "NFTs", "Blue Chips", "Layer 1s"];
  const LOOKING_FOR_OPTIONS = ["Learning", "Teaching", "Alpha Sharing", "Research Partner", "Risk Management", "Networking"];

  // Token Launch Options
  const TOKEN_LAUNCH_EXPERIENCE_OPTIONS = ["None", "Beginner", "Experienced", "Expert"];
  const LAUNCH_TIMELINE_OPTIONS = ["Immediate", "1-3 months", "3-6 months", "6+ months", "Just researching"];
  const LAUNCH_BUDGET_OPTIONS = ["Under $10K", "$10K-$50K", "$50K-$100K", "$100K+", "Prefer not to say"];
  const PROJECT_TYPE_OPTIONS = ["Meme Coin", "Utility Token", "DeFi Protocol", "GameFi", "NFT Project", "Other"];
  const HELP_WITH_OPTIONS = ["Technical Development", "Marketing", "Community Building", "Funding", "Legal/Compliance"];

  // Timezone options (popular ones)
  const TIMEZONE_OPTIONS = [
    "UTC",
    "America/New_York",
    "America/Chicago", 
    "America/Denver",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Dubai",
    "Australia/Sydney",
    "Australia/Melbourne"
  ];

  const [showProfileManager, setShowProfileManager] = useState(false);
  
  // User status management
  const [userStatus, setUserStatus] = useState('offline'); // 'active' or 'offline'
  const [showOnlyActive, setShowOnlyActive] = useState(false);
  
  // Token launch features
  const [showTokenLaunchForm, setShowTokenLaunchForm] = useState(false);
  const [tokenLaunchProfile, setTokenLaunchProfile] = useState({
    interested_in_token_launch: false,
    token_launch_experience: '',
    launch_timeline: '',
    launch_budget: '',
    project_type: '',
    looking_for_help_with: []
  });
  
  // Email/Password Authentication
  const [authMode, setAuthMode] = useState('signin'); // 'signin', 'signup', 'wallet'
  const [emailForm, setEmailForm] = useState({
    email: '',
    password: '',
    display_name: ''
  });
  const [authLoading, setAuthLoading] = useState(false);

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
      
      // Fetch user status
      const statusResponse = await fetch(`${API_BASE_URL}/api/user-status/${userId}`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setUserStatus(statusData.user_status);
      }
      
      // Update user's last activity
      await fetch(`${API_BASE_URL}/api/user/${userId}/update-activity`, {
        method: 'POST'
      });
      
      // Check if profile is complete
      if (!user.profile_complete) {
        setProfileForm({
          display_name: user.display_name || '',
          bio: user.bio || '',
          location: user.location || '',
          timezone: user.timezone || '',
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
          looking_for: user.looking_for || [],
          show_twitter: user.show_twitter !== undefined ? user.show_twitter : true,
          twitter_username: user.twitter_username || '',
          interested_in_token_launch: user.interested_in_token_launch || false,
          token_launch_experience: user.token_launch_experience || '',
          launch_timeline: user.launch_timeline || '',
          launch_budget: user.launch_budget || ''
        });
        setCurrentView('profile-setup');
      } else {
        setCurrentView('discover');
        fetchDiscoveryCards();
        fetchAiRecommendations();
        fetchMatches();
      }
      
      // Fetch token launch profile if user is interested
      if (user.interested_in_token_launch) {
        const tokenResponse = await fetch(`${API_BASE_URL}/api/token-launch-profile/${userId}`);
        if (tokenResponse.ok) {
          const tokenData = await tokenResponse.json();
          setTokenLaunchProfile(tokenData);
        }
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  // Handle user status toggle
  const handleStatusToggle = async () => {
    if (!currentUser) return;
    
    const newStatus = userStatus === 'active' ? 'offline' : 'active';
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/user-status/${currentUser.user_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_status: newStatus })
      });
      
      if (response.ok) {
        setUserStatus(newStatus);
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  // Filter cards based on active status
  const filterCardsByStatus = (cards) => {
    if (!showOnlyActive) return cards;
    return cards.filter(card => card.user_status === 'active');
  };

  const fetchDiscoveryCards = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/discover/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setDiscoveryCards(filterCardsByStatus(data.potential_matches || []));
      }
    } catch (error) {
      console.error('Error fetching discovery cards:', error);
    }
  };

  const fetchAiRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai-matches/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setAiRecommendations(filterCardsByStatus(data.ai_matches || []));
      }
    } catch (error) {
      console.error('Error fetching AI recommendations:', error);
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
      
      console.log('Demo user created:', demoUser); // Debug log
      
      setCurrentUser(demoUser);
      setProfileForm({
        display_name: demoUser.display_name || '',
        bio: demoUser.bio || '',
        location: demoUser.location || '',
        timezone: demoUser.timezone || '',
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
        looking_for: demoUser.looking_for || [],
        interested_in_token_launch: demoUser.interested_in_token_launch || false,
        token_launch_experience: demoUser.token_launch_experience || '',
        launch_timeline: demoUser.launch_timeline || '',
        launch_budget: demoUser.launch_budget || ''
      });
      setCurrentView('profile-setup');
    } catch (error) {
      console.error('Error creating demo user:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Debug: Check current user state
    console.log('Current user during upload:', currentUser);

    // Check if user is logged in (less strict check)
    if (!currentUser?.user_id) {
      console.error('Upload failed - user not authenticated:', { currentUser, user_id: currentUser?.user_id });
      alert('Please complete login/registration first before uploading a profile picture');
      return;
    }

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

  const handleSwipe = async (action, isAiRecommendation = false) => {
    const currentCards = isAiRecommendation ? aiRecommendations : discoveryCards;
    const currentIndex = isAiRecommendation ? currentAiIndex : currentCardIndex;
    
    if (currentIndex >= currentCards.length) return;
    
    const currentCard = currentCards[currentIndex];
    
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
      
      if (isAiRecommendation) {
        setCurrentAiIndex(prev => prev + 1);
      } else {
        setCurrentCardIndex(prev => prev + 1);
      }
      
      // Load more cards if running low
      if (currentIndex >= currentCards.length - 2) {
        if (isAiRecommendation) {
          fetchAiRecommendations();
        } else {
          fetchDiscoveryCards();
        }
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
        fetchAiRecommendations();
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

  // Get current card data based on discovery mode
  const getCurrentCard = () => {
    if (discoveryMode === 'ai') {
      return aiRecommendations[currentAiIndex];
    } else {
      return discoveryCards[currentCardIndex];
    }
  };

  const getCurrentIndex = () => {
    return discoveryMode === 'ai' ? currentAiIndex : currentCardIndex;
  };

  const getCurrentCards = () => {
    return discoveryMode === 'ai' ? aiRecommendations : discoveryCards;
  };

  // Redirect to login if not authenticated
  if (!currentUser && currentView !== 'login') {
    setCurrentView('login');
    return null;
  }

  // Login View
  if (currentView === 'login') {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white border border-gray-200 rounded-2xl p-8 shadow-lg">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-black mb-2">Solm8</h1>
            <p className="text-gray-600">Connect with like-minded Solana traders</p>
          </div>
          
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-black mb-4">Join the Trading Community</h2>
              <p className="text-gray-700 mb-6">Connect, collaborate, and profit together</p>
              
              {/* Sign Up Section */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-800 mb-3">New to Solm8?</h3>
                <button
                  onClick={handleTwitterLogin}
                  className="w-full bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 mb-3"
                >
                  <span>🐦</span>
                  <span>Sign Up with Twitter</span>
                </button>
                <button
                  onClick={handleDemoLogin}
                  className="w-full border border-gray-300 hover:bg-gray-50 text-black font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <span>🎮</span>
                  <span>Try Demo Account</span>
                </button>
              </div>

              {/* Divider */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Already have an account?</span>
                </div>
              </div>

              {/* Login Section */}
              <div>
                <h3 className="text-sm font-medium text-gray-800 mb-3">Welcome back!</h3>
                <button
                  onClick={handleTwitterLogin}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <span>🐦</span>
                  <span>Sign In with Twitter</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Profile Setup/Edit View (keeping same as before)
  if ((currentView === 'profile-setup' || currentView === 'profile-edit') && currentUser) {
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
              {/* Same form content as before - all the profile fields */}
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-black font-medium mb-2">Display Name</label>
                  <input
                    type="text"
                    value={profileForm.display_name}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, display_name: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="Your display name"
                  />
                </div>
                
                <div>
                  <label className="block text-black font-medium mb-2">Timezone</label>
                  <select
                    value={profileForm.timezone}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, timezone: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black bg-white focus:ring-2 focus:ring-black focus:border-transparent"
                  >
                    <option value="">Select your timezone</option>
                    {TIMEZONE_OPTIONS.map(tz => (
                      <option key={tz} value={tz}>{tz.replace('_', ' ')}</option>
                    ))}
                  </select>
                </div>
              </div>

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

              {/* Token Launch Interest */}
              <div className="p-6 bg-blue-50 rounded-2xl">
                <h3 className="text-lg font-semibold text-black mb-4">Token Launch & Project Interest</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="interested_in_token_launch"
                      checked={profileForm.interested_in_token_launch}
                      onChange={(e) => setProfileForm(prev => ({ ...prev, interested_in_token_launch: e.target.checked }))}
                      className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black focus:ring-2"
                    />
                    <label htmlFor="interested_in_token_launch" className="text-black font-medium">
                      I'm interested in launching a token or crypto project
                    </label>
                  </div>
                  
                  {profileForm.interested_in_token_launch && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
                        <select
                          value={profileForm.token_launch_experience}
                          onChange={(e) => setProfileForm(prev => ({ ...prev, token_launch_experience: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                        >
                          <option value="">Select experience</option>
                          {TOKEN_LAUNCH_EXPERIENCE_OPTIONS.map(exp => (
                            <option key={exp} value={exp}>{exp}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Timeline</label>
                        <select
                          value={profileForm.launch_timeline}
                          onChange={(e) => setProfileForm(prev => ({ ...prev, launch_timeline: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                        >
                          <option value="">Select timeline</option>
                          {LAUNCH_TIMELINE_OPTIONS.map(timeline => (
                            <option key={timeline} value={timeline}>{timeline}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Budget</label>
                        <select
                          value={profileForm.launch_budget}
                          onChange={(e) => setProfileForm(prev => ({ ...prev, launch_budget: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                        >
                          <option value="">Select budget</option>
                          {LAUNCH_BUDGET_OPTIONS.map(budget => (
                            <option key={budget} value={budget}>{budget}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  Connect with traders interested in early projects, find collaborators, and discover investment opportunities.
                </p>
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
          <h1 className="text-2xl font-bold text-black">Solm8</h1>
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
            <button
              onClick={() => setShowProfileManager(true)}
              className="px-4 py-2 rounded-lg font-medium text-gray-600 hover:text-black transition-all"
            >
              📱 Share Profile
            </button>
          </div>
          <div className="flex items-center space-x-3">
            {/* Status Toggle */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handleStatusToggle}
                className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium transition-all ${
                  userStatus === 'active' 
                    ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title={`Currently ${userStatus} - Click to ${userStatus === 'active' ? 'go offline' : 'go active'}`}
              >
                <div className={`w-2 h-2 rounded-full ${
                  userStatus === 'active' ? 'bg-green-500' : 'bg-gray-400'
                }`}></div>
                <span>{userStatus === 'active' ? 'Trading Active' : 'Offline'}</span>
              </button>
            </div>
            
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
          {/* Discovery Mode Toggle */}
          <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
            <button
              onClick={() => setDiscoveryMode('browse')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                discoveryMode === 'browse' 
                  ? 'bg-white text-black shadow-sm' 
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              Browse Traders
            </button>
            <button
              onClick={() => setDiscoveryMode('ai')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                discoveryMode === 'ai' 
                  ? 'bg-white text-black shadow-sm' 
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              💡 Best Matches
            </button>
          </div>

          {/* Active Users Filter */}
          <div className="flex items-center justify-between mb-6 p-3 bg-white rounded-lg border border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Show only active traders</span>
            </div>
            <button
              onClick={() => {
                setShowOnlyActive(!showOnlyActive);
                // Refresh cards with new filter
                if (discoveryMode === 'browse') {
                  fetchDiscoveryCards();
                } else {
                  fetchAiRecommendations();
                }
              }}
              className={`w-12 h-6 rounded-full transition-all duration-200 focus:outline-none ${
                showOnlyActive ? 'bg-green-500' : 'bg-gray-300'
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform duration-200 ${
                showOnlyActive ? 'translate-x-6' : 'translate-x-0.5'
              }`}></div>
            </button>
          </div>

          {getCurrentIndex() < getCurrentCards().length ? (
            <div className="bg-white rounded-2xl overflow-hidden shadow-lg border border-gray-200">
              {/* AI Compatibility Banner */}
              {discoveryMode === 'ai' && getCurrentCard()?.ai_compatibility && (
                <div className="bg-gradient-to-r from-blue-500 to-green-600 text-white p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Match Score</span>
                    <span className="text-2xl font-bold">
                      {getCurrentCard().ai_compatibility.compatibility_percentage}%
                    </span>
                  </div>
                  <div className="space-y-1">
                    {getCurrentCard().ai_compatibility.recommendations.map((rec, idx) => (
                      <p key={idx} className="text-xs text-blue-100">{rec}</p>
                    ))}
                  </div>
                </div>
              )}

              <div className="relative">
                <img
                  src={getCurrentCard()?.avatar_url}
                  alt="Profile"
                  className="w-full h-96 object-cover"
                />
                {/* Status Indicator */}
                {getCurrentCard()?.user_status === 'active' && (
                  <div className="absolute top-4 right-4 flex items-center space-x-1 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                    <span>Trading Now</span>
                  </div>
                )}
                {getCurrentCard()?.timezone && (
                  <div className="absolute top-4 left-4 bg-black/70 text-white px-2 py-1 rounded text-xs">
                    🌍 {getCurrentCard().timezone.replace('_', ' ')}
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                  <h3 className="text-2xl font-bold text-white">
                    {getCurrentCard()?.display_name}
                  </h3>
                  <div className="flex items-center space-x-2 mt-1">
                    {getCurrentCard()?.show_twitter && getCurrentCard()?.twitter_username && (
                      <p className="text-blue-300 text-sm">
                        🐦 @{getCurrentCard()?.twitter_username}
                      </p>
                    )}
                    {getCurrentCard()?.location && (
                      <p className="text-white/90 text-sm">📍 {getCurrentCard()?.location}</p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <p className="text-gray-700">{getCurrentCard()?.bio}</p>
                
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Experience:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {getCurrentCard()?.trading_experience}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Years:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {getCurrentCard()?.years_trading}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Style:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {getCurrentCard()?.trading_style}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Risk:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {getCurrentCard()?.risk_tolerance}
                      </span>
                    </div>
                  </div>

                  {/* Communication Preferences */}
                  {(getCurrentCard()?.preferred_communication_platform || getCurrentCard()?.preferred_trading_platform) && (
                    <div className="space-y-2">
                      {getCurrentCard()?.preferred_communication_platform && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-500">Prefers:</span>
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                            📱 {getCurrentCard()?.preferred_communication_platform}
                          </span>
                        </div>
                      )}
                      
                      {getCurrentCard()?.preferred_trading_platform && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-500">Trades on:</span>
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                            ⚡ {getCurrentCard()?.preferred_trading_platform}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div>
                    <span className="text-sm font-medium text-gray-500 block mb-2">Preferred Tokens:</span>
                    <div className="flex flex-wrap gap-1">
                      {getCurrentCard()?.preferred_tokens.map(token => (
                        <span key={token} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                          {token}
                        </span>
                      ))}
                    </div>
                  </div>

                  {getCurrentCard()?.best_trade && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-1">Best Trade:</span>
                      <p className="text-sm text-gray-700 bg-green-50 p-2 rounded-lg">
                        {getCurrentCard()?.best_trade}
                      </p>
                    </div>
                  )}

                  {getCurrentCard()?.looking_for?.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-2">Looking For:</span>
                      <div className="flex flex-wrap gap-1">
                        {getCurrentCard()?.looking_for.map(item => (
                          <span key={item} className="bg-black text-white px-2 py-1 rounded-full text-xs">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Token Launch Interest */}
                  {getCurrentCard()?.interested_in_token_launch && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-2">Project Interest:</span>
                      <div className="flex flex-wrap gap-1">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                          💰 Project Builder
                        </span>
                        {getCurrentCard()?.token_launch_experience && (
                          <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-xs">
                            {getCurrentCard().token_launch_experience} Experience
                          </span>
                        )}
                        {getCurrentCard()?.launch_timeline && (
                          <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-xs">
                            Timeline: {getCurrentCard().launch_timeline}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* AI Compatibility Details */}
                  {discoveryMode === 'ai' && getCurrentCard()?.ai_compatibility && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <span className="text-sm font-medium text-blue-800 block mb-2">
                        Why This Is A Good Match:
                      </span>
                      <div className="space-y-1">
                        {Object.entries(getCurrentCard().ai_compatibility.breakdown).map(([key, value]) => (
                          <div key={key} className="text-xs text-blue-700">
                            <span className="capitalize font-medium">{key}:</span> {value.reason}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex space-x-4 p-6 pt-0">
                <button
                  onClick={() => handleSwipe('pass', discoveryMode === 'ai')}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  ❌ Pass
                </button>
                <button
                  onClick={() => handleSwipe('like', discoveryMode === 'ai')}
                  className="flex-1 bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  ❤️ Like
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-600 py-12">
              <h3 className="text-2xl font-bold mb-4">
                No more {discoveryMode === 'ai' ? 'recommended matches' : 'traders to discover'}!
              </h3>
              <p className="text-gray-500 mb-6">
                {discoveryMode === 'ai' 
                  ? 'Try browsing all traders or check back later for new recommendations.'
                  : 'Check back later for new potential trading partners.'
                }
              </p>
              <div className="space-x-4">
                {discoveryMode === 'ai' && (
                  <button
                    onClick={() => setDiscoveryMode('browse')}
                    className="bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                  >
                    Browse All Traders
                  </button>
                )}
                <button
                  onClick={() => setCurrentView('matches')}
                  className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  View Your Matches
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Matches View and Chat View remain the same */}
      {/* Matches View */}
      {currentView === 'matches' && !selectedMatch && (
        <div className="max-w-4xl mx-auto pt-8 px-4">
          <h2 className="text-3xl font-bold text-black mb-8 text-center">Your Matches</h2>
          
          {matches.length === 0 ? (
            <div className="text-center text-gray-600 py-12">
              <h3 className="text-xl font-semibold mb-4">No trading connections yet</h3>
              <p className="text-gray-500 mb-6">Start connecting with fellow traders to build your network!</p>
              <button
                onClick={() => setCurrentView('discover')}
                className="bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
              >
                Start Connecting
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
                  className="bg-white border border-gray-200 rounded-2xl p-6 cursor-pointer hover:shadow-lg transition-all relative"
                >
                  {/* Status Indicator */}
                  {match.other_user.user_status === 'active' && (
                    <div className="absolute top-3 right-3 flex items-center space-x-1 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                      <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                      <span>Trading Now</span>
                    </div>
                  )}
                  
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
                        {match.other_user.timezone && (
                          <p className="text-xs text-gray-500">
                            🌍 {match.other_user.timezone.replace('_', ' ')}
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
                    {match.other_user.interested_in_token_launch && (
                      <div className="flex items-center space-x-2">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                          💰 Project Builder
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

      {/* Profile Manager Modal */}
      {showProfileManager && (
        <ProfileManager
          currentUser={currentUser}
          onClose={() => setShowProfileManager(false)}
        />
      )}

      {/* Match Modal */}
      {showMatchModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center">
            <div className="text-6xl mb-4">🤝</div>
            <h3 className="text-2xl font-bold text-black mb-2">New Trading Connection!</h3>
            <p className="text-gray-600 mb-6">You and another trader are interested in connecting. Start building your trading network!</p>
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

// Main App Component with Router
const AppWithRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<App />} />
        <Route path="/profile/:username" element={<PublicProfile />} />
      </Routes>
    </Router>
  );
};

export default AppWithRouter;