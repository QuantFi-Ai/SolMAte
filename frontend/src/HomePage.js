import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const HomePage = ({ onGetStarted, onLogin }) => {
  const [activeFeature, setActiveFeature] = useState(0);

  const features = [
    {
      icon: '🤝',
      title: 'Deep Connections',
      description: 'Move beyond surface-level follows. Build meaningful relationships with traders who truly understand your journey and challenges.',
      image: '/api/placeholder/500/300'
    },
    {
      icon: '🎯',
      title: 'Smart Matching',
      description: 'Our AI connects you with traders who complement your style, experience level, and goals - not just random people.',
      image: '/api/placeholder/500/300'
    },
    {
      icon: '💡',
      title: 'Shared Alpha',
      description: 'Exchange insights, strategies, and opportunities with verified traders who have skin in the game.',
      image: '/api/placeholder/500/300'
    },
    {
      icon: '🌟',
      title: 'Trusted Network',
      description: 'Build your inner circle of trading partners. Verify credentials, share wins and losses, grow together.',
      image: '/api/placeholder/500/300'
    }
  ];

  const plans = [
    {
      id: 'free',
      name: 'Explorer',
      price: 'Free',
      billing: 'Forever',
      description: 'Start building your trading network',
      popular: false,
      features: [
        '20 meaningful connections daily',
        'Basic trader discovery',
        'Secure messaging',
        'Profile verification',
        'Community access'
      ]
    },
    {
      id: 'basic_premium',
      name: 'Connector',
      price: '$9.99',
      billing: 'per month',
      description: 'Unlock deeper relationships',
      popular: true,
      features: [
        'Unlimited connections',
        'See who wants to connect',
        'Advanced compatibility filters',
        'Priority matching',
        'Read receipts & status',
        'Exclusive events access'
      ]
    },
    {
      id: 'pro_trader',
      name: 'Inner Circle',
      price: '$19.99',
      billing: 'per month',
      description: 'Build your elite trading network',
      popular: false,
      elite: true,
      features: [
        'All Connector features',
        'Verified trader status',
        'Private alpha groups',
        'Portfolio integration',
        'Signal sharing network',
        'Exclusive mastermind access',
        'Direct mentor matching'
      ]
    }
  ];

  const testimonials = [
    {
      name: 'Marcus Chen',
      role: 'DeFi Specialist',
      avatar: '/api/placeholder/60/60',
      content: 'Finally found my trading family. We share everything - wins, losses, strategies. Trading alone was killing my mental health.',
      rating: 5
    },
    {
      name: 'Elena Rodriguez',
      role: 'Institutional Trader',
      avatar: '/api/placeholder/60/60',
      content: 'The quality of connections here is unmatched. These aren\'t just followers - they\'re genuine trading partners who push me to be better.',
      rating: 5
    },
    {
      name: 'David Kim',
      role: 'Options Trader',
      avatar: '/api/placeholder/60/60',
      content: 'Went from trading in isolation to having a network of 12 close trading partners. We\'ve collectively grown our portfolios 400% this year.',
      rating: 5
    }
  ];

  const stats = [
    { number: '15K+', label: 'Deep Connections Made' },
    { number: '89%', label: 'Find Their Trading Partner' },
    { number: '$4.2B+', label: 'Collective Portfolio Growth' },
    { number: '94%', label: 'Report Reduced Trading Stress' }
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-black/80 backdrop-blur-xl border-b border-gray-800 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img src="/logo.svg" alt="SolM8 Logo" className="h-8 w-auto filter brightness-0 invert" />
              <span className="bg-white text-black px-2 py-1 rounded text-xs font-bold">BETA</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={onLogin}
                className="text-gray-300 hover:text-white font-medium transition-all"
              >
                Sign In
              </button>
              <AnimatedButton
                onClick={onGetStarted}
                variant="secondary"
                className="bg-white hover:bg-gray-200 text-black px-6 py-2 rounded-lg font-bold transition-all"
              >
                Find Your People
              </AnimatedButton>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-900"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="inline-flex items-center bg-gray-800 rounded-full px-6 py-3 mb-8">
              <span className="text-sm text-gray-300">🔥 Trusted by 15,000+ elite traders</span>
            </div>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-6xl lg:text-8xl font-black text-white mb-8 leading-tight"
          >
            Trading Is
            <br />
            <span className="text-gray-400">
              Lonely
            </span>
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl lg:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed"
          >
            Millions are trading. Few are connecting.
            <br />
            <span className="text-white font-semibold">Find your trading family. Build real relationships. Grow together.</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16"
          >
            <AnimatedButton
              onClick={onGetStarted}
              variant="secondary"
              className="bg-white hover:bg-gray-200 text-black px-8 py-4 rounded-xl text-lg font-bold shadow-2xl transform hover:scale-105 transition-all border-2 border-white"
            >
              End Trading Alone →
            </AnimatedButton>
            <button className="text-gray-300 hover:text-white font-medium flex items-center space-x-2 group">
              <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h6" />
              </svg>
              <span>See How It Works</span>
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl lg:text-4xl font-black text-white mb-2">{stat.number}</div>
                <div className="text-gray-400 font-medium">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-6xl font-black text-white mb-6">
              The Trading Paradox
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              More connected than ever, yet more isolated than ever
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="bg-black border border-gray-800 rounded-3xl p-8 text-center">
              <div className="text-4xl mb-4">😔</div>
              <h3 className="text-2xl font-bold text-white mb-4">Trading in Isolation</h3>
              <p className="text-gray-400">
                Making decisions alone. Celebrating wins alone. Processing losses alone. The mental toll is real.
              </p>
            </div>
            
            <div className="bg-black border border-gray-800 rounded-3xl p-8 text-center">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-2xl font-bold text-white mb-4">Shallow Connections</h3>
              <p className="text-gray-400">
                Thousands of followers, zero real relationships. Social media created connection illusion, not actual bonds.
              </p>
            </div>
            
            <div className="bg-black border border-gray-800 rounded-3xl p-8 text-center">
              <div className="text-4xl mb-4">🔄</div>
              <h3 className="text-2xl font-bold text-white mb-4">Missing Growth</h3>
              <p className="text-gray-400">
                No accountability partners. No learning from others' experiences. Stuck in your own bubble.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-6xl font-black text-white mb-6">
              We Fixed This
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Real connections with real traders who actually care about your success
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-6 rounded-2xl border-2 cursor-pointer transition-all ${
                    activeFeature === index
                      ? 'border-white bg-gray-900'
                      : 'border-gray-800 hover:border-gray-600'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className="flex items-start space-x-4">
                    <div className="text-4xl">{feature.icon}</div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                      <p className="text-gray-400">{feature.description}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            
            <div className="relative">
              <motion.div
                key={activeFeature}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl p-8 h-96 flex items-center justify-center border border-gray-700"
              >
                <div className="text-center">
                  <div className="text-6xl mb-4">{features[activeFeature].icon}</div>
                  <h4 className="text-2xl font-bold text-white mb-2">{features[activeFeature].title}</h4>
                  <p className="text-gray-300">{features[activeFeature].description}</p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-6xl font-black text-white mb-6">
              Choose Your Network
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Start with connections, scale to relationships, build your trading empire
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`bg-black border-2 rounded-3xl p-8 relative transform hover:scale-105 transition-all ${
                  plan.popular ? 'border-white shadow-2xl shadow-white/20' : plan.elite ? 'border-gray-400' : 'border-gray-800'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-white text-black px-6 py-2 rounded-full text-sm font-black">
                    MOST POPULAR
                  </div>
                )}
                {plan.elite && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gray-400 text-black px-6 py-2 rounded-full text-sm font-black">
                    ELITE
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-gray-400 mb-4">{plan.description}</p>
                  <div className="text-4xl font-black text-white mb-2">
                    {plan.price}
                    {plan.id !== 'free' && <span className="text-lg text-gray-400">/mo</span>}
                  </div>
                  {plan.id !== 'free' && (
                    <div className="text-gray-400">{plan.billing}</div>
                  )}
                </div>

                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center space-x-3">
                      <svg className="w-5 h-5 text-white flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-300">{feature}</span>
                    </div>
                  ))}
                </div>

                <AnimatedButton
                  onClick={onGetStarted}
                  variant={plan.popular || plan.elite ? "secondary" : "primary"}
                  className={`w-full py-4 rounded-xl font-bold transition-all ${
                    plan.popular || plan.elite
                      ? 'bg-white hover:bg-gray-200 text-black'
                      : 'bg-gray-800 hover:bg-gray-700 text-white'
                  }`}
                >
                  {plan.id === 'free' ? 'Start Connecting' : `Join ${plan.name}`}
                </AnimatedButton>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-400 mb-4">✅ 7-day free trial • Cancel anytime • No commitment</p>
            <button className="text-white hover:underline font-medium">
              Compare all features →
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-6xl font-black text-white mb-6">
              Real Stories, Real Bonds
            </h2>
            <p className="text-xl text-gray-300">
              From strangers to trading family
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-900 border border-gray-800 rounded-2xl p-8"
              >
                <div className="flex items-center space-x-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-300 mb-6 text-lg leading-relaxed">"{testimonial.content}"</p>
                <div className="flex items-center space-x-3">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover border-2 border-gray-700"
                  />
                  <div>
                    <div className="font-bold text-white">{testimonial.name}</div>
                    <div className="text-gray-400 text-sm">{testimonial.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white text-black">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-4xl lg:text-6xl font-black mb-6">
              Your Trading Family
              <br />
              Is Waiting
            </h2>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Stop trading alone. Start building relationships that last.
              <br />
              <span className="font-bold text-black">Join 15,000+ traders who found their people.</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <AnimatedButton
                onClick={onGetStarted}
                variant="primary"
                className="bg-black hover:bg-gray-800 text-white px-8 py-4 rounded-xl text-lg font-bold transform hover:scale-105 transition-all shadow-2xl"
              >
                Find Your People Now
              </AnimatedButton>
              <button className="border-2 border-black hover:bg-black hover:text-white text-black px-8 py-4 rounded-xl text-lg font-bold transition-all">
                Watch Success Stories
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <img src="/logo.svg" alt="SolM8 Logo" className="h-6 w-auto" />
              </div>
              <p className="text-gray-400">
                Where trading relationships are born. End the isolation. Start the connection.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Connect</h4>
              <div className="space-y-2 text-gray-400">
                <div className="hover:text-white cursor-pointer transition-colors">Find Traders</div>
                <div className="hover:text-white cursor-pointer transition-colors">Build Network</div>
                <div className="hover:text-white cursor-pointer transition-colors">Join Groups</div>
                <div className="hover:text-white cursor-pointer transition-colors">Success Stories</div>
              </div>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Support</h4>
              <div className="space-y-2 text-gray-400">
                <div className="hover:text-white cursor-pointer transition-colors">Help Center</div>
                <div className="hover:text-white cursor-pointer transition-colors">Community</div>
                <div className="hover:text-white cursor-pointer transition-colors">Contact Us</div>
                <div className="hover:text-white cursor-pointer transition-colors">Feedback</div>
              </div>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Legal</h4>
              <div className="space-y-2 text-gray-400">
                <div className="hover:text-white cursor-pointer transition-colors">Privacy Policy</div>
                <div className="hover:text-white cursor-pointer transition-colors">Terms of Service</div>
                <div className="hover:text-white cursor-pointer transition-colors">Security</div>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            © 2024 SolM8. All rights reserved. • Building real connections in crypto trading.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;