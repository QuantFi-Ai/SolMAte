import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const PublicProfileModal = ({ isOpen, onClose, user }) => {
  const [showShareMenu, setShowShareMenu] = useState(false);
  const [showSocialLinksForm, setShowSocialLinksForm] = useState(false);
  const [showTradingHighlights, setShowTradingHighlights] = useState(false);
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
      let profileUrl = `${window.location.origin}/profile/${user.username}`;
      if (referralCode) {
        profileUrl += `?ref=${referralCode}`;
      }

      // Create share text
      const shareText = `Check out my trading profile on Solm8! 🚀\n\nConnect with me and other crypto traders.\n\n#Solm8 #CryptoTrading`;
      
      // Create Twitter share URL
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(profileUrl)}`;
      
      // Open Twitter share dialog
      window.open(twitterUrl, '_blank', 'width=550,height=420');
      
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
      let profileUrl = `${window.location.origin}/profile/${user.username}`;
      if (referralCode) {
        profileUrl += `?ref=${referralCode}`;
      }
      
      await navigator.clipboard.writeText(profileUrl);
      alert('Profile link copied to clipboard!');
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      alert('Failed to copy link');
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-black">Your Public Profile</h2>
            <div className="flex items-center space-x-2">
              {/* Share Button */}
              <div className="relative">
                <button
                  onClick={() => setShowShareMenu(!showShareMenu)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-all"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                  <span>Share</span>
                </button>
                
                {showShareMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <button
                      onClick={handleShareProfile}
                      className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                      </svg>
                      <span>Share on Twitter</span>
                    </button>
                    <button
                      onClick={copyProfileLink}
                      className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-all"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <span>Copy Link</span>
                    </button>
                  </div>
                )}
              </div>
              
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
          </div>

          {/* Profile Content */}
          <div className="space-y-6">
            {/* Profile Header */}
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden">
                <img
                  src={user.avatar_url || '/api/placeholder/96/96'}
                  alt={user.display_name}
                  className="w-full h-full object-cover"
                />
              </div>
              <h1 className="text-3xl font-bold text-black mb-2">{user.display_name}</h1>
              <p className="text-lg text-gray-600">@{user.username}</p>
              {user.bio && (
                <p className="text-gray-700 mt-4 max-w-2xl mx-auto">{user.bio}</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setShowSocialLinksForm(!showSocialLinksForm)}
                className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-all"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                <span>Add Social Links</span>
              </button>
              
              <button
                onClick={() => setShowTradingHighlights(!showTradingHighlights)}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-all"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Add Screenshots</span>
              </button>
            </div>

            {/* Social Links Form */}
            {showSocialLinksForm && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-purple-50 rounded-xl p-6"
              >
                <h3 className="text-lg font-bold text-purple-800 mb-4">Add Social Links</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-purple-700 mb-2">Twitter</label>
                    <input
                      type="text"
                      placeholder="@yourusername"
                      value={socialLinks.twitter}
                      onChange={(e) => setSocialLinks({...socialLinks, twitter: e.target.value})}
                      className="w-full border border-purple-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-700 mb-2">Discord</label>
                    <input
                      type="text"
                      placeholder="username#1234"
                      value={socialLinks.discord}
                      onChange={(e) => setSocialLinks({...socialLinks, discord: e.target.value})}
                      className="w-full border border-purple-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-700 mb-2">Telegram</label>
                    <input
                      type="text"
                      placeholder="@yourusername"
                      value={socialLinks.telegram}
                      onChange={(e) => setSocialLinks({...socialLinks, telegram: e.target.value})}
                      className="w-full border border-purple-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-700 mb-2">Website</label>
                    <input
                      type="url"
                      placeholder="https://yourwebsite.com"
                      value={socialLinks.website}
                      onChange={(e) => setSocialLinks({...socialLinks, website: e.target.value})}
                      className="w-full border border-purple-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>
                <div className="flex justify-end mt-4">
                  <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-all">
                    Save Social Links
                  </button>
                </div>
              </motion.div>
            )}

            {/* Trading Highlights Form */}
            {showTradingHighlights && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-green-50 rounded-xl p-6"
              >
                <h3 className="text-lg font-bold text-green-800 mb-4">Add Trading Screenshots</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-green-700 mb-2">Upload P&L Screenshot</label>
                    <input
                      type="file"
                      accept="image/*"
                      className="w-full border border-green-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-green-700 mb-2">Title</label>
                    <input
                      type="text"
                      placeholder="e.g., My Best SOL Trade"
                      className="w-full border border-green-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-green-700 mb-2">Description</label>
                    <textarea
                      placeholder="Tell the story behind this trade..."
                      rows="3"
                      className="w-full border border-green-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-green-700 mb-2">Profit/Loss</label>
                      <input
                        type="text"
                        placeholder="e.g., +$5,000"
                        className="w-full border border-green-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-green-700 mb-2">Percentage Gain</label>
                      <input
                        type="text"
                        placeholder="e.g., +250%"
                        className="w-full border border-green-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  </div>
                </div>
                <div className="flex justify-end mt-4">
                  <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-all">
                    Save Trading Highlight
                  </button>
                </div>
              </motion.div>
            )}

            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {user.location && (
                <div className="text-center p-4 bg-gray-50 rounded-xl">
                  <h3 className="font-semibold text-gray-800 mb-2">📍 Location</h3>
                  <p className="text-gray-600">{user.location}</p>
                </div>
              )}
              
              {user.timezone && (
                <div className="text-center p-4 bg-gray-50 rounded-xl">
                  <h3 className="font-semibold text-gray-800 mb-2">🌍 Timezone</h3>
                  <p className="text-gray-600">{user.timezone}</p>
                </div>
              )}
            </div>

            {/* Trading Info */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-black">Trading Profile</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {user.trading_experience && (
                  <div className="p-4 bg-blue-50 rounded-xl">
                    <h4 className="font-semibold text-blue-800 mb-2">📈 Experience Level</h4>
                    <p className="text-blue-700">{user.trading_experience}</p>
                  </div>
                )}
                
                {user.years_trading && (
                  <div className="p-4 bg-green-50 rounded-xl">
                    <h4 className="font-semibold text-green-800 mb-2">⏱️ Years Trading</h4>
                    <p className="text-green-700">{user.years_trading} years</p>
                  </div>
                )}
                
                {user.trading_style && (
                  <div className="p-4 bg-purple-50 rounded-xl">
                    <h4 className="font-semibold text-purple-800 mb-2">🎯 Trading Style</h4>
                    <p className="text-purple-700">{user.trading_style}</p>
                  </div>
                )}
                
                {user.portfolio_size && (
                  <div className="p-4 bg-orange-50 rounded-xl">
                    <h4 className="font-semibold text-orange-800 mb-2">💼 Portfolio Size</h4>
                    <p className="text-orange-700">{user.portfolio_size}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Preferred Tokens */}
            {user.preferred_tokens && user.preferred_tokens.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-black mb-4">🪙 Preferred Tokens</h3>
                <div className="flex flex-wrap gap-2">
                  {user.preferred_tokens.map((token, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium"
                    >
                      {token}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Trading Goals */}
            {user.looking_for && user.looking_for.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-black mb-4">🎯 Trading Goals</h3>
                <div className="flex flex-wrap gap-2">
                  {user.looking_for.map((goal, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                    >
                      {goal}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Communication Preferences */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {user.communication_style && (
                <div className="p-4 bg-gray-50 rounded-xl">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">💬 Communication Style</h3>
                  <p className="text-gray-600">{user.communication_style}</p>
                </div>
              )}

              {user.trading_hours && (
                <div className="p-4 bg-gray-50 rounded-xl">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">⏰ Trading Hours</h3>
                  <p className="text-gray-600">{user.trading_hours}</p>
                </div>
              )}
            </div>

            {/* Close Button */}
            <div className="flex justify-center pt-4">
              <AnimatedButton
                onClick={onClose}
                variant="secondary"
                className="px-8"
              >
                Close Preview
              </AnimatedButton>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PublicProfileModal;