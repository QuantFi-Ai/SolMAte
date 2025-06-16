import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const SubscriptionManager = ({ currentUser, onClose }) => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
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
        alert(`Successfully upgraded to ${planType.replace('_', ' ').toUpperCase()}!`);
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
        alert(`Successfully changed to ${planType.replace('_', ' ').toUpperCase()} plan!`);
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

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      billing: 'Forever',
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

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black">Subscription Management</h2>
          <p className="text-gray-600">Manage your SolM8 subscription and billing</p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 text-2xl"
        >
          ×
        </button>
      </div>

      <div className="bg-gradient-to-r from-black to-gray-800 text-white rounded-2xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-xl font-bold">
                {currentPlanData?.name || 'Free'}
              </h3>
              {currentPlan === 'basic_premium' && (
                <span className="bg-blue-500 px-3 py-1 rounded-full text-sm font-medium">PREMIUM</span>
              )}
              {currentPlan === 'pro_trader' && (
                <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-sm font-bold">PRO TRADER</span>
              )}
            </div>
            <p className="text-gray-300">
              {currentPlan === 'free' ? 'Free plan' : `${currentPlanData?.price} ${currentPlanData?.billing}`}
            </p>
            {subscription?.subscription?.expires_at && (
              <p className="text-gray-400 text-sm mt-1">
                {subscription.subscription.status === 'active' ? 'Renews' : 'Expires'} on{' '}
                {new Date(subscription.subscription.expires_at).toLocaleDateString()}
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-3xl mb-2">
              {currentPlan === 'free' && '🆓'}
              {currentPlan === 'basic_premium' && '💎'}
              {currentPlan === 'pro_trader' && '⚡'}
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              subscription?.subscription?.status === 'active' 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-500 text-white'
            }`}>
              {subscription?.subscription?.status?.toUpperCase() || 'ACTIVE'}
            </span>
          </div>
        </div>
      </div>

      {subscription?.swipe_limits && (
        <div className="bg-gray-50 rounded-xl p-6">
          <h4 className="font-bold text-black mb-4">Usage This Month</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {subscription.swipe_limits.is_premium ? '∞' : subscription.swipe_limits.swipes_remaining}
              </div>
              <div className="text-gray-600 text-sm">Swipes Remaining</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {subscription.premium_features.see_who_liked_you ? 'Enabled' : 'Disabled'}
              </div>
              <div className="text-gray-600 text-sm">See Likes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {subscription.premium_features.rewind_swipes ? 'Enabled' : 'Disabled'}
              </div>
              <div className="text-gray-600 text-sm">Rewind</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {subscription.pro_trader_features?.trading_signals ? 'Enabled' : 'Disabled'}
              </div>
              <div className="text-gray-600 text-sm">Signals</div>
            </div>
          </div>
        </div>
      )}

      <div>
        <h4 className="font-bold text-black mb-4">Available Plans</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`border rounded-2xl p-6 relative ${
                plan.id === currentPlan
                  ? 'border-black bg-gray-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              } ${plan.popular ? 'border-blue-500' : ''} ${plan.elite ? 'border-yellow-500' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-xs font-bold">
                  MOST POPULAR
                </div>
              )}
              {plan.elite && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-black px-4 py-1 rounded-full text-xs font-bold">
                  ELITE
                </div>
              )}

              <div className="text-center mb-6">
                <h5 className="text-lg font-bold text-black mb-2">{plan.name}</h5>
                <div className="text-3xl font-bold text-black">
                  {plan.price}
                  {plan.id !== 'free' && <span className="text-lg text-gray-600">/{plan.billing.split(' ')[1]}</span>}
                </div>
                {plan.id !== 'free' && (
                  <div className="text-gray-600 text-sm">{plan.billing}</div>
                )}
              </div>

              {plan.id === currentPlan && (
                <div className="text-center mb-4">
                  <span className="bg-black text-white px-4 py-2 rounded-full text-sm font-medium">
                    Current Plan
                  </span>
                </div>
              )}

              <div className="space-y-3 mb-6">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-green-500 text-sm">✓</span>
                    <span className="text-gray-700 text-sm">{feature}</span>
                  </div>
                ))}
                {plan.limitations.map((limitation, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-red-500 text-sm">✗</span>
                    <span className="text-gray-500 text-sm">{limitation}</span>
                  </div>
                ))}
              </div>

              {plan.id !== currentPlan && (
                <AnimatedButton
                  onClick={() => {
                    setSelectedPlan(plan.id);
                    setShowUpgradeModal(true);
                  }}
                  className={`w-full py-3 rounded-lg font-semibold transition-all ${
                    plan.id === 'free'
                      ? 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                      : 'bg-black hover:bg-gray-800 text-white'
                  }`}
                >
                  {plan.id === 'free' ? 'Downgrade' : 'Upgrade'}
                </AnimatedButton>
              )}
            </div>
          ))}
        </div>
      </div>

      {currentPlan !== 'free' && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <h4 className="font-bold text-red-800 mb-2">Cancel Subscription</h4>
          <p className="text-red-600 text-sm mb-4">
            You'll retain access to premium features until the end of your current billing period.
          </p>
          <button
            onClick={() => setShowCancelConfirm(true)}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-semibold transition-all"
          >
            Cancel Subscription
          </button>
        </div>
      )}

      <AnimatePresence>
        {showUpgradeModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowUpgradeModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-black mb-4">
                {selectedPlan === 'free' ? 'Downgrade' : 'Upgrade'} Subscription
              </h3>
              <p className="text-gray-600 mb-6">
                {selectedPlan === 'free' 
                  ? 'Are you sure you want to downgrade to the free plan? You will lose access to premium features.'
                  : `Upgrade to ${plans.find(p => p.id === selectedPlan)?.name} for ${plans.find(p => p.id === selectedPlan)?.price} ${plans.find(p => p.id === selectedPlan)?.billing}?`
                }
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={() => setShowUpgradeModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-lg font-semibold transition-all"
                >
                  Cancel
                </button>
                <AnimatedButton
                  onClick={() => selectedPlan === 'free' ? handleDowngrade(selectedPlan) : handleUpgrade(selectedPlan)}
                  disabled={isProcessing}
                  className={`flex-1 py-3 rounded-lg font-semibold transition-all ${
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
      </AnimatePresence>

      <AnimatePresence>
        {showCancelConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowCancelConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center">
                <div className="text-4xl mb-4">😢</div>
                <h3 className="text-xl font-bold text-black mb-4">Cancel Subscription?</h3>
                <p className="text-gray-600 mb-6">
                  We're sorry to see you go! You'll retain access to premium features until{' '}
                  {subscription?.subscription?.expires_at && 
                    new Date(subscription.subscription.expires_at).toLocaleDateString()
                  }.
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={() => setShowCancelConfirm(false)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-lg font-semibold transition-all"
                  >
                    Keep Subscription
                  </button>
                  <button
                    onClick={handleCancelSubscription}
                    disabled={isProcessing}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg font-semibold transition-all"
                  >
                    {isProcessing ? 'Cancelling...' : 'Cancel Subscription'}
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