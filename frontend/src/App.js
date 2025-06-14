import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AnimatedPage,
  AnimatedButton,
  AnimatedCard,
  SwipeableCard,
  AnimatedMessage,
  TypingIndicator,
  MatchCelebration,
  AnimatedBadge,
  LoadingDots,
  ShimmerLoading,
  AnimatedInput,
  StaggeredList,
  ToastNotification,
  FloatingActionButton,
  AnimatedProfilePicture
} from './AnimatedComponents';
import { ReferralDashboard, SupportModal } from './ReferralComponents';
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
  // Discovery loading states
  const [discoveryLoading, setDiscoveryLoading] = useState(false);
  const [aiRecommendationsLoading, setAiRecommendationsLoading] = useState(false);
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
    display_name: '',
    referral_code: ''
  });
  const [authLoading, setAuthLoading] = useState(false);
  const [referralInfo, setReferralInfo] = useState(null);

  // Profile dropdown state
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  
  // Additional state for animations and toasts
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('info');
  const [isTyping, setIsTyping] = useState(false);

  // Support and Referral modals
  const [showReferralDashboard, setShowReferralDashboard] = useState(false);
  const [showSupportModal, setShowSupportModal] = useState(false);

  // Profile popup modal state
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const [selectedProfileUser, setSelectedProfileUser] = useState(null);
  const [profilePopupContext, setProfilePopupContext] = useState(''); // 'discover', 'matches', 'messages', 'chat'

  // Toast notification helper
  const showToastNotification = (message, type = 'info') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
  };

  // Typing indicator simulation
  const simulateTyping = (duration = 2000) => {
    setIsTyping(true);
    setTimeout(() => setIsTyping(false), duration);
  };

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
    // Check for referral code in URL
    const urlParams = new URLSearchParams(window.location.search);
    const referralCode = urlParams.get('ref');
    
    if (referralCode) {
      validateReferralCode(referralCode);
    }

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
    if (urlParams.get('auth_success') === 'true') {
      const userId = urlParams.get('user_id');
      
      if (userId) {
        fetchUserProfile(userId);
      }
    } else if (urlParams.get('auth_error') === 'true') {
      alert('Authentication failed. Please try again.');
    }
  }, []);

  // Validate referral code
  const validateReferralCode = async (code) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/referrals/validate/${code}`);
      if (response.ok) {
        const data = await response.json();
        if (data.valid) {
          setReferralInfo(data);
          setEmailForm(prev => ({ ...prev, referral_code: code }));
          showToastNotification(`🎉 ${data.message}`, 'success');
        } else {
          showToastNotification(data.message, 'error');
        }
      }
    } catch (error) {
      console.error('Error validating referral code:', error);
    }
  };

  // Get or generate user's referral code
  const getUserReferralCode = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/referrals/generate/${currentUser.user_id}`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        return data.referral_code;
      }
    } catch (error) {
      console.error('Error getting referral code:', error);
    }
    return null;
  };

  // Handle preview profile
  const handlePreviewProfile = () => {
    console.log('🔍 Preview Profile clicked');
    console.log('Current user:', currentUser);
    console.log('Username:', currentUser?.username);
    console.log('User ID:', currentUser?.user_id);
    
    if (currentUser?.user_id) {
      // Use user_id for the route since that's what the route expects
      const profileUrl = `${window.location.origin}/profile/${currentUser.user_id}`;
      console.log('Opening profile URL:', profileUrl);
      window.open(profileUrl, '_blank');
    } else {
      console.log('❌ No user ID available');
      showToastNotification('Profile not available for preview', 'error');
    }
  };

  // Handle share profile on Twitter
  const handleShareProfile = async () => {
    if (!currentUser?.username) {
      showToastNotification('Profile not available for sharing', 'error');
      return;
    }

    try {
      // Get user's referral code
      const referralCode = await getUserReferralCode();
      
      // Create profile URL with referral code
      let profileUrl = `${window.location.origin}/profile/${currentUser.username}`;
      if (referralCode) {
        profileUrl += `?ref=${referralCode}`;
      }

      // Create Twitter share text
      const shareText = `Check out my trading profile on Solm8! 🚀\n\nConnect with me and other crypto traders on the premier platform for finding your perfect trading partner.\n\n#Solm8 #CryptoTrading #TradingPartner`;
      
      // Create Twitter share URL
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(profileUrl)}`;
      
      // Open Twitter share dialog
      window.open(twitterUrl, '_blank', 'width=550,height=420');
      
      showToastNotification('Twitter share opened! 🐦', 'success');
    } catch (error) {
      console.error('Error sharing profile:', error);
      showToastNotification('Failed to share profile', 'error');
    }
  };

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
    console.log('🔍 fetchDiscoveryCards called with user:', user?.user_id);
    if (!user) {
      console.log('❌ No user provided to fetchDiscoveryCards');
      return;
    }
    
    setDiscoveryLoading(true);
    try {
      console.log('📡 Fetching discovery cards from:', `${API_BASE_URL}/api/discover/${user.user_id}`);
      const response = await fetch(`${API_BASE_URL}/api/discover/${user.user_id}`);
      console.log('📊 Discovery response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('📋 Discovery data received:', data?.length, 'cards');
        console.log('🔍 Raw discovery data:', data);
        const filteredData = filterCardsByStatus(data || []);
        console.log('✅ Filtered discovery cards:', filteredData?.length, 'cards');
        console.log('🔍 Filtered data:', filteredData);
        setDiscoveryCards(filteredData);
      } else {
        console.log('❌ Discovery API error:', response.status, response.statusText);
        const errorText = await response.text();
        console.log('❌ Error response:', errorText);
      }
    } catch (error) {
      console.error('❌ Error fetching discovery cards:', error);
    } finally {
      setDiscoveryLoading(false);
    }
  };

  const fetchAiRecommendations = async (user = currentUser) => {
    console.log('🤖 fetchAiRecommendations called with user:', user?.user_id);
    if (!user) {
      console.log('❌ No user provided to fetchAiRecommendations');
      return;
    }
    
    setAiRecommendationsLoading(true);
    try {
      console.log('📡 Fetching AI recommendations from:', `${API_BASE_URL}/api/ai-recommendations/${user.user_id}`);
      const response = await fetch(`${API_BASE_URL}/api/ai-recommendations/${user.user_id}`);
      console.log('📊 AI recommendations response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('📋 AI recommendations data received:', data?.length, 'cards');
        console.log('🔍 Raw AI data:', data);
        const filteredData = filterCardsByStatus(data || []);
        console.log('✅ Filtered AI recommendations:', filteredData?.length, 'cards');
        console.log('🔍 Filtered AI data:', filteredData);
        setAiRecommendations(filteredData);
      } else {
        console.log('❌ AI recommendations API error:', response.status, response.statusText);
        const errorText = await response.text();
        console.log('❌ Error response:', errorText);
      }
    } catch (error) {
      console.error('❌ Error fetching AI recommendations:', error);
    } finally {
      setAiRecommendationsLoading(false);
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

  const showUserProfile = (user, context = 'matches') => {
    console.log('🔍 showUserProfile called with context:', context);
    setSelectedProfileUser(user);
    setProfilePopupContext(context);
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
        showToastNotification(`🎉 You matched with ${currentCard.display_name}!`, 'success');
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
      showToastNotification('Something went wrong. Please try again.', 'error');
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
      <AnimatedPage className="min-h-screen bg-white flex items-center justify-center p-4">
        <AnimatedCard className="max-w-md w-full p-8" hover={false}>
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="text-center mb-8"
          >
            <motion.h1 
              className="text-4xl font-bold text-black mb-2"
              animate={{ 
                textShadow: ["0 0 0 rgba(0,0,0,0.1)", "0 2px 4px rgba(0,0,0,0.2)", "0 0 0 rgba(0,0,0,0.1)"]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Solm8
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-gray-600"
            >
              Connect with like-minded Solana traders
            </motion.p>
          </motion.div>
          
          <div className="space-y-6">
            {/* Authentication Mode Toggle */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex bg-gray-100 rounded-xl p-1 mb-6"
            >
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setAuthMode('signin')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                  authMode === 'signin' 
                    ? 'bg-white text-black shadow-sm' 
                    : 'text-gray-600 hover:text-black'
                }`}
              >
                Sign In
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setAuthMode('signup')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                  authMode === 'signup' 
                    ? 'bg-white text-black shadow-sm' 
                    : 'text-gray-600 hover:text-black'
                }`}
              >
                Sign Up
              </motion.button>
            </motion.div>

            {/* Email/Password Forms */}
            {(authMode === 'signin' || authMode === 'signup') && (
              <motion.form 
                initial={{ opacity: 0, x: authMode === 'signin' ? -20 : 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                onSubmit={authMode === 'signup' ? handleEmailSignup : handleEmailLogin} 
                className="space-y-4"
              >
                {authMode === 'signup' && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    transition={{ duration: 0.3 }}
                  >
                    <label className="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
                    <motion.input
                      whileFocus={{ scale: 1.02, y: -2 }}
                      type="text"
                      value={emailForm.display_name}
                      onChange={(e) => setEmailForm(prev => ({ ...prev, display_name: e.target.value }))}
                      className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-300"
                      placeholder="Your trading name"
                      required
                    />
                  </motion.div>
                )}
                
                {authMode === 'signup' && referralInfo && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-green-50 border border-green-200 rounded-lg p-3"
                  >
                    <div className="flex items-center space-x-2">
                      <img
                        src={referralInfo.referrer.avatar_url}
                        alt={referralInfo.referrer.display_name}
                        className="w-8 h-8 rounded-full"
                      />
                      <div>
                        <p className="text-sm font-medium text-green-800">
                          Referred by {referralInfo.referrer.display_name}
                        </p>
                        <p className="text-xs text-green-600">You'll both get special bonuses!</p>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                {authMode === 'signup' && referralInfo && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-green-50 border border-green-200 rounded-lg p-3"
                  >
                    <div className="flex items-center space-x-2">
                      <img
                        src={referralInfo.referrer.avatar_url}
                        alt={referralInfo.referrer.display_name}
                        className="w-8 h-8 rounded-full"
                      />
                      <div>
                        <p className="text-sm font-medium text-green-800">
                          Referred by {referralInfo.referrer.display_name}
                        </p>
                        <p className="text-xs text-green-600">You'll both get special bonuses!</p>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <motion.input
                    whileFocus={{ scale: 1.02, y: -2 }}
                    type="email"
                    value={emailForm.email}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-300"
                    placeholder="trader@example.com"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <motion.input
                    whileFocus={{ scale: 1.02, y: -2 }}
                    type="password"
                    value={emailForm.password}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, password: e.target.value }))}
                    className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-300"
                    placeholder="••••••••"
                    required
                  />
                </div>
                
                <AnimatedButton
                  type="submit"
                  disabled={authLoading}
                  className="w-full"
                >
                  {authLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <LoadingDots />
                      <span>Please wait...</span>
                    </div>
                  ) : (
                    authMode === 'signup' ? 'Create Account' : 'Sign In'
                  )}
                </AnimatedButton>
              </motion.form>
            )}
          </div>
        </AnimatedCard>
      </AnimatedPage>
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
      <motion.nav 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white border-b border-gray-200 p-4"
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <motion.h1 
            whileHover={{ scale: 1.05 }}
            className="text-2xl font-bold text-black cursor-pointer"
          >
            Solm8
          </motion.h1>
          <div className="flex space-x-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCurrentView('discover')}
              className={`nav-tab px-4 py-2 rounded-lg font-medium transition-all ${
                currentView === 'discover' ? 'active text-black' : 'text-gray-600 hover:text-black'
              }`}
            >
              Discover
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCurrentView('matches')}
              className={`nav-tab px-4 py-2 rounded-lg font-medium transition-all relative ${
                currentView === 'matches' ? 'active text-black' : 'text-gray-600 hover:text-black'
              }`}
            >
              Matches ({matches.length})
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setCurrentView('messages');
                fetchMatchesWithMessages();
              }}
              className={`nav-tab px-4 py-2 rounded-lg font-medium transition-all relative ${
                currentView === 'messages' ? 'active text-black' : 'text-gray-600 hover:text-black'
              }`}
            >
              Messages
              <AnimatedBadge 
                count={matchesWithMessages.length > 0 ? matchesWithMessages.reduce((total, match) => total + match.unread_count, 0) : 0}
              />
            </motion.button>
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
                      setShowReferralDashboard(true);
                      setShowProfileDropdown(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 715.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span>Refer Friends</span>
                  </button>
                  
                  <button
                    onClick={() => {
                      handlePreviewProfile();
                      setShowProfileDropdown(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span>Public Profile</span>
                  </button>
                  
                  <button
                    onClick={() => {
                      setShowSupportModal(true);
                      setShowProfileDropdown(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Support</span>
                  </button>
                  
                  <hr className="my-1 border-gray-200" />
                  
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
      </motion.nav>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-4">
        <AnimatePresence mode="wait">
          {/* Discover View */}
          {currentView === 'discover' && (
            <AnimatedPage key="discover">
              <div className="mb-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-black">Discover Traders</h2>
                  <div className="flex items-center space-x-4">
                    {/* Discovery Mode Toggle */}
                    <div className="flex bg-gray-100 rounded-xl p-1">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setDiscoveryMode('browse')}
                        className={`py-2 px-4 rounded-lg font-medium transition-all ${
                          discoveryMode === 'browse' 
                            ? 'bg-white text-black shadow-sm' 
                            : 'text-gray-600 hover:text-black'
                        }`}
                      >
                        Browse Traders
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setDiscoveryMode('ai')}
                        className={`py-2 px-4 rounded-lg font-medium transition-all ${
                          discoveryMode === 'ai' 
                            ? 'bg-white text-black shadow-sm' 
                            : 'text-gray-600 hover:text-black'
                        }`}
                      >
                        AI Recommended
                      </motion.button>
                    </div>
                    
                    {/* Active Filter Toggle */}
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="show_only_active"
                        checked={showOnlyActive}
                        onChange={(e) => {
                          setShowOnlyActive(e.target.checked);
                          // Re-filter cards
                          setDiscoveryCards(prev => filterCardsByStatus(prev));
                          setAiRecommendations(prev => filterCardsByStatus(prev));
                        }}
                        className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black focus:ring-2"
                      />
                      <label htmlFor="show_only_active" className="text-sm font-medium text-gray-700">
                        Show only active traders
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Discovery Cards */}
              <div className="grid grid-cols-1 gap-6">
                {getCurrentCards().length > 0 && getCurrentIndex() < getCurrentCards().length ? (
                  <SwipeableCard
                    onSwipeLeft={() => handleSwipe('pass', discoveryMode === 'ai')}
                    onSwipeRight={() => handleSwipe('like', discoveryMode === 'ai')}
                    className="max-w-2xl mx-auto w-full"
                  >
                    <AnimatedCard className="p-6" hover={false}>
                      <div className="flex items-start space-x-4">
                        <AnimatedProfilePicture
                          src={getCurrentCard().avatar_url}
                          alt={getCurrentCard().display_name}
                          size="w-20 h-20"
                          className={`cursor-pointer ${getCurrentCard().user_status === 'active' ? 'status-online' : ''}`}
                          onClick={() => showUserProfile(getCurrentCard(), 'discover')}
                        />
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="text-xl font-bold text-black">{getCurrentCard().display_name}</h3>
                            <div className="flex items-center space-x-2">
                              {discoveryMode === 'ai' && getCurrentCard().ai_compatibility && (
                                <div className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium">
                                  {getCurrentCard().ai_compatibility.compatibility_percentage}% Match
                                </div>
                              )}
                              {getCurrentCard().user_status === 'active' && (
                                <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium flex items-center">
                                  <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                                  Active
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="mt-1 text-sm text-gray-500">
                            {getCurrentCard().location && (
                              <div className="flex items-center space-x-1">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <span>{getCurrentCard().location}</span>
                              </div>
                            )}
                          </div>
                          
                          {getCurrentCard().bio && (
                            <p className="mt-3 text-gray-700">{getCurrentCard().bio}</p>
                          )}
                          
                          <div className="mt-4 grid grid-cols-2 gap-3">
                            {getCurrentCard().trading_experience && (
                              <div className="bg-gray-50 p-2 rounded-lg">
                                <span className="text-xs text-gray-500">Experience</span>
                                <p className="font-medium">{getCurrentCard().trading_experience}</p>
                              </div>
                            )}
                            
                            {getCurrentCard().trading_style && (
                              <div className="bg-gray-50 p-2 rounded-lg">
                                <span className="text-xs text-gray-500">Style</span>
                                <p className="font-medium">{getCurrentCard().trading_style}</p>
                              </div>
                            )}
                            
                            {getCurrentCard().preferred_tokens && getCurrentCard().preferred_tokens.length > 0 && (
                              <div className="bg-gray-50 p-2 rounded-lg col-span-2">
                                <span className="text-xs text-gray-500">Preferred Tokens</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {getCurrentCard().preferred_tokens.map(token => (
                                    <span key={token} className="bg-gray-200 text-gray-800 px-2 py-0.5 rounded text-xs">
                                      {token}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          
                          <div className="mt-6 flex justify-between">
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleSwipe('pass', discoveryMode === 'ai')}
                              className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded-lg transition-all"
                            >
                              Pass
                            </motion.button>
                            
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleSwipe('like', discoveryMode === 'ai')}
                              className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-4 rounded-lg transition-all"
                            >
                              Like
                            </motion.button>
                          </div>
                        </div>
                      </div>
                    </AnimatedCard>
                  </SwipeableCard>
                ) : (
                  <div className="text-center py-12">
                    <h3 className="text-xl font-medium text-gray-700 mb-2">
                      {(discoveryMode === 'browse' && discoveryLoading) || (discoveryMode === 'ai' && aiRecommendationsLoading) 
                        ? 'Loading traders...' 
                        : 'No traders available right now'}
                    </h3>
                    {(discoveryMode === 'browse' && discoveryLoading) || (discoveryMode === 'ai' && aiRecommendationsLoading) ? (
                      <div className="flex justify-center">
                        <LoadingDots size="lg" />
                      </div>
                    ) : (
                      <p className="text-gray-500">
                        {discoveryMode === 'browse' 
                          ? 'You\'ve seen all available traders. Check back later for new matches!' 
                          : 'No AI recommendations available. Check back later for new matches!'}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </AnimatedPage>
          )}
          
          {/* Matches View */}
          {currentView === 'matches' && (
            <AnimatedPage key="matches">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-black">Your Matches</h2>
                <p className="text-gray-600">Traders who liked you back</p>
              </div>
              
              {matches.length > 0 ? (
                <StaggeredList className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {matches.map(match => (
                    <AnimatedCard 
                      key={match.match_id} 
                      className="p-4"
                      onClick={() => showUserProfile(match.other_user, 'matches')}
                    >
                      <div className="flex items-center space-x-3">
                        <AnimatedProfilePicture
                          src={match.other_user?.avatar_url || '/api/placeholder/40/40'}
                          alt={match.other_user?.display_name || 'User'}
                          className={match.other_user?.user_status === 'active' ? 'status-online' : ''}
                        />
                        <div>
                          <h3 className="font-semibold text-black">{match.other_user?.display_name || 'Unknown User'}</h3>
                          <p className="text-sm text-gray-600">{match.other_user?.trading_style || 'Trader'}</p>
                        </div>
                      </div>
                      
                      <div className="mt-4 flex justify-between">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            openChatAndMarkRead(match);
                          }}
                          className="bg-black hover:bg-gray-800 text-white text-sm font-medium py-1.5 px-3 rounded-lg transition-all"
                        >
                          Message
                        </motion.button>
                        
                        <div className="text-xs text-gray-500 flex items-center">
                          Matched {new Date(match.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </AnimatedCard>
                  ))}
                </StaggeredList>
              ) : (
                <div className="text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-200">
                  <h3 className="text-xl font-medium text-gray-700 mb-2">No matches yet</h3>
                  <p className="text-gray-500 mb-6">
                    Like more traders to increase your chances of matching!
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setCurrentView('discover')}
                    className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-6 rounded-xl transition-all"
                  >
                    Discover Traders
                  </motion.button>
                </div>
              )}
            </AnimatedPage>
          )}
          
          {/* Messages View */}
          {currentView === 'messages' && (
            <AnimatedPage key="messages">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-black">Messages</h2>
                <p className="text-gray-600">Chat with your matches</p>
              </div>
              
              {matchesWithMessages.length > 0 ? (
                <StaggeredList className="space-y-2">
                  {matchesWithMessages.map(match => (
                    <AnimatedCard 
                      key={match.match_id} 
                      className={`p-4 ${match.unread_count > 0 ? 'border-l-4 border-black' : ''}`}
                      onClick={() => openChatAndMarkRead(match)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <AnimatedProfilePicture
                            src={match.other_user?.avatar_url || '/api/placeholder/40/40'}
                            alt={match.other_user?.display_name || 'User'}
                            className={match.other_user?.user_status === 'active' ? 'status-online' : ''}
                          />
                          <div>
                            <h3 className="font-semibold text-black">{match.other_user?.display_name || 'Unknown User'}</h3>
                            <p className="text-sm text-gray-600 truncate max-w-xs">
                              {match.last_message ? match.last_message.content : 'No messages yet'}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex flex-col items-end">
                          <div className="text-xs text-gray-500">
                            {match.last_message ? new Date(match.last_message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                          </div>
                          {match.unread_count > 0 && (
                            <div className="badge-animated badge-pulse bg-black text-white text-xs rounded-full w-5 h-5 flex items-center justify-center mt-1">
                              {match.unread_count}
                            </div>
                          )}
                        </div>
                      </div>
                    </AnimatedCard>
                  ))}
                </StaggeredList>
              ) : (
                <div className="text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-200">
                  <h3 className="text-xl font-medium text-gray-700 mb-2">No messages yet</h3>
                  <p className="text-gray-500 mb-6">
                    Start a conversation with one of your matches!
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setCurrentView('matches')}
                    className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-6 rounded-xl transition-all"
                  >
                    View Matches
                  </motion.button>
                </div>
              )}
            </AnimatedPage>
          )}
          
          {/* Chat View */}
          {currentView === 'chat' && selectedMatch && (
            <AnimatedPage key="chat">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                {/* Chat Header */}
                <div className="border-b border-gray-200 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setCurrentView('messages')}
                        className="text-gray-600 hover:text-black"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                      </motion.button>
                      
                      <AnimatedProfilePicture
                        src={selectedMatch.other_user?.avatar_url || '/api/placeholder/40/40'}
                        alt={selectedMatch.other_user?.display_name || 'User'}
                        className={selectedMatch.other_user?.user_status === 'active' ? 'status-online' : ''}
                        onClick={() => showUserProfile(selectedMatch.other_user, 'chat')}
                      />
                      
                      <div>
                        <h3 className="font-semibold text-black">{selectedMatch.other_user?.display_name || 'Unknown User'}</h3>
                        <p className="text-xs text-gray-500">
                          {selectedMatch.other_user?.user_status === 'active' ? 'Active now' : 'Offline'}
                        </p>
                      </div>
                    </div>
                    
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => showUserProfile(selectedMatch.other_user, 'chat')}
                      className="text-gray-600 hover:text-black"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </motion.button>
                  </div>
                </div>
                
                {/* Chat Messages */}
                <div className="p-4 h-96 overflow-y-auto chat-messages">
                  {messages.length > 0 ? (
                    <div className="space-y-4">
                      {messages.map(message => (
                        <AnimatedMessage
                          key={message.message_id}
                          message={message.content}
                          isOwn={message.sender_id === currentUser.user_id}
                          timestamp={message.created_at}
                        />
                      ))}
                      {isTyping && <TypingIndicator />}
                      <div ref={messagesEndRef} />
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                      <p className="text-gray-500 mb-4">No messages yet</p>
                      <p className="text-sm text-gray-400">Send a message to start the conversation!</p>
                    </div>
                  )}
                </div>
                
                {/* Chat Input */}
                <div className="border-t border-gray-200 p-4">
                  <form onSubmit={handleSendMessage} className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      className="chat-input flex-1"
                      placeholder="Type a message..."
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      type="submit"
                      disabled={!newMessage.trim()}
                      className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white p-3 rounded-full transition-all"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </motion.button>
                  </form>
                </div>
              </div>
            </AnimatedPage>
          )}
        </AnimatePresence>
      </div>
      
      {/* Match Celebration Modal */}
      <MatchCelebration
        isVisible={showMatchModal}
        onClose={() => setShowMatchModal(false)}
        user={getCurrentCard()}
      />

      {/* Referral Dashboard Modal */}
      <ReferralDashboard
        isOpen={showReferralDashboard}
        onClose={() => setShowReferralDashboard(false)}
        currentUser={currentUser}
      />

      {/* Support Modal */}
      <SupportModal
        isOpen={showSupportModal}
        onClose={() => setShowSupportModal(false)}
      />

      {/* Toast Notification */}
      <ToastNotification
        message={toastMessage}
        type={toastType}
        isVisible={showToast}
        onClose={() => setShowToast(false)}
      />
      
      {/* Profile Popup */}
      {showProfilePopup && selectedProfileUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-black">Trader Profile</h2>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setShowProfilePopup(false)}
                  className="text-gray-500 hover:text-black"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </motion.button>
              </div>
              
              <div className="flex flex-col md:flex-row md:space-x-6">
                <div className="md:w-1/3 flex flex-col items-center mb-6 md:mb-0">
                  <AnimatedProfilePicture
                    src={selectedProfileUser.avatar_url}
                    alt={selectedProfileUser.display_name}
                    size="w-32 h-32"
                    className={selectedProfileUser.user_status === 'active' ? 'status-online' : ''}
                  />
                  
                  <h3 className="text-xl font-bold text-black mt-4">{selectedProfileUser.display_name}</h3>
                  
                  {selectedProfileUser.location && (
                    <p className="text-gray-600 flex items-center mt-1">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {selectedProfileUser.location}
                    </p>
                  )}
                  
                  {selectedProfileUser.show_twitter && selectedProfileUser.twitter_username && (
                    <a
                      href={`https://twitter.com/${selectedProfileUser.twitter_username}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:text-blue-600 flex items-center mt-2"
                    >
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723 10.054 10.054 0 01-3.127 1.184 4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
                      </svg>
                      @{selectedProfileUser.twitter_username}
                    </a>
                  )}
                  
                  {profilePopupContext === 'chat' || profilePopupContext === 'messages' ? (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => {
                        setShowProfilePopup(false);
                        setCurrentView('chat');
                      }}
                      className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-6 rounded-xl mt-4 w-full transition-all"
                    >
                      Back to Chat
                    </motion.button>
                  ) : (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => {
                        const match = matches.find(m => m.user.user_id === selectedProfileUser.user_id);
                        if (match) {
                          setShowProfilePopup(false);
                          openChatAndMarkRead(match);
                        }
                      }}
                      className="bg-black hover:bg-gray-800 text-white font-medium py-2 px-6 rounded-xl mt-4 w-full transition-all"
                    >
                      Message
                    </motion.button>
                  )}
                </div>
                
                <div className="md:w-2/3">
                  {selectedProfileUser.bio && (
                    <div className="mb-6">
                      <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Bio</h4>
                      <p className="text-gray-800">{selectedProfileUser.bio}</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    {selectedProfileUser.trading_experience && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Experience</h4>
                        <p className="text-gray-800">{selectedProfileUser.trading_experience}</p>
                      </div>
                    )}
                    
                    {selectedProfileUser.years_trading > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Years Trading</h4>
                        <p className="text-gray-800">{selectedProfileUser.years_trading} {selectedProfileUser.years_trading === 1 ? 'year' : 'years'}</p>
                      </div>
                    )}
                    
                    {selectedProfileUser.trading_style && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Trading Style</h4>
                        <p className="text-gray-800">{selectedProfileUser.trading_style}</p>
                      </div>
                    )}
                    
                    {selectedProfileUser.portfolio_size && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Portfolio Size</h4>
                        <p className="text-gray-800">{selectedProfileUser.portfolio_size}</p>
                      </div>
                    )}
                    
                    {selectedProfileUser.risk_tolerance && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Risk Tolerance</h4>
                        <p className="text-gray-800">{selectedProfileUser.risk_tolerance}</p>
                      </div>
                    )}
                    
                    {selectedProfileUser.trading_hours && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Trading Hours</h4>
                        <p className="text-gray-800">{selectedProfileUser.trading_hours}</p>
                      </div>
                    )}
                  </div>
                  
                  {selectedProfileUser.preferred_tokens && selectedProfileUser.preferred_tokens.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Preferred Tokens</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedProfileUser.preferred_tokens.map(token => (
                          <span key={token} className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                            {token}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {selectedProfileUser.looking_for && selectedProfileUser.looking_for.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Looking For</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedProfileUser.looking_for.map(item => (
                          <span key={item} className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {selectedProfileUser.best_trade && (
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Best Trade</h4>
                      <p className="text-gray-800">{selectedProfileUser.best_trade}</p>
                    </div>
                  )}
                  
                  {selectedProfileUser.worst_trade && (
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Worst Trade</h4>
                      <p className="text-gray-800">{selectedProfileUser.worst_trade}</p>
                    </div>
                  )}
                  
                  {selectedProfileUser.favorite_project && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-500 uppercase mb-1">Favorite Project</h4>
                      <p className="text-gray-800">{selectedProfileUser.favorite_project}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
      
      {/* Profile Manager Modal */}
      {showProfileManager && (
        <ProfileManager
          user={currentUser}
          onClose={() => setShowProfileManager(false)}
          onUpdate={(updatedUser) => {
            setCurrentUser(updatedUser);
            setShowProfileManager(false);
          }}
        />
      )}
    </div>
  );
}

// Main App Component
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/profile/:userId" element={<PublicProfileWrapper />} />
        <Route path="/" element={<AppContent />} />
      </Routes>
    </Router>
  );
}

// Wrapper for Public Profile with useParams
function PublicProfileWrapper() {
  const { userId } = useParams();
  return <PublicProfile userId={userId} />;
}

export default App;
