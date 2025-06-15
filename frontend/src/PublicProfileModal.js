import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const PublicProfileModal = ({ isOpen, onClose, user }) => {
  const [showShareMenu, setShowShareMenu] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [socialLinks, setSocialLinks] = useState({
    twitter: '',
    discord: '',
    telegram: '',
    website: '',
    linkedin: ''
  });
  const [tradingHighlight, setTradingHighlight] = useState({
    title: '',
    description: '',
    profit_loss: '',
    percentage_gain: '',
    highlight_type: 'pnl_screenshot',
    date_achieved: new Date().toISOString().split('T')[0]
  });
  const [highlightImage, setHighlightImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  
  if (!isOpen || !user) return null;

  // Share profile function
  const handleShareProfile = async () => {
    try {
      // Get user's referral code
      const referralCode = await getUserReferralCode();
      
      // Create profile URL with referral code
      let profileUrl = `https://Solm8.com/profile/${user.username}`;
      if (referralCode) {
        profileUrl += `?ref=${referralCode}`;
      }

      // Create share text
      const shareText = `🚀 Check out my Solm8 trading profile!\n\nI'm ${user.trading_experience} trader specializing in ${user.preferred_tokens?.join(', ') || 'crypto trading'}.\n\nConnect with me and other elite Solana traders.\n\n#Solm8 #SolanaTrading #CryptoTrader`;
      
      // Create Twitter share URL
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(profileUrl)}`;
      
      // Open Twitter share dialog
      window.open(twitterUrl, '_blank', 'width=550,height=420');
      setShowShareMenu(false);
      
    } catch (error) {
      console.error('Error sharing profile:', error);
    }
  };

  const getUserReferralCode = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/referrals/generate/${user.user_id}`, {
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

  const copyProfileLink = async () => {
    try {
      const referralCode = await getUserReferralCode();
      let profileUrl = `https://Solm8.com/profile/${user.username}`;
      if (referralCode) {
        profileUrl += `?ref=${referralCode}`;
      }
      
      await navigator.clipboard.writeText(profileUrl);
      alert('🔗 Profile link copied to clipboard!');
      setShowShareMenu(false);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      alert('Failed to copy link');
    }
  };

  const previewPublicProfile = () => {
    const profileUrl = `https://Solm8.com/profile/${user.username}`;
    window.open(profileUrl, '_blank');
  };

  // Handle image file selection
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
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
      
      setHighlightImage(file);
    }
  };

  // Save trading highlight
  const handleSaveTradingHighlight = async () => {
    if (!tradingHighlight.title.trim()) {
      alert('Please enter a title for your trading highlight');
      return;
    }

    setIsUploading(true);
    
    try {
      let imageData = '';
      
      // Convert image to base64 if provided
      if (highlightImage) {
        const reader = new FileReader();
        imageData = await new Promise((resolve, reject) => {
          reader.onload = () => {
            const base64 = reader.result.split(',')[1]; // Remove data:image/... prefix
            resolve(base64);
          };
          reader.onerror = reject;
          reader.readAsDataURL(highlightImage);
        });
      }

      // Prepare highlight data
      const highlightData = {
        ...tradingHighlight,
        image_data: imageData
      };

      // Send to backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/save-trading-highlight/${user.user_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(highlightData)
      });

      if (response.ok) {
        alert('🎉 Trading highlight saved successfully!');
        // Reset form
        setTradingHighlight({
          title: '',
          description: '',
          profit_loss: '',
          percentage_gain: '',
          highlight_type: 'pnl_screenshot',
          date_achieved: new Date().toISOString().split('T')[0]
        });
        setHighlightImage(null);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save trading highlight');
      }
    } catch (error) {
      console.error('Error saving trading highlight:', error);
      alert(`Failed to save trading highlight: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Save social links
  const handleSaveSocialLinks = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/update-social-links/${user.user_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(socialLinks)
      });

      if (response.ok) {
        alert('🎉 Social links saved successfully!');
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save social links');
      }
    } catch (error) {
      console.error('Error saving social links:', error);
      alert(`Failed to save social links: ${error.message}`);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          className="bg-white rounded-3xl p-0 max-w-5xl w-full max-h-[95vh] overflow-hidden shadow-2xl border border-gray-200"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Hero Header */}
          <div className="relative bg-black p-8 text-white">
            <div className="relative flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <img
                    src={user.avatar_url || '/api/placeholder/96/96'}
                    alt={user.display_name}
                    className="w-24 h-24 rounded-full border-4 border-white shadow-lg object-cover"
                  />
                  <div className="absolute -bottom-2 -right-2 bg-white w-8 h-8 rounded-full border-2 border-black flex items-center justify-center">
                    <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold mb-1">{user.display_name}</h1>
                  <p className="text-gray-300 text-lg">@{user.username}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium">
                      {user.trading_experience} Trader
                    </span>
                    {user.years_trading && (
                      <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium">
                        {user.years_trading} Years Experience
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Header Actions */}
              <div className="flex items-center space-x-3">
                {/* Preview Button */}
                <button
                  onClick={previewPublicProfile}
                  className="bg-gray-800 text-white hover:bg-gray-700 px-6 py-3 rounded-xl flex items-center space-x-2 transition-all duration-300 font-medium"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>Preview</span>
                </button>
                
                {/* Share Button */}
                <div className="relative">
                  <button
                    onClick={() => setShowShareMenu(!showShareMenu)}
                    className="bg-white text-black hover:bg-gray-100 px-6 py-3 rounded-xl flex items-center space-x-2 transition-all duration-300 font-medium"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                    </svg>
                    <span>Share</span>
                  </button>
                  
                  {showShareMenu && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95, y: 10 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50"
                    >
                      <button
                        onClick={handleShareProfile}
                        className="flex items-center space-x-3 w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-all"
                      >
                        <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium">Share on Twitter</p>
                          <p className="text-xs text-gray-500">Share with your followers</p>
                        </div>
                      </button>
                      <button
                        onClick={copyProfileLink}
                        className="flex items-center space-x-3 w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-all"
                      >
                        <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium">Copy Link</p>
                          <p className="text-xs text-gray-500">Get shareable link</p>
                        </div>
                      </button>
                    </motion.div>
                  )}
                </div>
                
                <button
                  onClick={onClose}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white p-3 rounded-xl transition-all duration-300"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            {user.bio && (
              <p className="text-gray-200 mt-4 text-lg leading-relaxed max-w-2xl">{user.bio}</p>
            )}
          </div>

          {/* Navigation Tabs */}
          <div className="bg-white border-b border-gray-200">
            <div className="flex space-x-8 px-8">
              {[
                { id: 'overview', label: 'Trading Profile', icon: '📊' },
                { id: 'screenshots', label: 'Trading Screenshots', icon: '📸' },
                { id: 'social', label: 'Social & Links', icon: '🔗' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-all ${
                    activeTab === tab.id
                      ? 'border-black text-black'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="overflow-y-auto max-h-[60vh] p-8">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-8"
              >
                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 border border-gray-200 p-4 rounded-2xl">
                    <div className="text-2xl font-bold text-black">{user.trading_experience}</div>
                    <div className="text-gray-600 text-sm">Experience Level</div>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 p-4 rounded-2xl">
                    <div className="text-2xl font-bold text-black">{user.years_trading || 0}Y</div>
                    <div className="text-gray-600 text-sm">Years Trading</div>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 p-4 rounded-2xl">
                    <div className="text-2xl font-bold text-black">{user.trading_style}</div>
                    <div className="text-gray-600 text-sm">Trading Style</div>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 p-4 rounded-2xl">
                    <div className="text-2xl font-bold text-black">{user.portfolio_size}</div>
                    <div className="text-gray-600 text-sm">Portfolio Size</div>
                  </div>
                </div>

                {/* Preferred Tokens */}
                {user.preferred_tokens && user.preferred_tokens.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 p-6 rounded-2xl">
                    <h3 className="text-xl font-bold text-black mb-4 flex items-center">
                      <span className="text-2xl mr-2">🪙</span>
                      Preferred Token Categories
                    </h3>
                    <div className="flex flex-wrap gap-3">
                      {user.preferred_tokens.map((token, index) => (
                        <span
                          key={index}
                          className="px-4 py-2 bg-black text-white rounded-full text-sm font-medium shadow-sm transform hover:scale-105 transition-all"
                        >
                          {token}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trading Goals */}
                {user.looking_for && user.looking_for.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 p-6 rounded-2xl">
                    <h3 className="text-xl font-bold text-black mb-4 flex items-center">
                      <span className="text-2xl mr-2">🎯</span>
                      Trading Goals & Interests
                    </h3>
                    <div className="flex flex-wrap gap-3">
                      {user.looking_for.map((goal, index) => (
                        <span
                          key={index}
                          className="px-4 py-2 bg-gray-800 text-white rounded-full text-sm font-medium shadow-sm transform hover:scale-105 transition-all"
                        >
                          {goal}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trading Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {user.communication_style && (
                    <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                      <h4 className="font-bold text-black mb-3 flex items-center">
                        <span className="text-xl mr-2">💬</span>
                        Communication Style
                      </h4>
                      <p className="text-gray-600">{user.communication_style}</p>
                    </div>
                  )}

                  {user.trading_hours && (
                    <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                      <h4 className="font-bold text-black mb-3 flex items-center">
                        <span className="text-xl mr-2">⏰</span>
                        Active Trading Hours
                      </h4>
                      <p className="text-gray-600">{user.trading_hours}</p>
                    </div>
                  )}

                  {user.preferred_trading_platform && (
                    <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                      <h4 className="font-bold text-black mb-3 flex items-center">
                        <span className="text-xl mr-2">⚡</span>
                        Preferred Platform
                      </h4>
                      <p className="text-gray-600">{user.preferred_trading_platform}</p>
                    </div>
                  )}

                  {user.location && (
                    <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                      <h4 className="font-bold text-black mb-3 flex items-center">
                        <span className="text-xl mr-2">📍</span>
                        Location
                      </h4>
                      <p className="text-gray-600">{user.location}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Trading Screenshots Tab */}
            {activeTab === 'screenshots' && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-black mb-2">📸 Trading Screenshots & Highlights</h3>
                  <p className="text-gray-600">Showcase your best trades and achievements</p>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-2xl p-8">
                  <div className="text-center mb-6">
                    <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <h4 className="text-xl font-bold text-black mb-2">Add Trading Screenshot</h4>
                    <p className="text-gray-600">Upload your P&L screenshots, trading achievements, or portfolio highlights</p>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-semibold text-black mb-3">Upload Screenshot</label>
                      <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-gray-400 transition-all">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleImageUpload}
                          className="hidden"
                          id="screenshot-upload"
                        />
                        <label htmlFor="screenshot-upload" className="cursor-pointer">
                          <div className="space-y-2">
                            <svg className="w-12 h-12 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="text-black font-medium">Click to upload or drag and drop</p>
                            <p className="text-gray-600 text-sm">PNG, JPG, GIF up to 5MB</p>
                          </div>
                        </label>
                      </div>
                      {highlightImage && (
                        <p className="text-sm text-black mt-2 flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Selected: {highlightImage.name}
                        </p>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-black mb-2">Title</label>
                        <input
                          type="text"
                          placeholder="e.g., My Best SOL Trade"
                          value={tradingHighlight.title}
                          onChange={(e) => setTradingHighlight({...tradingHighlight, title: e.target.value})}
                          className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-black mb-2">Date</label>
                        <input
                          type="date"
                          value={tradingHighlight.date_achieved}
                          onChange={(e) => setTradingHighlight({...tradingHighlight, date_achieved: e.target.value})}
                          className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-black mb-2">Description</label>
                      <textarea
                        placeholder="Tell the story behind this trade..."
                        rows="3"
                        value={tradingHighlight.description}
                        onChange={(e) => setTradingHighlight({...tradingHighlight, description: e.target.value})}
                        className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-black mb-2">Profit/Loss</label>
                        <input
                          type="text"
                          placeholder="e.g., +$5,000"
                          value={tradingHighlight.profit_loss}
                          onChange={(e) => setTradingHighlight({...tradingHighlight, profit_loss: e.target.value})}
                          className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-black mb-2">Percentage Gain</label>
                        <input
                          type="text"
                          placeholder="e.g., +250%"
                          value={tradingHighlight.percentage_gain}
                          onChange={(e) => setTradingHighlight({...tradingHighlight, percentage_gain: e.target.value})}
                          className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <button 
                        onClick={handleSaveTradingHighlight}
                        disabled={isUploading}
                        className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white px-8 py-3 rounded-xl transition-all duration-300 font-semibold shadow-lg transform hover:scale-105"
                      >
                        {isUploading ? (
                          <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Saving...
                          </span>
                        ) : (
                          'Save Trading Highlight'
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Social & Links Tab */}
            {activeTab === 'social' && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-black mb-2">🔗 Social Links & Connections</h3>
                  <p className="text-gray-600">Connect with other traders across platforms</p>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-2xl p-8">
                  <div className="text-center mb-6">
                    <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                    </div>
                    <h4 className="text-xl font-bold text-black mb-2">Add Your Social Links</h4>
                    <p className="text-gray-600">Let other traders connect with you on your preferred platforms</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[
                      { key: 'twitter', label: 'Twitter', placeholder: '@yourusername', icon: '🐦' },
                      { key: 'discord', label: 'Discord', placeholder: 'username#1234', icon: '🎮' },
                      { key: 'telegram', label: 'Telegram', placeholder: '@yourusername', icon: '✈️' },
                      { key: 'website', label: 'Website', placeholder: 'https://yourwebsite.com', icon: '🌐' }
                    ].map((social) => (
                      <div key={social.key}>
                        <label className="block text-sm font-semibold text-black mb-2 flex items-center">
                          <span className="mr-2">{social.icon}</span>
                          {social.label}
                        </label>
                        <div className="relative">
                          <input
                            type={social.key === 'website' ? 'url' : 'text'}
                            placeholder={social.placeholder}
                            value={socialLinks[social.key]}
                            onChange={(e) => setSocialLinks({...socialLinks, [social.key]: e.target.value})}
                            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent pl-12"
                          />
                          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 w-6 h-6 bg-gray-800 rounded-lg flex items-center justify-center">
                            <span className="text-xs text-white">{social.icon}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-end mt-6">
                    <button 
                      onClick={handleSaveSocialLinks}
                      className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-xl transition-all duration-300 font-semibold shadow-lg transform hover:scale-105"
                    >
                      Save Social Links
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PublicProfileModal;