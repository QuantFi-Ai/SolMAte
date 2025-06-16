import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const SubscriptionManager = ({ currentUser, onClose }) => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('overview');
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (currentUser) {
      fetchSubscriptionInfo();
    }
  }, [currentUser]);

  const fetchSubscriptionInfo = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planType) => {
    setIsProcessing(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/upgrade/${currentUser.user_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_type: planType })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`🎉 Successfully upgraded to ${planType.replace('_', ' ').toUpperCase()}!`);
        setShowUpgradeModal(false);
        fetchSubscriptionInfo();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to upgrade subscription');
      }
    } catch (error) {
      console.error('Error upgrading subscription:', error);
      alert('Failed to upgrade subscription');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDowngrade = async (planType) => {
    setIsProcessing(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/upgrade/${currentUser.user_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_type: planType })
      });

      if (response.ok) {
        alert(`✅ Successfully changed to ${planType.replace('_', ' ').toUpperCase()} plan!`);
        fetchSubscriptionInfo();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to change subscription');
      }
    } catch (error) {
      console.error('Error changing subscription:', error);
      alert('Failed to change subscription');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCancelSubscription = async () => {
    setIsProcessing(true);
    try {
      await handleDowngrade('free');
      setShowCancelConfirm(false);
      alert('Subscription cancelled. You will retain premium features until the end of your billing period.');
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      alert('Failed to cancel subscription');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsProcessing(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${currentUser.user_id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert('Account deleted successfully. You will be logged out.');
        // Redirect to login or home
        window.location.href = '/';
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to delete account');
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account');
    } finally {
      setIsProcessing(false);
    }
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      billing: 'Forever',
      description: 'Perfect for getting started',
      features: [
        '20 swipes per day',
        'Basic discovery',
        'Standard matching',
        'Basic messaging'
      ],
      limitations: [
        'No rewind swipes',
        'Cannot see who liked you',
        'No advanced filters',
        'No premium features'
      ]
    },
    {
      id: 'basic_premium',
      name: 'Basic Premium',
      price: '$9.99',
      billing: 'per month',
      description: 'Essential features for active traders',
      popular: true,
      features: [
        'Unlimited swipes',
        'See who liked you',
        'Rewind last swipe',
        'Advanced filters',
        'Priority in discovery',
        'Read receipts'
      ],
      limitations: [
        'No trading signals',
        'No group chats',
        'No portfolio verification',
        'No analytics'
      ]
    },
    {
      id: 'pro_trader',
      name: 'Pro Trader',
      price: '$19.99',
      billing: 'per month',
      description: 'Advanced features for serious traders',
      elite: true,
      features: [
        'All Basic Premium features',
        'Portfolio integration',
        'Trading signal sharing',
        'Create trading groups',
        'Trading calendar',
        'Performance analytics',
        'Priority support'
      ],
      limitations: []
    }
  ];

  const currentPlan = subscription?.subscription?.plan_type || 'free';
  const currentPlanData = plans.find(plan => plan.id === currentPlan);

  const sections = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'plans', label: 'Plans', icon: '💎' },
    { id: 'billing', label: 'Billing', icon: '🧾' },
    { id: 'account', label: 'Account', icon: '⚙️' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">Loading subscription details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      {/* Sidebar Navigation */}
      <div className="w-64 bg-gray-50 border-r border-gray-200 p-6">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-xl font-bold text-black">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 p-1 rounded-lg hover:bg-gray-200 transition-all"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="space-y-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all ${
                activeSection === section.id
                  ? 'bg-black text-white'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span className="text-lg">{section.icon}</span>
              <span>{section.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        {/* Overview Section */}
        {activeSection === 'overview' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-8"
          >
            <div>
              <h3 className="text-3xl font-bold text-black mb-2">Subscription Overview</h3>
              <p className="text-gray-600">Manage your SolM8 subscription and features</p>
            </div>

            {/* Current Plan Card */}
            <div className="bg-gradient-to-br from-black to-gray-800 text-white rounded-3xl p-8">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="text-4xl">
                      {currentPlan === 'free' && '🆓'}
                      {currentPlan === 'basic_premium' && '💎'}
                      {currentPlan === 'pro_trader' && '⚡'}
                    </div>
                    <div>
                      <h4 className="text-2xl font-bold mb-1">
                        {currentPlanData?.name || 'Free'}
                      </h4>
                      {currentPlan === 'basic_premium' && (
                        <span className="bg-blue-500 px-3 py-1 rounded-full text-sm font-medium">PREMIUM</span>
                      )}
                      {currentPlan === 'pro_trader' && (
                        <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-sm font-bold">PRO TRADER</span>
                      )}
                    </div>
                  </div>
                  <p className="text-gray-300 text-lg">
                    {currentPlan === 'free' ? 'Free plan' : `${currentPlanData?.price} ${currentPlanData?.billing}`}
                  </p>
                  {subscription?.subscription?.expires_at && (
                    <p className="text-gray-400 text-sm mt-2">
                      {subscription.subscription.status === 'active' ? 'Renews' : 'Expires'} on{' '}
                      {new Date(subscription.subscription.expires_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                    subscription?.subscription?.status === 'active' 
                      ? 'bg-green-500 text-white' 
                      : 'bg-gray-500 text-white'
                  }`}>
                    {subscription?.subscription?.status?.toUpperCase() || 'ACTIVE'}
                  </span>
                </div>
              </div>
            </div>

            {/* Usage Stats */}
            {subscription?.swipe_limits && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white border border-gray-200 rounded-2xl p-6 text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {subscription.swipe_limits.is_premium ? '∞' : subscription.swipe_limits.swipes_remaining}
                  </div>
                  <div className="text-gray-600 font-medium">Swipes Today</div>
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl p-6 text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {subscription.premium_features.see_who_liked_you ? '✓' : '✗'}
                  </div>
                  <div className="text-gray-600 font-medium">See Likes</div>
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl p-6 text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">
                    {subscription.premium_features.rewind_swipes ? '✓' : '✗'}
                  </div>
                  <div className="text-gray-600 font-medium">Rewind</div>
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl p-6 text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-2">
                    {subscription.pro_trader_features?.trading_signals ? '✓' : '✗'}
                  </div>
                  <div className="text-gray-600 font-medium">Pro Features</div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Plans Section */}
        {activeSection === 'plans' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-8"
          >
            <div>
              <h3 className="text-3xl font-bold text-black mb-2">Choose Your Plan</h3>
              <p className="text-gray-600">Select the perfect plan for your trading needs</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className={`border-2 rounded-3xl p-8 relative transition-all hover:shadow-lg ${
                    plan.id === currentPlan
                      ? 'border-black bg-gray-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  } ${plan.popular ? 'border-blue-500' : ''} ${plan.elite ? 'border-yellow-500' : ''}`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-6 py-2 rounded-full text-sm font-bold">
                      MOST POPULAR
                    </div>
                  )}
                  {plan.elite && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-black px-6 py-2 rounded-full text-sm font-bold">
                      ELITE
                    </div>
                  )}

                  <div className="text-center mb-8">
                    <h5 className="text-2xl font-bold text-black mb-2">{plan.name}</h5>
                    <p className="text-gray-600 mb-4">{plan.description}</p>
                    <div className="text-4xl font-bold text-black mb-2">
                      {plan.price}
                      {plan.id !== 'free' && <span className="text-lg text-gray-600">/{plan.billing.split(' ')[1]}</span>}
                    </div>
                    {plan.id !== 'free' && (
                      <div className="text-gray-600">{plan.billing}</div>
                    )}
                  </div>

                  {plan.id === currentPlan && (
                    <div className="text-center mb-6">
                      <span className="bg-black text-white px-6 py-3 rounded-full font-medium">
                        Current Plan
                      </span>
                    </div>
                  )}

                  <div className="space-y-4 mb-8">
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <span className="text-green-500 font-bold">✓</span>
                        <span className="text-gray-700">{feature}</span>
                      </div>
                    ))}
                    {plan.limitations.map((limitation, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <span className="text-red-500 font-bold">✗</span>
                        <span className="text-gray-500">{limitation}</span>
                      </div>
                    ))}
                  </div>

                  {plan.id !== currentPlan && (
                    <AnimatedButton
                      onClick={() => {
                        setSelectedPlan(plan.id);
                        setShowUpgradeModal(true);
                      }}
                      className={`w-full py-4 rounded-xl font-semibold transition-all ${
                        plan.id === 'free'
                          ? 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                          : 'bg-black hover:bg-gray-800 text-white'
                      }`}
                    >
                      {plan.id === 'free' ? 'Downgrade to Free' : `Upgrade to ${plan.name}`}
                    </AnimatedButton>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Billing Section */}
        {activeSection === 'billing' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-8"
          >
            <div>
              <h3 className="text-3xl font-bold text-black mb-2">Billing & Payments</h3>
              <p className="text-gray-600">Manage your billing information and payment methods</p>
            </div>

            {/* Current Subscription */}
            <div className="bg-white border border-gray-200 rounded-2xl p-8">
              <h4 className="text-xl font-bold text-black mb-6">Current Subscription</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">Plan</label>
                  <div className="text-lg font-semibold text-black">{currentPlanData?.name}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">Amount</label>
                  <div className="text-lg font-semibold text-black">
                    {currentPlan === 'free' ? 'Free' : `${currentPlanData?.price} ${currentPlanData?.billing}`}
                  </div>
                </div>
                {subscription?.subscription?.expires_at && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-2">Next Billing Date</label>
                      <div className="text-lg font-semibold text-black">
                        {new Date(subscription.subscription.expires_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-2">Status</label>
                      <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                        subscription.subscription.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {subscription.subscription.status?.toUpperCase()}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Cancel Subscription */}
            {currentPlan !== 'free' && (
              <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8">
                <h4 className="text-xl font-bold text-red-800 mb-4">Cancel Subscription</h4>
                <p className="text-red-600 mb-6">
                  Cancel your subscription and downgrade to the free plan. You'll retain access to premium features until the end of your current billing period.
                </p>
                <button
                  onClick={() => setShowCancelConfirm(true)}
                  className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-xl font-semibold transition-all"
                >
                  Cancel Subscription
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Account Section */}
        {activeSection === 'account' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-8"
          >
            <div>
              <h3 className="text-3xl font-bold text-black mb-2">Account Settings</h3>
              <p className="text-gray-600">Manage your account and data preferences</p>
            </div>

            {/* Account Info */}
            <div className="bg-white border border-gray-200 rounded-2xl p-8">
              <h4 className="text-xl font-bold text-black mb-6">Account Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">Display Name</label>
                  <div className="text-lg font-semibold text-black">{currentUser?.display_name}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">Username</label>
                  <div className="text-lg font-semibold text-black">@{currentUser?.username}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">Email</label>
                  <div className="text-lg font-semibold text-black">{currentUser?.email || 'Not provided'}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">Member Since</label>
                  <div className="text-lg font-semibold text-black">
                    {currentUser?.created_at ? new Date(currentUser.created_at).toLocaleDateString() : 'Unknown'}
                  </div>
                </div>
              </div>
            </div>

            {/* Data Export */}
            <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-8">
              <h4 className="text-xl font-bold text-blue-800 mb-4">Export Your Data</h4>
              <p className="text-blue-600 mb-6">
                Download a copy of all your data including profile information, matches, and messages.
              </p>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold transition-all">
                Request Data Export
              </button>
            </div>

            {/* Danger Zone */}
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8">
              <h4 className="text-xl font-bold text-red-800 mb-4">Danger Zone</h4>
              <div className="space-y-6">
                <div>
                  <h5 className="font-semibold text-red-700 mb-2">Delete Account</h5>
                  <p className="text-red-600 text-sm mb-4">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-xl font-semibold transition-all"
                  >
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Modals */}
      <AnimatePresence>
        {showUpgradeModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[100] overflow-y-auto"
            onClick={() => setShowUpgradeModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-8 max-w-md w-full max-h-[90vh] overflow-y-auto my-8"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-2xl font-bold text-black mb-4">
                {selectedPlan === 'free' ? 'Downgrade' : 'Upgrade'} Subscription
              </h3>
              <p className="text-gray-600 mb-8">
                {selectedPlan === 'free' 
                  ? 'Are you sure you want to downgrade to the free plan? You will lose access to premium features.'
                  : `Upgrade to ${plans.find(p => p.id === selectedPlan)?.name} for ${plans.find(p => p.id === selectedPlan)?.price} ${plans.find(p => p.id === selectedPlan)?.billing}?`
                }
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={() => setShowUpgradeModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-xl font-semibold transition-all"
                >
                  Cancel
                </button>
                <AnimatedButton
                  onClick={() => selectedPlan === 'free' ? handleDowngrade(selectedPlan) : handleUpgrade(selectedPlan)}
                  disabled={isProcessing}
                  className={`flex-1 py-3 rounded-xl font-semibold transition-all ${
                    selectedPlan === 'free'
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-black hover:bg-gray-800 text-white'
                  }`}
                >
                  {isProcessing ? 'Processing...' : 'Confirm'}
                </AnimatedButton>
              </div>
            </motion.div>
          </motion.div>
        )}

        {showCancelConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]"
            onClick={() => setShowCancelConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center">
                <div className="text-6xl mb-4">😢</div>
                <h3 className="text-2xl font-bold text-black mb-4">Cancel Subscription?</h3>
                <p className="text-gray-600 mb-8">
                  We're sorry to see you go! You'll retain access to premium features until{' '}
                  {subscription?.subscription?.expires_at && 
                    new Date(subscription.subscription.expires_at).toLocaleDateString()
                  }.
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={() => setShowCancelConfirm(false)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-xl font-semibold transition-all"
                  >
                    Keep Subscription
                  </button>
                  <button
                    onClick={handleCancelSubscription}
                    disabled={isProcessing}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-xl font-semibold transition-all"
                  >
                    {isProcessing ? 'Cancelling...' : 'Cancel Subscription'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]"
            onClick={() => setShowDeleteConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-2xl font-bold text-red-600 mb-4">Delete Account?</h3>
                <p className="text-gray-600 mb-8">
                  This action is <strong>permanent</strong> and cannot be undone. All your data, matches, messages, and profile will be permanently deleted.
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-xl font-semibold transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteAccount}
                    disabled={isProcessing}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-xl font-semibold transition-all"
                  >
                    {isProcessing ? 'Deleting...' : 'Delete Account'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SubscriptionManager;