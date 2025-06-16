import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const ProTraderModal = ({ isOpen, onClose, onUpgrade, currentUser }) => {
  const [isUpgrading, setIsUpgrading] = useState(false);

  if (!isOpen) return null;

  const handleUpgrade = async () => {
    setIsUpgrading(true);
    try {
      await onUpgrade('pro_trader');
      onClose();
    } catch (error) {
      console.error('Upgrade failed:', error);
    } finally {
      setIsUpgrading(false);
    }
  };

  const basicFeatures = [
    '🚀 Unlimited swipes',
    '👀 See who liked you',
    '⏪ Rewind last swipe',
    '🎯 Advanced filters',
    '⭐ Priority discovery'
  ];

  const proTraderFeatures = [
    {
      icon: '💼',
      title: 'Portfolio Integration',
      description: 'Connect your wallet/exchange for verified portfolio size',
      benefit: 'Build trust with verified trading credentials'
    },
    {
      icon: '📡',
      title: 'Trading Signal Sharing',
      description: 'Send encrypted trade alerts to your network',
      benefit: 'Share alpha and get trade ideas from experts'
    },
    {
      icon: '👥',
      title: 'Trading Groups',
      description: 'Create groups with up to 10 matched traders',
      benefit: 'Build exclusive trading communities'
    },
    {
      icon: '📅',
      title: 'Trading Calendar',
      description: 'Schedule trading sessions and strategy calls',
      benefit: 'Coordinate with your trading network'
    },
    {
      icon: '📊',
      title: 'Performance Analytics',
      description: 'Track your matching success and profile metrics',
      benefit: 'Optimize your profile for better connections'
    }
  ];

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
          {/* Header */}
          <div className="bg-gradient-to-r from-black via-gray-800 to-black text-white p-8">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-4xl">⚡</span>
                  <h2 className="text-3xl font-bold">Pro Trader</h2>
                  <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-sm font-bold">ELITE</span>
                </div>
                <p className="text-gray-300 text-lg">Advanced features for serious traders</p>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-300 text-2xl p-2"
              >
                ×
              </button>
            </div>
          </div>

          {/* Pricing Comparison */}
          <div className="p-8 bg-gray-50 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Free Tier */}
              <div className="text-center p-4 bg-white rounded-xl border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Current Plan</div>
                <div className="text-xl font-bold text-gray-700">Free</div>
                <div className="text-gray-500">$0/month</div>
                <div className="text-sm text-red-500 mt-2">Limited features</div>
              </div>

              {/* Basic Premium */}
              <div className="text-center p-4 bg-white rounded-xl border border-gray-300">
                <div className="text-gray-600 text-sm mb-1">Basic Premium</div>
                <div className="text-xl font-bold text-gray-800">Premium</div>
                <div className="text-gray-600">$9.99/month</div>
                <div className="text-sm text-blue-600 mt-2">Essential features</div>
              </div>

              {/* Pro Trader */}
              <div className="text-center p-6 bg-black text-white rounded-xl border-2 border-yellow-500 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-black px-4 py-1 rounded-full text-xs font-bold">
                  RECOMMENDED
                </div>
                <div className="text-yellow-400 text-sm mb-1">Upgrade To</div>
                <div className="text-2xl font-bold">Pro Trader</div>
                <div className="text-lg text-yellow-400">$19.99/month</div>
                <div className="text-sm text-green-400 mt-2">All features included</div>
              </div>
            </div>
          </div>

          <div className="p-8 overflow-y-auto max-h-[60vh]">
            {/* What's Included */}
            <div className="mb-8">
              <h3 className="text-xl font-bold text-center mb-4">What's Included with Pro Trader</h3>
              
              {/* Basic Premium Features */}
              <div className="bg-blue-50 rounded-xl p-6 mb-6">
                <h4 className="font-bold text-blue-800 mb-3 flex items-center">
                  <span className="text-2xl mr-2">💎</span>
                  All Basic Premium Features
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {basicFeatures.map((feature, index) => (
                    <div key={index} className="text-blue-700 text-sm flex items-center">
                      <span className="mr-2">✓</span>
                      {feature}
                    </div>
                  ))}
                </div>
              </div>

              {/* Pro Trader Exclusive Features */}
              <div className="space-y-4">
                <h4 className="font-bold text-black mb-4 flex items-center">
                  <span className="text-2xl mr-2">⚡</span>
                  PLUS Pro Trader Exclusive Features
                </h4>
                
                {proTraderFeatures.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all"
                  >
                    <div className="flex items-start space-x-4">
                      <div className="text-4xl">{feature.icon}</div>
                      <div className="flex-1">
                        <h5 className="font-bold text-black text-lg mb-2">{feature.title}</h5>
                        <p className="text-gray-600 mb-2">{feature.description}</p>
                        <p className="text-green-600 text-sm font-medium">
                          💡 {feature.benefit}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Success Stories */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 mb-8">
              <div className="text-center">
                <div className="text-4xl mb-3">🎯</div>
                <h4 className="font-bold text-gray-800 mb-3">Join Elite Traders</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-green-600">5x</div>
                    <div className="text-sm text-gray-600">More Quality Matches</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">85%</div>
                    <div className="text-sm text-gray-600">Success Rate</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-600">500+</div>
                    <div className="text-sm text-gray-600">Pro Traders</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Value Proposition */}
            <div className="bg-black text-white rounded-xl p-6 mb-8">
              <h4 className="font-bold mb-4 text-center">Why Pro Traders Choose SolM8</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">✓</span>
                  <span>Verified portfolio credentials</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">✓</span>
                  <span>Exclusive alpha sharing network</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">✓</span>
                  <span>Private trading groups</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">✓</span>
                  <span>Real-time performance tracking</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <button
                onClick={onClose}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-4 rounded-xl font-semibold transition-all"
              >
                Maybe Later
              </button>
              <AnimatedButton
                onClick={handleUpgrade}
                disabled={isUpgrading}
                className="flex-1 bg-black hover:bg-gray-800 text-white py-4 rounded-xl font-semibold transition-all"
              >
                {isUpgrading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Upgrading...
                  </span>
                ) : (
                  `Upgrade to Pro Trader - $19.99/month`
                )}
              </AnimatedButton>
            </div>

            {/* Guarantee */}
            <div className="text-center mt-6">
              <p className="text-gray-500 text-sm">
                ✅ 7-day free trial • Cancel anytime • 30-day money-back guarantee
              </p>
              <p className="text-gray-400 text-xs mt-1">
                Join the elite trading network today
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ProTraderModal;