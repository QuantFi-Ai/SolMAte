import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedButton } from './AnimatedComponents';

const HomePage = ({ onGetStarted, onLogin }) => {
  const [activeFeature, setActiveFeature] = useState(0);

  const features = [
    {
      icon: '🎯',
      title: 'AI-Powered Matching',
      description: 'Advanced algorithms match you with traders based on experience, trading style, and portfolio size.',
      image: '/api/placeholder/500/300'
    },
    {
      icon: '📡',
      title: 'Trading Signals',
      description: 'Share encrypted trade alerts and alpha with your network. Get real-time insights from expert traders.',
      image: '/api/placeholder/500/300'
    },
    {
      icon: '👥',
      title: 'Trading Groups',
      description: 'Create exclusive groups with your best trading connections. Collaborate and share strategies.',
      image: '/api/placeholder/500/300'
    },
    {
      icon: '💼',
      title: 'Portfolio Verification',
      description: 'Connect your wallet or exchange for verified portfolio credentials. Build trust with real data.',
      image: '/api/placeholder/500/300'
    }
  ];

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      billing: 'Forever',
      description: 'Perfect for getting started',
      popular: false,
      features: [
        '20 swipes per day',
        'Basic discovery',
        'Standard matching',
        'Basic messaging',
        'Profile creation',
        'Community access'
      ]
    },
    {
      id: 'basic_premium',
      name: 'Premium',
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
        'Read receipts',
        'Premium support'
      ]
    },
    {
      id: 'pro_trader',
      name: 'Pro Trader',
      price: '$19.99',
      billing: 'per month',
      description: 'Advanced features for serious traders',
      popular: false,
      elite: true,
      features: [
        'All Premium features',
        'Portfolio integration',
        'Trading signal sharing',
        'Create trading groups',
        'Trading calendar',
        'Performance analytics',
        'Priority support',
        'Exclusive alpha groups'
      ]
    }
  ];

  const testimonials = [
    {
      name: 'Alex Chen',
      role: 'DeFi Trader',
      avatar: '/api/placeholder/60/60',
      content: 'Found my trading partner through SolM8. We\'ve 3x our portfolio together in 6 months.',
      rating: 5
    },
    {
      name: 'Sarah Kim',
      role: 'Portfolio Manager',
      avatar: '/api/placeholder/60/60',
      content: 'The trading signals feature is incredible. Getting alpha from verified traders changed my game.',
      rating: 5
    },
    {
      name: 'Marcus Johnson',
      role: 'Crypto Investor',
      avatar: '/api/placeholder/60/60',
      content: 'Best crypto trading community. Finally found traders who match my style and experience level.',
      rating: 5
    }
  ];

  const stats = [
    { number: '10K+', label: 'Active Traders' },
    { number: '500K+', label: 'Successful Matches' },
    { number: '$2.5B+', label: 'Combined Portfolio Value' },
    { number: '95%', label: 'Success Rate' }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/90 backdrop-blur-lg border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-bold text-black">SolM8</div>
              <span className="bg-black text-white px-2 py-1 rounded text-xs font-medium">BETA</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={onLogin}
                className="text-gray-600 hover:text-black font-medium transition-all"
              >
                Sign In
              </button>
              <AnimatedButton
                onClick={onGetStarted}
                className="bg-black hover:bg-gray-800 text-white px-6 py-2 rounded-lg font-medium"
              >
                Get Started
              </AnimatedButton>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-5xl lg:text-7xl font-bold text-black mb-8"
            >
              Find Your
              <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                {' '}Trading Partner
              </span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-xl lg:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed"
            >
              Connect with elite Solana traders. Share strategies, signals, and build your trading network.
              The premier platform for serious crypto traders.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <AnimatedButton
                onClick={onGetStarted}
                className="bg-black hover:bg-gray-800 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg"
              >
                Start Trading Together →
              </AnimatedButton>
              <button className="text-gray-600 hover:text-black font-medium flex items-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h6" />
                </svg>
                <span>Watch Demo</span>
              </button>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="grid grid-cols-2 lg:grid-cols-4 gap-8 mt-20"
            >
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl lg:text-4xl font-bold text-black mb-2">{stat.number}</div>
                  <div className="text-gray-600 font-medium">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-black mb-6">
              Everything You Need to Succeed
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Advanced features designed specifically for serious Solana traders
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-6 rounded-2xl border-2 cursor-pointer transition-all ${
                    activeFeature === index
                      ? 'border-black bg-gray-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className="flex items-start space-x-4">
                    <div className="text-4xl">{feature.icon}</div>
                    <div>
                      <h3 className="text-xl font-bold text-black mb-2">{feature.title}</h3>
                      <p className="text-gray-600">{feature.description}</p>
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
                className="bg-gradient-to-br from-gray-100 to-gray-200 rounded-3xl p-8 h-96 flex items-center justify-center"
              >
                <div className="text-center">
                  <div className="text-6xl mb-4">{features[activeFeature].icon}</div>
                  <h4 className="text-2xl font-bold text-black mb-2">{features[activeFeature].title}</h4>
                  <p className="text-gray-600">{features[activeFeature].description}</p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-black mb-6">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Start free, upgrade when you're ready to unlock advanced trading features
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`bg-white rounded-3xl p-8 border-2 relative ${
                  plan.popular ? 'border-blue-500 shadow-lg' : plan.elite ? 'border-yellow-500 shadow-lg' : 'border-gray-200'
                }`}
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
                  <h3 className="text-2xl font-bold text-black mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  <div className="text-4xl font-bold text-black mb-2">
                    {plan.price}
                    {plan.id !== 'free' && <span className="text-lg text-gray-600">/mo</span>}
                  </div>
                  {plan.id !== 'free' && (
                    <div className="text-gray-600">{plan.billing}</div>
                  )}
                </div>

                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center space-x-3">
                      <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                <AnimatedButton
                  onClick={onGetStarted}
                  className={`w-full py-4 rounded-xl font-semibold transition-all ${
                    plan.popular || plan.elite
                      ? 'bg-black hover:bg-gray-800 text-white'
                      : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                  }`}
                >
                  {plan.id === 'free' ? 'Start Free' : `Get ${plan.name}`}
                </AnimatedButton>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">✅ 7-day free trial • Cancel anytime • No setup fees</p>
            <button className="text-black hover:underline font-medium">
              Compare all features →
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-black mb-6">
              Loved by Traders Worldwide
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands of successful traders who found their perfect trading partners
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-50 rounded-2xl p-8"
              >
                <div className="flex items-center space-x-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-700 mb-6 text-lg leading-relaxed">"{testimonial.content}"</p>
                <div className="flex items-center space-x-3">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <div className="font-semibold text-black">{testimonial.name}</div>
                    <div className="text-gray-600 text-sm">{testimonial.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-black text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-4xl lg:text-5xl font-bold mb-6">
              Ready to Find Your Trading Partner?
            </h2>
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              Join the premier community of Solana traders. Start building your network today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <AnimatedButton
                onClick={onGetStarted}
                className="bg-white hover:bg-gray-200 text-black px-8 py-4 rounded-xl text-lg font-semibold"
              >
                Start Free Trial
              </AnimatedButton>
              <button className="border border-white hover:bg-white hover:text-black text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all">
                Schedule Demo
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="text-2xl font-bold text-black mb-4">SolM8</div>
              <p className="text-gray-600">
                The premier platform for Solana traders to connect, collaborate, and grow together.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-black mb-4">Product</h4>
              <div className="space-y-2 text-gray-600">
                <div>Features</div>
                <div>Pricing</div>
                <div>API</div>
                <div>Security</div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-black mb-4">Company</h4>
              <div className="space-y-2 text-gray-600">
                <div>About</div>
                <div>Blog</div>
                <div>Careers</div>
                <div>Contact</div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-black mb-4">Legal</h4>
              <div className="space-y-2 text-gray-600">
                <div>Privacy</div>
                <div>Terms</div>
                <div>Security</div>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-200 mt-8 pt-8 text-center text-gray-600">
            © 2024 SolM8. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;