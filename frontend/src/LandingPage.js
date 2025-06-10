import React, { useState, useEffect } from 'react';

const LandingPage = () => {
  const [email, setEmail] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Track mouse position for parallax effects
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleGetStarted = () => {
    window.location.href = '/app';
  };

  const handleEmailSignup = (e) => {
    e.preventDefault();
    window.location.href = '/app';
  };

  // Floating particles component
  const FloatingParticles = () => (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 3}s`,
            animationDuration: `${2 + Math.random() * 3}s`,
            opacity: 0.3,
          }}
        />
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)`,
          }}
        />
        
        {/* Animated Gradient Orbs in Grayscale */}
        <div 
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-white/5 to-gray-500/10 rounded-full blur-3xl animate-pulse"
          style={{
            transform: `translate(${mousePosition.x * 0.05}px, ${mousePosition.y * 0.05}px)`,
          }}
        />
        <div 
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-gray-500/10 to-white/5 rounded-full blur-3xl animate-pulse"
          style={{
            transform: `translate(${-mousePosition.x * 0.03}px, ${-mousePosition.y * 0.03}px)`,
            animationDelay: '1s',
          }}
        />
        
        <FloatingParticles />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 backdrop-blur-md bg-black/20 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">
                Solm8
              </h1>
              <div className="ml-3 px-2 py-1 text-xs bg-white/10 text-gray-300 rounded-full border border-white/20">
                BETA
              </div>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition-all duration-300 relative group">
                Features
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"></span>
              </a>
              <a href="#how-it-works" className="text-gray-300 hover:text-white transition-all duration-300 relative group">
                How it Works
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"></span>
              </a>
              <a href="#community" className="text-gray-300 hover:text-white transition-all duration-300 relative group">
                Community
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"></span>
              </a>
              <button 
                onClick={handleGetStarted}
                className="relative px-6 py-2 bg-white text-black rounded-lg font-medium overflow-hidden group transition-all duration-300 hover:shadow-lg hover:shadow-white/25 hover:bg-gray-100"
              >
                <span className="relative z-10">Launch App</span>
              </button>
            </div>
            
            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-300 hover:text-white transition-all"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className="md:hidden backdrop-blur-md bg-black/40 border-t border-white/10 py-4">
              <div className="space-y-4">
                <a href="#features" className="block text-gray-300 hover:text-white transition-all px-4">Features</a>
                <a href="#how-it-works" className="block text-gray-300 hover:text-white transition-all px-4">How it Works</a>
                <a href="#community" className="block text-gray-300 hover:text-white transition-all px-4">Community</a>
                <button 
                  onClick={handleGetStarted}
                  className="mx-4 w-[calc(100%-2rem)] bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-all"
                >
                  Launch App
                </button>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 min-h-screen flex items-center">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center">
            {/* Glitch effect heading */}
            <div className="relative mb-8">
              <h1 className="text-6xl md:text-8xl font-black text-white mb-4 leading-tight tracking-tight">
                FIND YOUR
              </h1>
              <div className="relative inline-block">
                <h1 className="text-6xl md:text-8xl font-black text-white leading-tight tracking-tight">
                  TRADING M8
                </h1>
                {/* Glitch layers in grayscale */}
                <h1 className="absolute inset-0 text-6xl md:text-8xl font-black text-gray-400 opacity-30 animate-pulse leading-tight tracking-tight" style={{ transform: 'translate(2px, 0)' }}>
                  TRADING M8
                </h1>
                <h1 className="absolute inset-0 text-6xl md:text-8xl font-black text-gray-600 opacity-20 animate-pulse leading-tight tracking-tight" style={{ transform: 'translate(-2px, 0)', animationDelay: '0.1s' }}>
                  TRADING M8
                </h1>
              </div>
            </div>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              AI-powered matching system connecting crypto traders worldwide. 
              <span className="text-white font-semibold"> Share strategies</span>, 
              <span className="text-gray-100 font-semibold"> build networks</span>, 
              <span className="text-white font-semibold"> dominate markets</span>.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-16">
              <button 
                onClick={handleGetStarted}
                className="group relative px-8 py-4 bg-white text-black text-lg font-bold rounded-xl overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-white/25"
              >
                <span className="relative z-10 flex items-center">
                  <span>ENTER THE MATRIX</span>
                  <svg className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </button>
              
              <button className="group text-gray-300 px-8 py-4 rounded-xl border border-white/20 hover:border-white hover:text-white transition-all duration-300 hover:bg-white/5 backdrop-blur-sm">
                <span className="flex items-center text-lg font-medium">
                  <span>WATCH DEMO</span>
                  <div className="ml-2 w-0 h-0 border-l-4 border-l-white border-t-2 border-t-transparent border-b-2 border-b-transparent group-hover:translate-x-1 transition-transform"></div>
                </span>
              </button>
            </div>

            {/* Futuristic Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {[
                { value: "1K+", label: "ACTIVE TRADERS", accent: "cyan" },
                { value: "95%", label: "MATCH SUCCESS", accent: "purple" },
                { value: "24/7", label: "GLOBAL NETWORK", accent: "pink" },
                { value: "AI", label: "POWERED", accent: "cyan" }
              ].map((stat, index) => (
                <div key={index} className="group">
                  <div className="relative p-6 rounded-xl backdrop-blur-md bg-black/20 border border-cyan-500/20 hover:border-cyan-500/50 transition-all duration-300 hover:bg-black/40">
                    <div className={`text-3xl font-black text-${stat.accent}-400 mb-2 group-hover:scale-110 transition-transform`}>
                      {stat.value}
                    </div>
                    <div className="text-xs text-gray-400 font-mono tracking-wider">
                      {stat.label}
                    </div>
                    {/* Animated corner accents */}
                    <div className={`absolute top-0 left-0 w-2 h-2 bg-${stat.accent}-400 opacity-0 group-hover:opacity-100 transition-opacity`}></div>
                    <div className={`absolute bottom-0 right-0 w-2 h-2 bg-${stat.accent}-400 opacity-0 group-hover:opacity-100 transition-opacity`}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-black text-white mb-6">
              NEXT-GEN
              <span className="block bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                TRADING TECH
              </span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Cutting-edge features designed for the future of crypto trading collaboration
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: "🤖",
                title: "AI NEURAL MATCHING",
                desc: "Advanced machine learning algorithms analyze trading patterns, risk profiles, and compatibility factors to create perfect partnerships.",
                accent: "cyan",
                delay: "0s"
              },
              {
                icon: "📱",
                title: "HOLOGRAPHIC PROFILES",
                desc: "3D interactive trading profiles with real-time P&L visualization, achievement showcases, and social proof integration.",
                accent: "purple", 
                delay: "0.2s"
              },
              {
                icon: "⚡",
                title: "QUANTUM CHAT",
                desc: "Encrypted, real-time communication with built-in strategy sharing, market analysis tools, and collaborative trading features.",
                accent: "pink",
                delay: "0.4s"
              }
            ].map((feature, index) => (
              <div 
                key={index} 
                className="group relative"
                style={{ animationDelay: feature.delay }}
              >
                <div className="relative p-8 rounded-2xl backdrop-blur-md bg-black/20 border border-cyan-500/20 hover:border-cyan-500/50 transition-all duration-500 hover:bg-black/40 hover:scale-105 overflow-hidden">
                  {/* Animated background gradient */}
                  <div className={`absolute inset-0 bg-gradient-to-br from-${feature.accent}-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
                  
                  <div className="relative z-10">
                    <div className="text-6xl mb-6 group-hover:scale-110 transition-transform duration-300">
                      {feature.icon}
                    </div>
                    <h3 className={`text-xl font-black text-${feature.accent}-400 mb-4 tracking-wider`}>
                      {feature.title}
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      {feature.desc}
                    </p>
                  </div>
                  
                  {/* Corner accents */}
                  <div className={`absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-${feature.accent}-400/20 to-transparent`}></div>
                  <div className={`absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-${feature.accent}-400/20 to-transparent`}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works - Futuristic Process */}
      <section id="how-it-works" className="relative z-10 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-black text-white mb-6">
              ACTIVATION
              <span className="block bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                PROTOCOL
              </span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "NEURAL SCAN", desc: "Connect your trading identity and let our AI analyze your profile" },
              { step: "02", title: "QUANTUM MATCH", desc: "Advanced algorithms find your perfect trading counterparts" },
              { step: "03", title: "SYNC & TRADE", desc: "Enter the matrix and start building your trading empire" }
            ].map((step, index) => (
              <div key={index} className="text-center group">
                <div className="relative mx-auto mb-8">
                  {/* Hexagonal frame */}
                  <div className="relative w-24 h-24 mx-auto">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rotate-45 rounded-lg backdrop-blur-sm border border-cyan-500/30 group-hover:rotate-90 transition-transform duration-500"></div>
                    <div className="absolute inset-2 bg-black/60 rotate-45 rounded-lg flex items-center justify-center group-hover:rotate-90 transition-transform duration-500">
                      <span className="text-2xl font-black text-cyan-400 -rotate-45 group-hover:-rotate-90 transition-transform duration-500">
                        {step.step}
                      </span>
                    </div>
                  </div>
                </div>
                <h3 className="text-xl font-black text-white mb-4 tracking-wider">{step.title}</h3>
                <p className="text-gray-300 leading-relaxed max-w-xs mx-auto">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Community Section - Futuristic CTA */}
      <section id="community" className="relative z-10 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative p-12 rounded-3xl backdrop-blur-md bg-gradient-to-br from-black/40 to-black/20 border border-cyan-500/30 overflow-hidden">
            {/* Animated background elements */}
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 animate-gradient"></div>
            
            <div className="relative z-10 text-center text-white">
              <h2 className="text-5xl font-black mb-6">
                <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  JOIN THE REVOLUTION
                </span>
              </h2>
              <p className="text-xl mb-8 text-gray-300 max-w-3xl mx-auto">
                Enter the future of crypto trading collaboration. Limited beta access available.
              </p>
              
              <form onSubmit={handleEmailSignup} className="max-w-md mx-auto">
                <div className="flex flex-col sm:flex-row gap-4">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your neural link..."
                    className="flex-1 px-6 py-4 rounded-xl bg-black/60 text-white placeholder-gray-400 border border-cyan-500/30 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 backdrop-blur-sm transition-all"
                    required
                  />
                  <button
                    type="submit"
                    className="bg-gradient-to-r from-cyan-500 to-purple-500 text-white px-8 py-4 rounded-xl font-bold hover:scale-105 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25"
                  >
                    ACTIVATE
                  </button>
                </div>
              </form>
              
              <p className="text-sm text-gray-400 mt-6 font-mono">
                &gt; 1000+ TRADERS CONNECTED TO THE MATRIX
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 bg-black/60 backdrop-blur-md border-t border-cyan-500/20 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <h3 className="text-3xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
                Solm8
              </h3>
              <p className="text-gray-400 max-w-md leading-relaxed">
                The neural network for crypto traders. Connect, collaborate, and conquer the markets together.
              </p>
            </div>
            
            <div>
              <h4 className="font-bold text-cyan-400 mb-4 tracking-wider">MATRIX</h4>
              <ul className="space-y-3 text-gray-400 font-mono text-sm">
                <li><a href="#" className="hover:text-cyan-400 transition-all">&gt; FEATURES</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-all">&gt; PROTOCOLS</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-all">&gt; SECURITY</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-all">&gt; NEURAL_NET</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold text-purple-400 mb-4 tracking-wider">NETWORK</h4>
              <ul className="space-y-3 text-gray-400 font-mono text-sm">
                <li><a href="#" className="hover:text-purple-400 transition-all">&gt; DISCORD_NODE</a></li>
                <li><a href="#" className="hover:text-purple-400 transition-all">&gt; TWITTER_FEED</a></li>
                <li><a href="#" className="hover:text-purple-400 transition-all">&gt; TELEGRAM_NET</a></li>
                <li><a href="#" className="hover:text-purple-400 transition-all">&gt; DATA_STREAM</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-cyan-500/20 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between">
            <p className="text-gray-400 text-sm font-mono">© 2024 SOLM8.NETWORK // ALL_RIGHTS_RESERVED</p>
            <div className="flex space-x-6 mt-4 md:mt-0 font-mono text-sm">
              <a href="#" className="text-gray-400 hover:text-cyan-400 transition-all">&gt; PRIVACY_PROTOCOL</a>
              <a href="#" className="text-gray-400 hover:text-cyan-400 transition-all">&gt; TERMS_MATRIX</a>
              <a href="#" className="text-gray-400 hover:text-cyan-400 transition-all">&gt; SUPPORT_NET</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;