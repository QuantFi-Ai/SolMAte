import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import PublicProfile from './PublicProfile';
import ProfileManager from './ProfileManager';
import LandingPage from './LandingPage';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Solana wallet configuration
function AppContent() {
  // State management
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [discoveryCards, setDiscoveryCards] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [currentAiIndex, setCurrentAiIndex] = useState(0);
  const [matches, setMatches] = useState([]);
  const [matchesWithMessages, setMatchesWithMessages] = useState([]);
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

  // Profile dropdown state
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  
  // Profile popup modal state
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const [selectedProfileUser, setSelectedProfileUser] = useState(null);

  // Validate session with backend
  const validateSession = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/${userData.user_id}`);
      if (response.ok) {
        const currentUserData = await response.json();
        // Update localStorage with latest user data
        localStorage.setItem('solm8_user', JSON.stringify(currentUserData));
        return currentUserData;
      } else {
        // User no longer exists on backend, clear session
        localStorage.removeItem('solm8_user');
        return null;
      }
    } catch (error) {
      console.error('Session validation failed:', error);
      return userData; // Fallback to stored data if network fails
    }
  };

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem('solm8_user');
    setCurrentUser(null);
    setCurrentView('login');
    setUserStatus('offline');
    setShowProfileDropdown(false);
    // Close WebSocket if open
    if (ws) {
      ws.close();
      setWs(null);
    }
  };

  // Handle auth callback and session restoration on page load
  useEffect(() => {
    // First, check for stored user session
    const storedUser = localStorage.getItem('solm8_user');
    if (storedUser && !currentUser) {
      try {
        const userData = JSON.parse(storedUser);
        console.log('Restoring user session:', userData);
        
        // Validate session with backend
        validateSession(userData).then((validatedUser) => {
          if (validatedUser) {
            setCurrentUser(validatedUser);
            
            // Update user activity
            fetch(`${API_BASE_URL}/api/user/${validatedUser.user_id}/update-activity`, {
              method: 'POST'
            }).catch(err => console.error('Failed to update activity:', err));
            
            // Set appropriate view based on profile completion
            if (!validatedUser.profile_complete) {
              setCurrentView('profile-setup');
            } else {
              setCurrentView('discover');
              console.log('🔄 Session restored, fetching data...');
              fetchDiscoveryCards(validatedUser);
              fetchAiRecommendations(validatedUser);
              fetchMatches(validatedUser);
              fetchMatchesWithMessages(validatedUser);
            }
          } else {
            // Invalid session, go to login
            setCurrentView('login');
          }
        });
        
        return; // Don't process URL params if we restored session
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('solm8_user');
        setCurrentView('login');
      }
    }

    // Then check for auth callback URL params
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_success') === 'true') {
      const userId = urlParams.get('user_id');
      
      if (userId) {
        fetchUserProfile(userId);
      }
    } else if (urlParams.get('auth_error') === 'true') {
      alert('Authentication failed. Please try again.');
    }
  }, []);

  // Setup WebSocket when user is logged in (disabled for now - using HTTP polling)
  useEffect(() => {
    // WebSocket functionality disabled - using HTTP polling for chat instead
    // This prevents connection errors while keeping chat functional
    return () => {
      if (ws) {
        ws.close();
        setWs(null);
      }
    };
  }, [currentUser, ws]);

  // Auto-refresh messages and unread counts
  useEffect(() => {
    let messagePolling;
    
    if (currentView === 'chat' && selectedMatch) {
      // Poll for new messages every 3 seconds when in chat
      messagePolling = setInterval(() => {
        fetchMessages(selectedMatch.match_id);
      }, 3000);
    } else if (currentView === 'messages') {
      // Poll for unread count updates every 5 seconds when in Messages view
      messagePolling = setInterval(() => {
        fetchMatchesWithMessages();
      }, 5000);
    }
    
    return () => {
      if (messagePolling) {
        clearInterval(messagePolling);
      }
    };
  }, [currentView, selectedMatch]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showProfileDropdown && !event.target.closest('.profile-dropdown')) {
        setShowProfileDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showProfileDropdown]);

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

  // Email/Password Authentication Functions
  const handleEmailSignup = async (e) => {
    e.preventDefault();
    if (!emailForm.email || !emailForm.password || !emailForm.display_name) {
      alert('Please fill in all fields');
      return;
    }
    
    setAuthLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/email/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailForm)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }
      
      const data = await response.json();
      setCurrentUser(data.user);
      setCurrentView('profile-setup');
      setEmailForm({ email: '', password: '', display_name: '' });
      
      // Save user session to localStorage
      localStorage.setItem('solm8_user', JSON.stringify(data.user));
      
    } catch (error) {
      console.error('Signup error:', error);
      alert(error.message || 'Signup failed. Please try again.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    if (!emailForm.email || !emailForm.password) {
      alert('Please enter email and password');
      return;
    }
    
    setAuthLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/email/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: emailForm.email,
          password: emailForm.password
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }
      
      const data = await response.json();
      setCurrentUser(data.user);
      setEmailForm({ email: '', password: '', display_name: '' });
      
      // Save user session to localStorage
      localStorage.setItem('solm8_user', JSON.stringify(data.user));
      
      // Check if profile is complete
      if (!data.user.profile_complete) {
        setCurrentView('profile-setup');
      } else {
        setCurrentView('discover');
      }
      
    } catch (error) {
      console.error('Login error:', error);
      alert(error.message || 'Login failed. Please check your credentials.');
    } finally {
      setAuthLoading(false);
    }
  };

  // Temporary wallet connect placeholder
  const handleWalletConnect = async () => {
    alert('Wallet authentication coming soon! Please use email/password for now.');
  };

  const fetchDiscoveryCards = async (user = currentUser) => {
    if (!user) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/discover/${user.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setDiscoveryCards(filterCardsByStatus(data || []));
      }
    } catch (error) {
      console.error('Error fetching discovery cards:', error);
    }
  };

  const fetchAiRecommendations = async (user = currentUser) => {
    if (!user) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai-recommendations/${user.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setAiRecommendations(filterCardsByStatus(data || []));
      }
    } catch (error) {
      console.error('Error fetching AI recommendations:', error);
    }
  };

  const fetchMatches = async (user = currentUser) => {
    if (!user) return;
    try {
      console.log('🔍 Fetching matches for user:', user.user_id);
      const response = await fetch(`${API_BASE_URL}/api/matches/${user.user_id}`);
      console.log('📡 Matches response status:', response.status);
      const matchesData = await response.json();
      console.log('📊 Matches data received:', matchesData);
      setMatches(matchesData);
      console.log('✅ Matches state updated, count:', matchesData.length);
    } catch (error) {
      console.error('❌ Error fetching matches:', error);
    }
  };

  const fetchMatchesWithMessages = async (user = currentUser) => {
    if (!user) return;
    try {
      console.log('💬 Fetching matches with messages for user:', user.user_id);
      const response = await fetch(`${API_BASE_URL}/api/matches-with-messages/${user.user_id}`);
      if (response.ok) {
        const matchesData = await response.json();
        console.log('📧 Matches with messages data received:', matchesData.length, 'matches');
        setMatchesWithMessages(matchesData);
      }
    } catch (error) {
      console.error('❌ Error fetching matches with messages:', error);
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

  const markMessagesAsRead = async (matchId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/messages/${matchId}/mark-read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: currentUser.user_id })
      });
      
      if (response.ok) {
        // Refresh matches with messages to update unread counts
        fetchMatchesWithMessages();
      }
    } catch (error) {
      console.error('Error marking messages as read:', error);
    }
  };

  const openChatAndMarkRead = async (match) => {
    setSelectedMatch(match);
    setCurrentView('chat');
    
    // Fetch messages and mark as read
    await fetchMessages(match.match_id);
    await markMessagesAsRead(match.match_id);
  };

  const showUserProfile = (user) => {
    setSelectedProfileUser(user);
    setShowProfilePopup(true);
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
      
      // Update localStorage
      localStorage.setItem('solm8_user', JSON.stringify({ ...currentUser, ...profileForm, profile_complete: true }));
      
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
    setShowProfileDropdown(false);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedMatch) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          match_id: selectedMatch.match_id,
          sender_id: currentUser.user_id,
          content: newMessage.trim()
        })
      });
      
      if (response.ok) {
        // Refresh messages
        fetchMessages(selectedMatch.match_id);
        setNewMessage('');
      } else {
        console.error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
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

  // Redirect to login if not authenticated (but don't interfere with session restoration)
  if (!currentUser && currentView !== 'login') {
    // Give session restoration a moment to work
    setTimeout(() => {
      if (!currentUser) {
        setCurrentView('login');
      }
    }, 100);
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
            {/* Authentication Mode Toggle */}
            <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
              <button
                onClick={() => setAuthMode('signin')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                  authMode === 'signin' 
                    ? 'bg-white text-black shadow-sm' 
                    : 'text-gray-600 hover:text-black'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setAuthMode('signup')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                  authMode === 'signup' 
                    ? 'bg-white text-black shadow-sm' 
                    : 'text-gray-600 hover:text-black'
                }`}
              >
                Sign Up
              </button>
            </div>

            {/* Email/Password Forms */}
            {(authMode === 'signin' || authMode === 'signup') && (
              <form onSubmit={authMode === 'signup' ? handleEmailSignup : handleEmailLogin} className="space-y-4">
                {authMode === 'signup' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
                    <input
                      type="text"
                      value={emailForm.display_name}
                      onChange={(e) => setEmailForm(prev => ({ ...prev, display_name: e.target.value }))}
                      className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent"
                      placeholder="Your trading name"
                      required
                    />
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={emailForm.email}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="trader@example.com"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input
                    type="password"
                    value={emailForm.password}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, password: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="••••••••"
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 disabled:opacity-50"
                >
                  {authLoading ? 'Please wait...' : (authMode === 'signup' ? 'Create Account' : 'Sign In')}
                </button>
              </form>
            )}
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
              onClick={() => {
                setCurrentView('messages');
                fetchMatchesWithMessages();
              }}
              className={`px-4 py-2 rounded-lg font-medium transition-all relative ${
                currentView === 'messages' ? 'bg-black text-white' : 'text-gray-600 hover:text-black'
              }`}
            >
              Messages
              {matchesWithMessages.length > 0 && matchesWithMessages.reduce((total, match) => total + match.unread_count, 0) > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {matchesWithMessages.reduce((total, match) => total + match.unread_count, 0)}
                </span>
              )}
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
                <span>{userStatus === 'active' ? 'Active' : 'Offline'}</span>
              </button>
            </div>
            
            {/* Profile Dropdown */}
            <div className="relative profile-dropdown">
              <button
                onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                className="group flex items-center space-x-2 hover:bg-gray-50 px-2 py-1 rounded-lg transition-all"
                title="Profile menu"
              >
                <img
                  src={currentUser?.avatar_url}
                  alt="Profile"
                  className="w-8 h-8 rounded-full border-2 border-gray-300 group-hover:border-gray-400 transition-all"
                />
                <span className="text-black font-medium group-hover:text-gray-700">{currentUser?.display_name}</span>
                <svg className={`w-4 h-4 transition-transform ${showProfileDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Dropdown Menu */}
              {showProfileDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <button
                    onClick={handleEditProfile}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <span>Edit Profile</span>
                  </button>
                  
                  <button
                    onClick={() => {
                      setShowProfileManager(true);
                      setShowProfileDropdown(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                    </svg>
                    <span>Share Profile</span>
                  </button>
                  
                  <div className="border-t border-gray-100 my-1"></div>
                  
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
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
              🤖 AI Matches
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
                      <span className="text-sm font-medium text-gray-500">Portfolio:</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                        💰 {getCurrentCard()?.portfolio_size}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Risk:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        {getCurrentCard()?.risk_tolerance}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Hours:</span>
                      <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                        🕐 {getCurrentCard()?.trading_hours}
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
                      {getCurrentCard()?.preferred_tokens?.map((token, idx) => (
                        <span key={idx} className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
                          {token}
                        </span>
                      ))}
                    </div>
                  </div>

                  {getCurrentCard()?.looking_for && getCurrentCard()?.looking_for?.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-2">Looking For:</span>
                      <div className="flex flex-wrap gap-1">
                        {getCurrentCard()?.looking_for?.map((item, idx) => (
                          <span key={idx} className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Best Trade Preview */}
                  {getCurrentCard()?.best_trade && (
                    <div>
                      <span className="text-sm font-medium text-green-600 block mb-1">💰 Best Trade:</span>
                      <p className="text-xs text-gray-600 bg-green-50 p-2 rounded line-clamp-2">
                        {getCurrentCard()?.best_trade.substring(0, 120)}
                        {getCurrentCard()?.best_trade.length > 120 ? '...' : ''}
                      </p>
                    </div>
                  )}

                  {/* Best Trade Preview */}
                  {getCurrentCard()?.best_trade && (
                    <div>
                      <span className="text-sm font-medium text-green-600 block mb-1">💰 Best Trade:</span>
                      <p className="text-xs text-gray-600 bg-green-50 p-2 rounded line-clamp-2">
                        {getCurrentCard()?.best_trade.substring(0, 120)}
                        {getCurrentCard()?.best_trade.length > 120 ? '...' : ''}
                      </p>
                    </div>
                  )}

                  {/* Trading Stories */}
                  {(getCurrentCard()?.best_trade || getCurrentCard()?.worst_trade) && (
                    <div className="space-y-2">
                      {getCurrentCard()?.best_trade && (
                        <div>
                          <span className="text-sm font-medium text-green-600 block mb-1">💰 Best Trade:</span>
                          <p className="text-xs text-gray-600 bg-green-50 p-2 rounded">{getCurrentCard()?.best_trade}</p>
                        </div>
                      )}
                      
                      {getCurrentCard()?.worst_trade && (
                        <div>
                          <span className="text-sm font-medium text-red-600 block mb-1">📉 Learning Experience:</span>
                          <p className="text-xs text-gray-600 bg-red-50 p-2 rounded">{getCurrentCard()?.worst_trade}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {getCurrentCard()?.favorite_project && (
                    <div>
                      <span className="text-sm font-medium text-gray-500 block mb-1">❤️ Favorite Project:</span>
                      <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded">{getCurrentCard()?.favorite_project}</p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex space-x-4 p-6 pt-0">
                <button
                  onClick={() => handleSwipe('pass', discoveryMode === 'ai')}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <span>👎</span>
                  <span>Pass</span>
                </button>
                <button
                  onClick={() => handleSwipe('like', discoveryMode === 'ai')}
                  className="flex-1 bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <span>👍</span>
                  <span>Like</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-8 text-center shadow-lg border border-gray-200">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-black mb-2">No More Traders</h3>
              <p className="text-gray-600 mb-4">
                {discoveryMode === 'ai' 
                  ? "You've seen all your AI-matched traders. Try browsing all traders or come back later for new members!"
                  : "You've seen all available traders. Come back later for new members!"
                }
              </p>
              <button
                onClick={() => {
                  if (discoveryMode === 'ai') {
                    setDiscoveryMode('browse');
                  } else {
                    setCurrentCardIndex(0);
                    setCurrentAiIndex(0);
                    fetchDiscoveryCards();
                    fetchAiRecommendations();
                  }
                }}
                className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-4 rounded-lg transition-all"
              >
                {discoveryMode === 'ai' ? 'Browse All Traders' : 'Refresh'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Matches View */}
      {currentView === 'matches' && (
        <div className="max-w-4xl mx-auto pt-8 px-4">
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <h2 className="text-2xl font-bold text-black mb-6">Your Matches</h2>
            
            {matches.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">💫</div>
                <h3 className="text-xl font-bold text-black mb-2">No Matches Yet</h3>
                <p className="text-gray-600 mb-4">Start swiping to find your trading partners!</p>
                <button
                  onClick={() => setCurrentView('discover')}
                  className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-4 rounded-lg transition-all"
                >
                  Start Discovering
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {matches.map((match) => (
                  <div key={match.match_id} className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all">
                    <div className="flex items-center space-x-3 mb-3">
                      <img
                        src={match.other_user.avatar_url}
                        alt="Match"
                        className="w-12 h-12 rounded-full object-cover"
                      />
                      <div>
                        <h3 className="font-semibold text-black">{match.other_user.display_name}</h3>
                        <p className="text-sm text-gray-500">
                          {match.other_user.trading_experience} • {match.other_user.trading_style}
                        </p>
                      </div>
                    </div>
                    
                    {match.other_user.bio && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">{match.other_user.bio}</p>
                    )}
                    
                    <div className="flex space-x-2 mb-3">
                      {match.other_user.preferred_tokens?.slice(0, 2).map((token, idx) => (
                        <span key={idx} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                          {token}
                        </span>
                      ))}
                      {match.other_user.preferred_tokens?.length > 2 && (
                        <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                          +{match.other_user.preferred_tokens.length - 2}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => showUserProfile(match.other_user)}
                        className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg transition-all"
                      >
                        👤 View Profile
                      </button>
                      <button
                        onClick={() => {
                          setSelectedMatch(match);
                          fetchMessages(match.match_id);
                          setCurrentView('chat');
                        }}
                        className="flex-1 bg-black hover:bg-gray-800 text-white font-medium py-2 px-4 rounded-lg transition-all"
                      >
                        💬 Chat
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Messages View */}
      {currentView === 'messages' && (
        <div className="max-w-4xl mx-auto pt-8 px-4">
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <h2 className="text-2xl font-bold text-black mb-6">Messages</h2>
            
            {matchesWithMessages.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-xl font-bold text-black mb-2">No Conversations Yet</h3>
                <p className="text-gray-600 mb-4">Start matching to begin conversations!</p>
                <button
                  onClick={() => setCurrentView('discover')}
                  className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-4 rounded-lg transition-all"
                >
                  Find Traders
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {matchesWithMessages.map((match) => (
                  <div key={match.match_id} className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all cursor-pointer"
                       onClick={() => openChatAndMarkRead(match)}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="relative">
                          <img
                            src={match.other_user.avatar_url}
                            alt="Profile"
                            className="w-12 h-12 rounded-full object-cover"
                          />
                          {match.other_user.user_status === 'active' && (
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
                          )}
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="font-semibold text-black">{match.other_user.display_name}</h3>
                            {match.other_user.trading_experience && (
                              <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                                {match.other_user.trading_experience}
                              </span>
                            )}
                          </div>
                          
                          {match.latest_message.content ? (
                            <div className="flex items-center space-x-2">
                              <p className="text-sm text-gray-600 truncate max-w-xs">
                                {match.latest_message.sender_id === currentUser?.user_id ? 'You: ' : ''}
                                {match.latest_message.content}
                              </p>
                              {match.latest_message.timestamp && (
                                <span className="text-xs text-gray-400 whitespace-nowrap">
                                  {new Date(match.latest_message.timestamp).toLocaleDateString()}
                                </span>
                              )}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-400">Start a conversation...</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        {match.unread_count > 0 && (
                          <span className="bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-medium">
                            {match.unread_count}
                          </span>
                        )}
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chat View */}
      {currentView === 'chat' && selectedMatch && (
        <div className="max-w-2xl mx-auto pt-8 px-4">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200 flex items-center space-x-3">
              <button
                onClick={() => setCurrentView('matches')}
                className="text-gray-600 hover:text-black transition-all"
              >
                ← Back
              </button>
              <img
                src={selectedMatch.other_user.avatar_url}
                alt="Match"
                className="w-10 h-10 rounded-full object-cover"
              />
              <div>
                <h3 className="font-semibold text-black">{selectedMatch.other_user.display_name}</h3>
                <p className="text-sm text-gray-500">
                  {selectedMatch.other_user.trading_experience} Trader
                </p>
              </div>
            </div>
            
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`flex ${message.sender_id === currentUser.user_id ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 rounded-lg ${
                      message.sender_id === currentUser.user_id
                        ? 'bg-black text-white'
                        : 'bg-gray-100 text-black'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-all"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-2xl font-bold text-black mb-2">It's a Match!</h3>
            <p className="text-gray-600 mb-6">You both liked each other. Start trading together!</p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowMatchModal(false)}
                className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 font-medium py-2 px-4 rounded-lg transition-all"
              >
                Keep Swiping
              </button>
              <button
                onClick={() => {
                  setShowMatchModal(false);
                  setCurrentView('matches');
                }}
                className="flex-1 bg-black hover:bg-gray-800 text-white font-medium py-2 px-4 rounded-lg transition-all"
              >
                Start Chat
              </button>
            </div>
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

      {/* Profile Popup Modal */}
      {showProfilePopup && selectedProfileUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[95vh] overflow-y-auto">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
              <h2 className="text-2xl font-bold text-black">Trader Profile</h2>
              <button
                onClick={() => setShowProfilePopup(false)}
                className="text-gray-500 hover:text-black transition-all"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Profile Header */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-6">
                <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
                  <img
                    src={selectedProfileUser.avatar_url}
                    alt={selectedProfileUser.display_name}
                    className="w-20 h-20 rounded-full border-4 border-white shadow-lg"
                  />
                  
                  <div className="flex-1 text-center md:text-left">
                    <h1 className="text-2xl font-bold text-black mb-2">{selectedProfileUser.display_name}</h1>
                    {selectedProfileUser.show_twitter && selectedProfileUser.twitter_username && (
                      <p className="text-blue-600 mb-2">🐦 @{selectedProfileUser.twitter_username}</p>
                    )}
                    {selectedProfileUser.location && (
                      <p className="text-gray-600 mb-2">📍 {selectedProfileUser.location}</p>
                    )}
                    
                    <div className="flex flex-wrap justify-center md:justify-start gap-2">
                      <span className="bg-black text-white px-3 py-1 rounded-full text-sm font-medium">
                        {selectedProfileUser.trading_experience}
                      </span>
                      <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                        {selectedProfileUser.years_trading} years trading
                      </span>
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {selectedProfileUser.portfolio_size}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bio */}
              {selectedProfileUser.bio && (
                <div>
                  <h3 className="text-lg font-semibold text-black mb-3">About</h3>
                  <p className="text-gray-700 leading-relaxed">{selectedProfileUser.bio}</p>
                </div>
              )}

              {/* Trading Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Trading Style</h4>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Style:</span> {selectedProfileUser.trading_style}</p>
                    <p><span className="text-gray-500">Risk Tolerance:</span> {selectedProfileUser.risk_tolerance}</p>
                    <p><span className="text-gray-500">Trading Hours:</span> {selectedProfileUser.trading_hours}</p>
                    <p><span className="text-gray-500">Communication:</span> {selectedProfileUser.communication_style}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Platforms</h4>
                  <div className="space-y-2 text-sm">
                    {selectedProfileUser.preferred_trading_platform && (
                      <p><span className="text-gray-500">Trading Platform:</span> {selectedProfileUser.preferred_trading_platform}</p>
                    )}
                    {selectedProfileUser.preferred_communication_platform && (
                      <p><span className="text-gray-500">Communication Platform:</span> {selectedProfileUser.preferred_communication_platform}</p>
                    )}
                    {selectedProfileUser.favorite_project && (
                      <p><span className="text-gray-500">Favorite Project:</span> {selectedProfileUser.favorite_project}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Preferred Tokens */}
              {selectedProfileUser.preferred_tokens && selectedProfileUser.preferred_tokens.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Preferred Token Categories</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedProfileUser.preferred_tokens.map((token, idx) => (
                      <span key={idx} className="bg-purple-100 text-purple-800 px-3 py-2 rounded-lg text-sm font-medium">
                        {token}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Looking For */}
              {selectedProfileUser.looking_for && selectedProfileUser.looking_for.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Looking For</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedProfileUser.looking_for.map((item, idx) => (
                      <span key={idx} className="bg-orange-100 text-orange-800 px-3 py-2 rounded-lg text-sm font-medium">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Trading Stories */}
              {(selectedProfileUser.best_trade || selectedProfileUser.worst_trade) && (
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-800">Trading Stories</h4>
                  
                  {selectedProfileUser.best_trade && (
                    <div>
                      <h5 className="text-green-600 font-medium mb-2">💰 Best Trade</h5>
                      <p className="text-sm text-gray-700 bg-green-50 p-3 rounded-lg">{selectedProfileUser.best_trade}</p>
                    </div>
                  )}
                  
                  {selectedProfileUser.worst_trade && (
                    <div>
                      <h5 className="text-red-600 font-medium mb-2">📉 Learning Experience</h5>
                      <p className="text-sm text-gray-700 bg-red-50 p-3 rounded-lg">{selectedProfileUser.worst_trade}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setShowProfilePopup(false);
                    // Find the match for this user and open chat
                    const match = matches.find(m => m.other_user.user_id === selectedProfileUser.user_id);
                    if (match) {
                      setSelectedMatch(match);
                      fetchMessages(match.match_id);
                      setCurrentView('chat');
                    }
                  }}
                  className="flex-1 bg-black hover:bg-gray-800 text-white font-medium py-3 px-6 rounded-lg transition-all"
                >
                  💬 Start Chat
                </button>
                <button
                  onClick={() => setShowProfilePopup(false)}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-lg transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Profile Popup Modal */}
      {showProfilePopup && selectedProfileUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[95vh] overflow-y-auto">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
              <h2 className="text-2xl font-bold text-black">Trader Profile</h2>
              <button
                onClick={() => setShowProfilePopup(false)}
                className="text-gray-500 hover:text-black transition-all"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Profile Header */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-6">
                <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
                  <img
                    src={selectedProfileUser.avatar_url}
                    alt={selectedProfileUser.display_name}
                    className="w-20 h-20 rounded-full border-4 border-white shadow-lg"
                  />
                  
                  <div className="flex-1 text-center md:text-left">
                    <h1 className="text-2xl font-bold text-black mb-2">{selectedProfileUser.display_name}</h1>
                    {selectedProfileUser.show_twitter && selectedProfileUser.twitter_username && (
                      <p className="text-blue-600 mb-2">🐦 @{selectedProfileUser.twitter_username}</p>
                    )}
                    {selectedProfileUser.location && (
                      <p className="text-gray-600 mb-2">📍 {selectedProfileUser.location}</p>
                    )}
                    
                    <div className="flex flex-wrap justify-center md:justify-start gap-2">
                      <span className="bg-black text-white px-3 py-1 rounded-full text-sm font-medium">
                        {selectedProfileUser.trading_experience}
                      </span>
                      <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                        {selectedProfileUser.years_trading} years trading
                      </span>
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {selectedProfileUser.portfolio_size}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bio */}
              {selectedProfileUser.bio && (
                <div>
                  <h3 className="text-lg font-semibold text-black mb-3">About</h3>
                  <p className="text-gray-700 leading-relaxed">{selectedProfileUser.bio}</p>
                </div>
              )}

              {/* Trading Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Trading Style</h4>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Style:</span> {selectedProfileUser.trading_style}</p>
                    <p><span className="text-gray-500">Risk Tolerance:</span> {selectedProfileUser.risk_tolerance}</p>
                    <p><span className="text-gray-500">Trading Hours:</span> {selectedProfileUser.trading_hours}</p>
                    <p><span className="text-gray-500">Communication:</span> {selectedProfileUser.communication_style}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Platforms</h4>
                  <div className="space-y-2 text-sm">
                    {selectedProfileUser.preferred_trading_platform && (
                      <p><span className="text-gray-500">Trading Platform:</span> {selectedProfileUser.preferred_trading_platform}</p>
                    )}
                    {selectedProfileUser.preferred_communication_platform && (
                      <p><span className="text-gray-500">Communication Platform:</span> {selectedProfileUser.preferred_communication_platform}</p>
                    )}
                    {selectedProfileUser.favorite_project && (
                      <p><span className="text-gray-500">Favorite Project:</span> {selectedProfileUser.favorite_project}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Preferred Tokens */}
              {selectedProfileUser.preferred_tokens && selectedProfileUser.preferred_tokens.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Preferred Token Categories</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedProfileUser.preferred_tokens.map((token, idx) => (
                      <span key={idx} className="bg-purple-100 text-purple-800 px-3 py-2 rounded-lg text-sm font-medium">
                        {token}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Looking For */}
              {selectedProfileUser.looking_for && selectedProfileUser.looking_for.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Looking For</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedProfileUser.looking_for.map((item, idx) => (
                      <span key={idx} className="bg-orange-100 text-orange-800 px-3 py-2 rounded-lg text-sm font-medium">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Trading Stories */}
              {(selectedProfileUser.best_trade || selectedProfileUser.worst_trade) && (
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-800">Trading Stories</h4>
                  
                  {selectedProfileUser.best_trade && (
                    <div>
                      <h5 className="text-green-600 font-medium mb-2">💰 Best Trade</h5>
                      <p className="text-sm text-gray-700 bg-green-50 p-3 rounded-lg">{selectedProfileUser.best_trade}</p>
                    </div>
                  )}
                  
                  {selectedProfileUser.worst_trade && (
                    <div>
                      <h5 className="text-red-600 font-medium mb-2">📉 Learning Experience</h5>
                      <p className="text-sm text-gray-700 bg-red-50 p-3 rounded-lg">{selectedProfileUser.worst_trade}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setShowProfilePopup(false);
                    // Find the match for this user and open chat
                    const match = matches.find(m => m.other_user.user_id === selectedProfileUser.user_id);
                    if (match) {
                      setSelectedMatch(match);
                      fetchMessages(match.match_id);
                      setCurrentView('chat');
                    }
                  }}
                  className="flex-1 bg-black hover:bg-gray-800 text-white font-medium py-3 px-6 rounded-lg transition-all"
                >
                  💬 Start Chat
                </button>
                <button
                  onClick={() => setShowProfilePopup(false)}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-lg transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/profile/:username" element={<PublicProfile />} />
        <Route path="/*" element={<AppContent />} />
      </Routes>
    </Router>
  );
}

export default App;