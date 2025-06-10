import React, { useState } from 'react';

const LandingPage = () => {
  const [email, setEmail] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleGetStarted = () => {
    // Redirect to the main app
    window.location.href = '/app';
  };

  const handleEmailSignup = (e) => {
    e.preventDefault();
    // For now, just redirect to app
    window.location.href = '/app';
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-black">Solm8</h1>
              <span className="ml-2 text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">Beta</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-black transition-all">Features</a>
              <a href="#how-it-works" className="text-gray-600 hover:text-black transition-all">How it Works</a>
              <a href="#community" className="text-gray-600 hover:text-black transition-all">Community</a>
              <button 
                onClick={handleGetStarted}
                className="bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-all font-medium"
              >
                Get Started
              </button>
            </div>
            
            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-600 hover:text-black transition-all"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-white border-t border-gray-100 py-4">
              <div className="space-y-4">
                <a href="#features" className="block text-gray-600 hover:text-black transition-all px-4">Features</a>
                <a href="#how-it-works" className="block text-gray-600 hover:text-black transition-all px-4">How it Works</a>
                <a href="#community" className="block text-gray-600 hover:text-black transition-all px-4">Community</a>
                <button 
                  onClick={handleGetStarted}
                  className="mx-4 w-[calc(100%-2rem)] bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-all font-medium"
                >
                  Get Started
                </button>
              </div>
            </div>
          )}
            
            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-600 hover:text-black transition-all"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-white border-t border-gray-100 py-4">
              <div className="space-y-4">
                <a href="#features" className="block text-gray-600 hover:text-black transition-all px-4">Features</a>
                <a href="#how-it-works" className="block text-gray-600 hover:text-black transition-all px-4">How it Works</a>
                <a href="#community" className="block text-gray-600 hover:text-black transition-all px-4">Community</a>
                <button 
                  onClick={handleGetStarted}
                  className="mx-4 w-[calc(100%-2rem)] bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-all font-medium"
                >
                  Get Started
                </button>
              </div>
            </div>
          )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-32 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center animate-fade-in-up">
            <h1 className="text-5xl md:text-7xl font-bold text-black mb-8 leading-tight">
              Find Your Perfect
              <span className="block bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent animate-gradient">
                Trading Partner
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Connect with like-minded crypto traders. Share strategies, learn together, and grow your portfolio with AI-powered matching.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <button 
                onClick={handleGetStarted}
                className="bg-black text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-gray-800 transition-all shadow-lg"
              >
                Start Trading Together
              </button>
              <button className="text-gray-600 px-8 py-4 rounded-xl text-lg font-medium hover:text-black transition-all">
                Watch Demo →
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-2xl font-bold text-black">1000+</div>
                <div className="text-sm text-gray-500">Active Traders</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-black">95%</div>
                <div className="text-sm text-gray-500">Match Success</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-black">24/7</div>
                <div className="text-sm text-gray-500">Global Network</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-black">AI</div>
                <div className="text-sm text-gray-500">Powered</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-black mb-6">Why Traders Choose Solm8</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Built for crypto traders, by crypto traders. Every feature designed to help you succeed.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {/* AI Matching */}
            <div className="text-center group">
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all">
                <span className="text-3xl">🤖</span>
              </div>
              <h3 className="text-xl font-semibold text-black mb-4">AI-Powered Matching</h3>
              <p className="text-gray-600 leading-relaxed">
                Our advanced algorithm analyzes trading style, experience, and preferences to find your perfect trading partner.
              </p>
            </div>

            {/* Shareable Profiles */}
            <div className="text-center group">
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all">
                <span className="text-3xl">📱</span>
              </div>
              <h3 className="text-xl font-semibold text-black mb-4">Shareable Profiles</h3>
              <p className="text-gray-600 leading-relaxed">
                Showcase your trading achievements with PnL screenshots, build your reputation, and attract the right connections.
              </p>
            </div>

            {/* Secure Chat */}
            <div className="text-center group">
              <div className="bg-gradient-to-br from-orange-50 to-red-50 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all">
                <span className="text-3xl">💬</span>
              </div>
              <h3 className="text-xl font-semibold text-black mb-4">Secure Conversations</h3>
              <p className="text-gray-600 leading-relaxed">
                Connect instantly with matched traders. Share strategies, discuss markets, and learn from each other safely.
              </p>
            </div>
          </div>

          {/* Additional Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-20">
            <div className="bg-gray-50 p-8 rounded-2xl">
              <h4 className="text-lg font-semibold text-black mb-4">🎯 Smart Recommendations</h4>
              <p className="text-gray-600">Get personalized match suggestions based on your trading goals, experience level, and preferred tokens.</p>
            </div>
            <div className="bg-gray-50 p-8 rounded-2xl">
              <h4 className="text-lg font-semibold text-black mb-4">📊 Portfolio Insights</h4>
              <p className="text-gray-600">Share and compare trading strategies, analyze performance, and learn from successful traders.</p>
            </div>
            <div className="bg-gray-50 p-8 rounded-2xl">
              <h4 className="text-lg font-semibold text-black mb-4">🌐 Global Community</h4>
              <p className="text-gray-600">Connect with traders worldwide across different time zones and trading styles.</p>
            </div>
            <div className="bg-gray-50 p-8 rounded-2xl">
              <h4 className="text-lg font-semibold text-black mb-4">🔒 Privacy First</h4>
              <p className="text-gray-600">Your data is secure. Share only what you want, control your visibility, and trade with confidence.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-black mb-6">How Solm8 Works</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Get started in minutes and find your trading community today.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="bg-black text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6 text-lg font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-black mb-4">Create Your Profile</h3>
              <p className="text-gray-600">
                Connect with Twitter, add your trading experience, preferred tokens, and showcase your best trades.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-black text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6 text-lg font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-black mb-4">Get AI Matches</h3>
              <p className="text-gray-600">
                Our AI analyzes your profile and suggests traders with complementary skills and compatible goals.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-black text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6 text-lg font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-black mb-4">Start Trading Together</h3>
              <p className="text-gray-600">
                Connect, chat, share strategies, and grow your portfolio together with like-minded traders.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Community Section */}
      <section id="community" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-3xl p-12 text-center text-white">
            <h2 className="text-4xl font-bold mb-6">Join the Solm8 Community</h2>
            <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
              Connect with thousands of traders, share your success stories, and build your trading network.
            </p>
            
            <form onSubmit={handleEmailSignup} className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-4">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="flex-1 px-6 py-4 rounded-xl text-black placeholder-gray-500 border-none focus:ring-2 focus:ring-white/50"
                  required
                />
                <button
                  type="submit"
                  className="bg-white text-purple-600 px-8 py-4 rounded-xl font-semibold hover:bg-gray-100 transition-all"
                >
                  Get Early Access
                </button>
              </div>
            </form>
            
            <p className="text-sm opacity-75 mt-4">Join 1000+ traders already using Solm8</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <h3 className="text-2xl font-bold mb-4">Solm8</h3>
              <p className="text-gray-400 max-w-md">
                The premier platform for crypto traders to connect, learn, and grow together. Find your trading partner today.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-all">Features</a></li>
                <li><a href="#" className="hover:text-white transition-all">How it Works</a></li>
                <li><a href="#" className="hover:text-white transition-all">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-all">Security</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Community</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-all">Discord</a></li>
                <li><a href="#" className="hover:text-white transition-all">Twitter</a></li>
                <li><a href="#" className="hover:text-white transition-all">Telegram</a></li>
                <li><a href="#" className="hover:text-white transition-all">Blog</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between">
            <p className="text-gray-400 text-sm">© 2024 Solm8. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-white transition-all text-sm">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-white transition-all text-sm">Terms of Service</a>
              <a href="#" className="text-gray-400 hover:text-white transition-all text-sm">Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;