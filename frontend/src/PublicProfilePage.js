import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const PublicProfilePage = ({ username }) => {
  const [user, setUser] = useState(null);
  const [tradingHighlights, setTradingHighlights] = useState([]);
  const [socialLinks, setSocialLinks] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (username) {
      fetchPublicProfile();
    }
  }, [username]);

  const fetchPublicProfile = async () => {
    try {
      setLoading(true);
      
      // Fetch user profile
      const profileResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public-profile/${username}`);
      if (!profileResponse.ok) {
        throw new Error('Profile not found');
      }
      const userData = await profileResponse.json();
      setUser(userData);

      // Fetch trading highlights
      try {
        const highlightsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/trading-highlights/${userData.user_id}`);
        if (highlightsResponse.ok) {
          const highlightsData = await highlightsResponse.json();
          setTradingHighlights(highlightsData || []);
        }
      } catch (highlightsError) {
        console.log('No trading highlights found');
      }

      // Fetch social links
      try {
        const socialResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-links/${userData.user_id}`);
        if (socialResponse.ok) {
          const socialData = await socialResponse.json();
          setSocialLinks(socialData || {});
        }
      } catch (socialError) {
        console.log('No social links found');
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const joinSolm8 = () => {
    window.open('https://Solm8.com', '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-black mb-4">Profile Not Found</h1>
          <p className="text-gray-600 mb-8">The trader profile you're looking for doesn't exist.</p>
          <button
            onClick={joinSolm8}
            className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-xl font-medium"
          >
            Join SolM8 →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with SolM8 Branding */}
      <header className="bg-black text-white py-4 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl font-bold">SolM8</div>
            <span className="text-gray-300">|</span>
            <span className="text-gray-300">Trader Profile</span>
          </div>
          <button
            onClick={joinSolm8}
            className="bg-white text-black hover:bg-gray-100 px-6 py-2 rounded-lg font-medium transition-all"
          >
            Join SolM8
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6">
        {/* Profile Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-black text-white rounded-3xl p-8 mb-8"
        >
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            <div className="relative">
              <img
                src={user.avatar_url || '/api/placeholder/120/120'}
                alt={user.display_name}
                className="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover"
              />
              <div className="absolute -bottom-2 -right-2 bg-white w-10 h-10 rounded-full border-2 border-black flex items-center justify-center">
                <svg className="w-5 h-5 text-black" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            
            <div className="text-center md:text-left flex-1">
              <h1 className="text-4xl font-bold mb-2">{user.display_name}</h1>
              <p className="text-gray-300 text-xl mb-4">@{user.username}</p>
              
              <div className="flex flex-wrap justify-center md:justify-start gap-3 mb-4">
                <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium">
                  {user.trading_experience} Trader
                </span>
                {user.years_trading && (
                  <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium">
                    {user.years_trading} Years Experience
                  </span>
                )}
                {user.portfolio_size && (
                  <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium">
                    {user.portfolio_size} Portfolio
                  </span>
                )}
              </div>
              
              {user.bio && (
                <div className="bg-white bg-opacity-10 rounded-xl p-4 mb-6">
                  <h3 className="text-sm font-semibold text-white mb-2 opacity-80">About Me</h3>
                  <p className="text-gray-200 text-lg leading-relaxed">{user.bio}</p>
                </div>
              )}
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
                <button
                  onClick={joinSolm8}
                  className="bg-white text-black hover:bg-gray-100 px-8 py-3 rounded-xl font-semibold transition-all"
                >
                  Connect on SolM8 →
                </button>
                {Object.keys(socialLinks).length > 0 && (
                  <div className="flex space-x-3 justify-center">
                    {socialLinks.twitter && (
                      <a
                        href={`https://twitter.com/${socialLinks.twitter.replace('@', '')}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-white bg-opacity-20 hover:bg-opacity-30 p-3 rounded-lg transition-all"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                        </svg>
                      </a>
                    )}
                    {socialLinks.discord && (
                      <div className="bg-white bg-opacity-20 p-3 rounded-lg">
                        <span className="text-xs font-medium">🎮 {socialLinks.discord}</span>
                      </div>
                    )}
                    {socialLinks.telegram && (
                      <a
                        href={`https://t.me/${socialLinks.telegram.replace('@', '')}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-white bg-opacity-20 hover:bg-opacity-30 p-3 rounded-lg transition-all"
                      >
                        <span className="text-sm">✈️</span>
                      </a>
                    )}
                    {socialLinks.website && (
                      <a
                        href={socialLinks.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-white bg-opacity-20 hover:bg-opacity-30 p-3 rounded-lg transition-all"
                      >
                        <span className="text-sm">🌐</span>
                      </a>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Trading Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="bg-white border border-gray-200 p-6 rounded-2xl text-center">
            <div className="text-2xl font-bold text-black mb-1">{user.trading_experience}</div>
            <div className="text-gray-600 text-sm">Experience</div>
          </div>
          <div className="bg-white border border-gray-200 p-6 rounded-2xl text-center">
            <div className="text-2xl font-bold text-black mb-1">{user.years_trading || 0}Y</div>
            <div className="text-gray-600 text-sm">Trading</div>
          </div>
          <div className="bg-white border border-gray-200 p-6 rounded-2xl text-center">
            <div className="text-2xl font-bold text-black mb-1">{user.trading_style}</div>
            <div className="text-gray-600 text-sm">Style</div>
          </div>
          <div className="bg-white border border-gray-200 p-6 rounded-2xl text-center">
            <div className="text-2xl font-bold text-black mb-1">{user.portfolio_size}</div>
            <div className="text-gray-600 text-sm">Portfolio</div>
          </div>
        </motion.div>

        {/* Trading Highlights */}
        {tradingHighlights.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white border border-gray-200 rounded-2xl p-8 mb-8"
          >
            <h3 className="text-2xl font-bold text-black mb-6 flex items-center">
              <span className="text-3xl mr-3">📸</span>
              Trading Highlights
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {tradingHighlights.map((highlight, index) => (
                <div key={index} className="border border-gray-200 rounded-xl p-6">
                  {highlight.image_data && (
                    <img
                      src={`data:image/jpeg;base64,${highlight.image_data}`}
                      alt={highlight.title}
                      className="w-full h-48 object-cover rounded-lg mb-4"
                    />
                  )}
                  <h4 className="font-bold text-black mb-2">{highlight.title}</h4>
                  {highlight.description && (
                    <p className="text-gray-600 text-sm mb-3">{highlight.description}</p>
                  )}
                  <div className="flex justify-between text-sm">
                    {highlight.profit_loss && (
                      <span className="bg-black text-white px-3 py-1 rounded-full font-medium">
                        {highlight.profit_loss}
                      </span>
                    )}
                    {highlight.percentage_gain && (
                      <span className="bg-gray-800 text-white px-3 py-1 rounded-full font-medium">
                        {highlight.percentage_gain}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Trading Preferences */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          {/* Preferred Tokens */}
          {user.preferred_tokens && user.preferred_tokens.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl p-8">
              <h3 className="text-xl font-bold text-black mb-4 flex items-center">
                <span className="text-2xl mr-2">🪙</span>
                Preferred Token Categories
              </h3>
              <div className="flex flex-wrap gap-3">
                {user.preferred_tokens.map((token, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-black text-white rounded-full text-sm font-medium"
                  >
                    {token}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Trading Goals */}
          {user.looking_for && user.looking_for.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl p-8">
              <h3 className="text-xl font-bold text-black mb-4 flex items-center">
                <span className="text-2xl mr-2">🎯</span>
                Trading Goals & Interests
              </h3>
              <div className="flex flex-wrap gap-3">
                {user.looking_for.map((goal, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-gray-800 text-white rounded-full text-sm font-medium"
                  >
                    {goal}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* SolM8 Promotion Footer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-black text-white rounded-2xl p-8 mt-12 text-center"
        >
          <h3 className="text-3xl font-bold mb-4">Connect with Elite Solana Traders</h3>
          <p className="text-gray-300 text-lg mb-6 max-w-2xl mx-auto">
            Join SolM8 to discover, match, and collaborate with traders like {user.display_name}. 
            Share strategies, build networks, and grow your trading success together.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={joinSolm8}
              className="bg-white text-black hover:bg-gray-100 px-8 py-4 rounded-xl font-bold text-lg transition-all"
            >
              Join SolM8 Now →
            </button>
            <button
              onClick={() => window.open('https://Solm8.com/about', '_blank')}
              className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-black px-8 py-4 rounded-xl font-medium transition-all"
            >
              Learn More
            </button>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-700">
            <p className="text-gray-400 text-sm">
              Powered by <span className="font-bold text-white">SolM8.com</span> - The Premier Solana Trading Community
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PublicProfilePage;