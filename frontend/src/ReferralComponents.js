import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton, AnimatedCard, LoadingDots, ToastNotification } from './AnimatedComponents';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Referral Dashboard Modal
export const ReferralDashboard = ({ isOpen, onClose, currentUser }) => {
  const [referralStats, setReferralStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  useEffect(() => {
    if (isOpen && currentUser) {
      fetchReferralStats();
    }
  }, [isOpen, currentUser]);

  const fetchReferralStats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/referrals/stats/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setReferralStats(data);
      } else {
        showToastMessage('Failed to load referral stats');
      }
    } catch (error) {
      console.error('Error fetching referral stats:', error);
      showToastMessage('Failed to load referral stats');
    } finally {
      setLoading(false);
    }
  };

  const generateReferralCode = async () => {
    setGenerating(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/referrals/generate/${currentUser.user_id}`, {
        method: 'POST'
      });
      if (response.ok) {
        await fetchReferralStats();
        showToastMessage('Referral code generated successfully!');
      } else {
        showToastMessage('Failed to generate referral code');
      }
    } catch (error) {
      console.error('Error generating referral code:', error);
      showToastMessage('Failed to generate referral code');
    } finally {
      setGenerating(false);
    }
  };

  const copyReferralLink = async () => {
    if (referralStats?.referral_link) {
      try {
        await navigator.clipboard.writeText(referralStats.referral_link);
        setCopied(true);
        showToastMessage('Referral link copied to clipboard!');
        setTimeout(() => setCopied(false), 2000);
      } catch (error) {
        console.error('Failed to copy:', error);
        showToastMessage('Failed to copy link');
      }
    }
  };

  const shareReferralLink = async () => {
    if (navigator.share && referralStats?.referral_link) {
      try {
        await navigator.share({
          title: 'Join Solm8 - Connect with Crypto Traders',
          text: 'Join me on Solm8, the premier platform for crypto traders to connect and collaborate!',
          url: referralStats.referral_link,
        });
      } catch (error) {
        console.log('Error sharing:', error);
        copyReferralLink();
      }
    } else {
      copyReferralLink();
    }
  };

  const showToastMessage = (message) => {
    setToastMessage(message);
    setShowToast(true);
  };

  if (!isOpen) return null;

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
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-black">Referral Dashboard</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <LoadingDots size="lg" />
              <p className="text-gray-600 mt-4">Loading referral data...</p>
            </div>
          ) : (
            <div className="space-y-6">
              {referralStats?.referral_code ? (
                <AnimatedCard className="p-6">
                  <h3 className="text-lg font-semibold text-black mb-4">Your Referral Link</h3>
                  <div className="bg-gray-50 p-4 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      <code className="flex-1 text-sm text-gray-700 break-all">
                        {referralStats.referral_link}
                      </code>
                      <div className="flex space-x-2">
                        <AnimatedButton
                          onClick={copyReferralLink}
                          variant="secondary"
                          className="text-sm py-2 px-3"
                        >
                          {copied ? '✓ Copied' : 'Copy'}
                        </AnimatedButton>
                        <AnimatedButton
                          onClick={shareReferralLink}
                          className="text-sm py-2 px-3"
                        >
                          Share
                        </AnimatedButton>
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    Share this link with friends to earn referral rewards!
                  </p>
                </AnimatedCard>
              ) : (
                <AnimatedCard className="p-6 text-center">
                  <h3 className="text-lg font-semibold text-black mb-4">Generate Your Referral Code</h3>
                  <p className="text-gray-600 mb-4">
                    Create your unique referral link to start inviting friends and earning rewards.
                  </p>
                  <AnimatedButton
                    onClick={generateReferralCode}
                    disabled={generating}
                    className="mx-auto"
                  >
                    {generating ? (
                      <div className="flex items-center space-x-2">
                        <LoadingDots />
                        <span>Generating...</span>
                      </div>
                    ) : (
                      'Generate Referral Code'
                    )}
                  </AnimatedButton>
                </AnimatedCard>
              )}

              {referralStats && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <AnimatedCard className="p-6 text-center">
                    <div className="text-3xl font-bold text-blue-600">
                      {referralStats.total_referrals}
                    </div>
                    <div className="text-sm text-gray-600">Total Referrals</div>
                  </AnimatedCard>
                  
                  <AnimatedCard className="p-6 text-center">
                    <div className="text-3xl font-bold text-green-600">
                      {referralStats.successful_signups}
                    </div>
                    <div className="text-sm text-gray-600">Active Users</div>
                  </AnimatedCard>
                  
                  <AnimatedCard className="p-6 text-center">
                    <div className="text-3xl font-bold text-orange-600">
                      {referralStats.pending_signups}
                    </div>
                    <div className="text-sm text-gray-600">Pending Setup</div>
                  </AnimatedCard>
                </div>
              )}

              {referralStats?.referred_users && referralStats.referred_users.length > 0 && (
                <AnimatedCard className="p-6">
                  <h3 className="text-lg font-semibold text-black mb-4">
                    Your Referrals ({referralStats.referred_users.length})
                  </h3>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {referralStats.referred_users.map((user, index) => (
                      <motion.div
                        key={user.user_id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                      >
                        <img
                          src={user.avatar_url}
                          alt={user.display_name}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                        <div className="flex-1">
                          <div className="font-medium text-black">{user.display_name}</div>
                          <div className="text-sm text-gray-600">@{user.username}</div>
                        </div>
                        <div className="text-right">
                          <div className={`text-xs px-2 py-1 rounded-full ${
                            user.profile_complete 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {user.profile_complete ? 'Active' : 'Setting up'}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {new Date(user.joined_at).toLocaleDateString()}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </AnimatedCard>
              )}

              <AnimatedCard className="p-6">
                <h3 className="text-lg font-semibold text-black mb-4">How Referrals Work</h3>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">1</div>
                    <div>
                      <div className="font-medium text-black">Share Your Link</div>
                      <div className="text-sm text-gray-600">Send your unique referral link to friends and fellow traders</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">2</div>
                    <div>
                      <div className="font-medium text-black">They Sign Up</div>
                      <div className="text-sm text-gray-600">When someone uses your link to join Solm8, you both benefit</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">3</div>
                    <div>
                      <div className="font-medium text-black">Earn Rewards</div>
                      <div className="text-sm text-gray-600">Get premium features, priority matching, and exclusive benefits</div>
                    </div>
                  </div>
                </div>
              </AnimatedCard>
            </div>
          )}
        </motion.div>

        <ToastNotification
          message={toastMessage}
          type="success"
          isVisible={showToast}
          onClose={() => setShowToast(false)}
        />
      </motion.div>
    </AnimatePresence>
  );
};

// Support Modal
export const SupportModal = ({ isOpen, onClose }) => {
  const [selectedTopic, setSelectedTopic] = useState('');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [sending, setSending] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const supportTopics = [
    'Account Issues',
    'Technical Problems',
    'Matching Issues',
    'Payment & Billing',
    'Privacy & Safety',
    'Feature Request',
    'Other'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);
    
    setTimeout(() => {
      setSending(false);
      setShowToast(true);
      setSelectedTopic('');
      setMessage('');
      setEmail('');
      
      setTimeout(() => {
        onClose();
      }, 2000);
    }, 1500);
  };

  if (!isOpen) return null;

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
          className="bg-white rounded-2xl p-6 max-w-md w-full"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-black">Contact Support</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What can we help you with?
              </label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent"
              >
                <option value="">Select a topic</option>
                {supportTopics.map(topic => (
                  <option key={topic} value={topic}>{topic}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Describe your issue
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
                rows={4}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-black focus:ring-2 focus:ring-black focus:border-transparent"
                placeholder="Please provide as much detail as possible..."
              />
            </div>

            <AnimatedButton
              type="submit"
              disabled={sending}
              className="w-full"
            >
              {sending ? (
                <div className="flex items-center justify-center space-x-2">
                  <LoadingDots />
                  <span>Sending...</span>
                </div>
              ) : (
                'Send Support Request'
              )}
            </AnimatedButton>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              Need immediate help? Email us at{' '}
              <a href="mailto:support@solm8.com" className="text-blue-600 hover:underline">
                support@solm8.com
              </a>
            </p>
          </div>

          <ToastNotification
            message="Support request sent successfully! We'll get back to you soon."
            type="success"
            isVisible={showToast}
            onClose={() => setShowToast(false)}
          />
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
