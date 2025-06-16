import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const TradingSignals = ({ currentUser, onUpgrade }) => {
  const [signals, setSignals] = useState([]);
  const [activeTab, setActiveTab] = useState('received'); // 'received' or 'sent'
  const [showCreateSignal, setShowCreateSignal] = useState(false);
  const [matches, setMatches] = useState([]);
  const [newSignal, setNewSignal] = useState({
    recipient_ids: [],
    signal_type: 'alert',
    token_symbol: '',
    price_target: '',
    stop_loss: '',
    risk_level: 'medium',
    message: ''
  });
  const [isProTrader, setIsProTrader] = useState(false);

  useEffect(() => {
    if (currentUser) {
      checkSubscription();
      fetchSignals();
      fetchMatches();
    }
  }, [currentUser, activeTab]);

  const checkSubscription = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/subscription/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setIsProTrader(data.subscription.plan_type === 'pro_trader');
      }
    } catch (error) {
      console.error('Error checking subscription:', error);
    }
  };

  const fetchSignals = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/trading-signals/${currentUser.user_id}?signal_type=${activeTab}`);
      if (response.ok) {
        const data = await response.json();
        setSignals(data.signals || []);
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
    }
  };

  const fetchMatches = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/matches/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setMatches(data || []);
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const handleCreateSignal = async () => {
    if (!isProTrader) {
      onUpgrade('pro_trader');
      return;
    }

    try {
      const signalData = {
        ...newSignal,
        sender_id: currentUser.user_id,
        price_target: newSignal.price_target ? parseFloat(newSignal.price_target) : null,
        stop_loss: newSignal.stop_loss ? parseFloat(newSignal.stop_loss) : null
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/trading-signal/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signalData)
      });

      if (response.ok) {
        const data = await response.json();
        alert('Trading signal sent successfully!');
        setShowCreateSignal(false);
        setNewSignal({
          recipient_ids: [],
          signal_type: 'alert',
          token_symbol: '',
          price_target: '',
          stop_loss: '',
          risk_level: 'medium',
          message: ''
        });
        fetchSignals(); // Refresh signals
      } else {
        const error = await response.json();
        alert(error.message || 'Failed to send signal');
      }
    } catch (error) {
      console.error('Error sending signal:', error);
      alert('Failed to send signal');
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getSignalTypeIcon = (type) => {
    switch (type) {
      case 'entry': return '📈';
      case 'exit': return '📉';
      case 'analysis': return '🔍';
      default: return '🚨';
    }
  };

  if (!isProTrader) {
    return (
      <div className="bg-white rounded-2xl p-8 border border-gray-200">
        <div className="text-center">
          <div className="text-6xl mb-4">⚡</div>
          <h3 className="text-2xl font-bold text-black mb-4">Trading Signals</h3>
          <p className="text-gray-600 mb-6">
            Send encrypted trade alerts and alpha to your trading network. Share opportunities and get signals from other Pro Traders.
          </p>
          <div className="bg-gray-50 rounded-xl p-6 mb-6">
            <h4 className="font-bold text-black mb-3">Pro Trader Features:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span>Send real-time trade alerts</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span>Encrypted signal sharing</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span>Price targets & stop losses</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-500">✓</span>
                <span>Risk level indicators</span>
              </div>
            </div>
          </div>
          <AnimatedButton
            onClick={() => onUpgrade('pro_trader')}
            className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-xl font-semibold"
          >
            Upgrade to Pro Trader - $19.99/month
          </AnimatedButton>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">📡</span>
          <h2 className="text-2xl font-bold text-black">Trading Signals</h2>
          <span className="bg-black text-white px-3 py-1 rounded-full text-sm font-medium">PRO</span>
        </div>
        <AnimatedButton
          onClick={() => setShowCreateSignal(true)}
          className="bg-black hover:bg-gray-800 text-white px-6 py-2 rounded-lg font-medium"
        >
          + Send Signal
        </AnimatedButton>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveTab('received')}
          className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${
            activeTab === 'received'
              ? 'bg-white text-black shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Received Signals
        </button>
        <button
          onClick={() => setActiveTab('sent')}
          className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${
            activeTab === 'sent'
              ? 'bg-white text-black shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Sent Signals
        </button>
      </div>

      {/* Signals List */}
      <div className="space-y-4">
        {signals.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-xl">
            <div className="text-4xl mb-4">📡</div>
            <p className="text-gray-600">
              {activeTab === 'received' ? 'No signals received yet' : 'No signals sent yet'}
            </p>
            <p className="text-gray-500 text-sm mt-2">
              {activeTab === 'received' 
                ? 'Signals from your trading network will appear here'
                : 'Share your next alpha with your matches'
              }
            </p>
          </div>
        ) : (
          signals.map((signal, index) => (
            <motion.div
              key={signal.signal_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getSignalTypeIcon(signal.signal_type)}</span>
                  <div>
                    <h4 className="font-bold text-black">
                      {signal.token_symbol} - {signal.signal_type.charAt(0).toUpperCase() + signal.signal_type.slice(1)}
                    </h4>
                    {signal.sender_info && (
                      <p className="text-gray-600 text-sm">
                        From: {signal.sender_info.display_name} (@{signal.sender_info.username})
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(signal.risk_level)}`}>
                    {signal.risk_level.toUpperCase()} RISK
                  </span>
                  <span className="text-gray-500 text-xs">
                    {new Date(signal.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <p className="text-gray-700 mb-4">{signal.message}</p>

              {(signal.price_target || signal.stop_loss) && (
                <div className="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
                  {signal.price_target && (
                    <div>
                      <span className="text-gray-600 text-sm">Price Target:</span>
                      <div className="font-semibold text-green-600">${signal.price_target}</div>
                    </div>
                  )}
                  {signal.stop_loss && (
                    <div>
                      <span className="text-gray-600 text-sm">Stop Loss:</span>
                      <div className="font-semibold text-red-600">${signal.stop_loss}</div>
                    </div>
                  )}
                </div>
              )}

              {signal.expires_at && (
                <div className="mt-4 text-xs text-gray-500">
                  Expires: {new Date(signal.expires_at).toLocaleDateString()}
                </div>
              )}
            </motion.div>
          ))
        )}
      </div>

      {/* Create Signal Modal */}
      <AnimatePresence>
        {showCreateSignal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowCreateSignal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-black">Send Trading Signal</h3>
                <button
                  onClick={() => setShowCreateSignal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-black mb-2">Token Symbol</label>
                    <input
                      type="text"
                      placeholder="e.g., SOL, BTC, ETH"
                      value={newSignal.token_symbol}
                      onChange={(e) => setNewSignal({...newSignal, token_symbol: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-black mb-2">Signal Type</label>
                    <select
                      value={newSignal.signal_type}
                      onChange={(e) => setNewSignal({...newSignal, signal_type: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                    >
                      <option value="alert">Alert</option>
                      <option value="entry">Entry Signal</option>
                      <option value="exit">Exit Signal</option>
                      <option value="analysis">Analysis</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-black mb-2">Recipients</label>
                  <div className="max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-3">
                    {matches.length === 0 ? (
                      <p className="text-gray-500 text-sm">No matches available</p>
                    ) : (
                      matches.map((match) => (
                        <label key={match.user_id} className="flex items-center space-x-2 py-1">
                          <input
                            type="checkbox"
                            checked={newSignal.recipient_ids.includes(match.user_id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewSignal({
                                  ...newSignal,
                                  recipient_ids: [...newSignal.recipient_ids, match.user_id]
                                });
                              } else {
                                setNewSignal({
                                  ...newSignal,
                                  recipient_ids: newSignal.recipient_ids.filter(id => id !== match.user_id)
                                });
                              }
                            }}
                            className="rounded"
                          />
                          <span className="text-sm">{match.display_name}</span>
                        </label>
                      ))
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-black mb-2">Price Target</label>
                    <input
                      type="number"
                      step="0.01"
                      placeholder="Optional"
                      value={newSignal.price_target}
                      onChange={(e) => setNewSignal({...newSignal, price_target: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-black mb-2">Stop Loss</label>
                    <input
                      type="number"
                      step="0.01"
                      placeholder="Optional"
                      value={newSignal.stop_loss}
                      onChange={(e) => setNewSignal({...newSignal, stop_loss: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-black mb-2">Risk Level</label>
                    <select
                      value={newSignal.risk_level}
                      onChange={(e) => setNewSignal({...newSignal, risk_level: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-black mb-2">Message</label>
                  <textarea
                    placeholder="Share your analysis, reasoning, or any additional context..."
                    rows="4"
                    value={newSignal.message}
                    onChange={(e) => setNewSignal({...newSignal, message: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                  />
                </div>

                <div className="flex space-x-4 mt-6">
                  <button
                    onClick={() => setShowCreateSignal(false)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-lg font-semibold transition-all"
                  >
                    Cancel
                  </button>
                  <AnimatedButton
                    onClick={handleCreateSignal}
                    disabled={!newSignal.token_symbol || !newSignal.message || newSignal.recipient_ids.length === 0}
                    className="flex-1 bg-black hover:bg-gray-800 disabled:opacity-50 text-white py-3 rounded-lg font-semibold transition-all"
                  >
                    Send Signal
                  </AnimatedButton>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TradingSignals;