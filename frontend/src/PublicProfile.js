import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PublicProfile = () => {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPublicProfile();
  }, [username]);

  const fetchPublicProfile = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/public-profile/${username}`);
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else {
        setError('Profile not found');
      }
    } catch (err) {
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const copyProfileLink = () => {
    navigator.clipboard.writeText(window.location.href);
    alert('Profile link copied to clipboard!');
  };

  const shareOnTwitter = () => {
    const text = `Check out ${profile.display_name}'s trading profile on Solm8!`;
    const url = window.location.href;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Profile Not Found</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <a href="/" className="bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800 transition-all">
            Go to Solm8
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <a href="/" className="text-2xl font-bold text-black">Solm8</a>
          <div className="flex space-x-2">
            <button
              onClick={copyProfileLink}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-all"
            >
              📋 Copy Link
            </button>
            <button
              onClick={shareOnTwitter}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-all"
            >
              🐦 Share
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Profile Header */}
        <div className="bg-white rounded-2xl p-8 mb-8 shadow-lg border border-gray-200">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            <img
              src={profile.avatar_url}
              alt={profile.display_name}
              className="w-32 h-32 rounded-full border-4 border-gray-300"
            />
            
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl font-bold text-black mb-2">{profile.display_name}</h1>
              <p className="text-xl text-gray-600 mb-4">@{profile.username}</p>
              
              {profile.bio && (
                <p className="text-gray-700 mb-4">{profile.bio}</p>
              )}
              
              <div className="flex flex-wrap justify-center md:justify-start gap-2 mb-4">
                <span className="bg-black text-white px-3 py-1 rounded-full text-sm font-medium">
                  {profile.trading_experience}
                </span>
                <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                  {profile.years_trading} years trading
                </span>
                <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                  {profile.trading_style}
                </span>
              </div>
              
              {profile.location && (
                <p className="text-gray-600 mb-2">📍 {profile.location}</p>
              )}
              
              {/* Social Links */}
              <div className="flex justify-center md:justify-start space-x-4">
                {profile.show_twitter && profile.twitter_username && (
                  <a
                    href={`https://twitter.com/${profile.twitter_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600 transition-all"
                  >
                    🐦 @{profile.twitter_username}
                  </a>
                )}
                
                {profile.social_links?.discord && (
                  <a
                    href={profile.social_links.discord}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-500 hover:text-indigo-600 transition-all"
                  >
                    💬 Discord
                  </a>
                )}
                
                {profile.social_links?.telegram && (
                  <a
                    href={profile.social_links.telegram}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700 transition-all"
                  >
                    📱 Telegram
                  </a>
                )}
                
                {profile.social_links?.website && (
                  <a
                    href={profile.social_links.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-green-600 hover:text-green-700 transition-all"
                  >
                    🌐 Website
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Trading Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-black mb-4">Trading Profile</h3>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-500">Portfolio Size:</span>
                <p className="font-medium text-gray-800">{profile.portfolio_size}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Risk Tolerance:</span>
                <p className="font-medium text-gray-800">{profile.risk_tolerance}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Trading Hours:</span>
                <p className="font-medium text-gray-800">{profile.trading_hours}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-black mb-4">Preferred Platforms</h3>
            <div className="space-y-3">
              {profile.preferred_trading_platform && (
                <div>
                  <span className="text-sm text-gray-500">Trading:</span>
                  <p className="font-medium text-gray-800">⚡ {profile.preferred_trading_platform}</p>
                </div>
              )}
              <div>
                <span className="text-sm text-gray-500">Joined:</span>
                <p className="font-medium text-gray-800">{new Date(profile.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-black mb-4">Interests</h3>
            <div className="flex flex-wrap gap-2">
              {profile.preferred_tokens.map(token => (
                <span key={token} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                  {token}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Trading Highlights */}
        {profile.trading_highlights && profile.trading_highlights.length > 0 && (
          <div className="bg-white rounded-2xl p-8 mb-8 shadow-lg border border-gray-200">
            <h3 className="text-2xl font-bold text-black mb-6">Trading Highlights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {profile.trading_highlights.map(highlight => (
                <div key={highlight.highlight_id} className="border border-gray-200 rounded-xl p-4">
                  {highlight.image_data && (
                    <img
                      src={`data:image/jpeg;base64,${highlight.image_data}`}
                      alt={highlight.title}
                      className="w-full h-48 object-cover rounded-lg mb-4"
                    />
                  )}
                  <h4 className="font-semibold text-lg text-black mb-2">{highlight.title}</h4>
                  {highlight.description && (
                    <p className="text-gray-700 mb-3">{highlight.description}</p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {highlight.profit_loss && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                        💰 {highlight.profit_loss}
                      </span>
                    )}
                    {highlight.percentage_gain && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                        📈 {highlight.percentage_gain}
                      </span>
                    )}
                    {highlight.date_achieved && (
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                        📅 {highlight.date_achieved}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trading Stories */}
        {(profile.best_trade || profile.favorite_project) && (
          <div className="bg-white rounded-2xl p-8 mb-8 shadow-lg border border-gray-200">
            <h3 className="text-2xl font-bold text-black mb-6">Trading Stories</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {profile.best_trade && (
                <div className="bg-green-50 p-4 rounded-xl">
                  <h4 className="font-semibold text-green-800 mb-2">🏆 Best Trade</h4>
                  <p className="text-green-700">{profile.best_trade}</p>
                </div>
              )}
              
              {profile.favorite_project && (
                <div className="bg-blue-50 p-4 rounded-xl">
                  <h4 className="font-semibold text-blue-800 mb-2">❤️ Favorite Project</h4>
                  <p className="text-blue-700">{profile.favorite_project}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Looking For */}
        {profile.looking_for && profile.looking_for.length > 0 && (
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <h3 className="text-2xl font-bold text-black mb-6">Looking For</h3>
            <div className="flex flex-wrap gap-2">
              {profile.looking_for.map(item => (
                <span key={item} className="bg-black text-white px-4 py-2 rounded-full font-medium">
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* CTA to Join */}
        <div className="text-center mt-12">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">Ready to Connect with Crypto Traders?</h3>
            <p className="text-lg mb-6">Join SolMatch to find your perfect trading partner!</p>
            <a
              href="/"
              className="bg-white text-purple-600 px-8 py-3 rounded-xl font-bold hover:bg-gray-100 transition-all inline-block"
            >
              Join SolMatch
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicProfile;