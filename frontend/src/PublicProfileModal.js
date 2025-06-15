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
          className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-black">Your Public Profile</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
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

            {/* Trading Platforms */}
            {user.preferred_platforms && user.preferred_platforms.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-black mb-4">🔧 Preferred Platforms</h3>
                <div className="flex flex-wrap gap-2">
                  {user.preferred_platforms.map((platform, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium"
                    >
                      {platform}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Goals */}
            {user.goals && user.goals.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-black mb-4">🎯 Goals</h3>
                <div className="flex flex-wrap gap-2">
                  {user.goals.map((goal, index) => (
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
            {user.communication_style && (
              <div className="p-4 bg-gray-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">💬 Communication Style</h3>
                <p className="text-gray-600">{user.communication_style}</p>
              </div>
            )}

            {/* Active Hours */}
            {user.active_hours && (
              <div className="p-4 bg-gray-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">⏰ Active Hours</h3>
                <p className="text-gray-600">{user.active_hours}</p>
              </div>
            )}

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
