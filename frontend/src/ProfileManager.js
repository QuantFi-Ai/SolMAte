import React, { useState, useEffect, useRef } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ProfileManager = ({ currentUser, onClose }) => {
  const [tradingHighlights, setTradingHighlights] = useState([]);
  const [socialLinks, setSocialLinks] = useState({
    twitter: '',
    discord: '',
    telegram: '',
    website: '',
    linkedin: ''
  });
  const [newHighlight, setNewHighlight] = useState({
    title: '',
    description: '',
    image_data: '',
    highlight_type: 'pnl_screenshot',
    date_achieved: '',
    profit_loss: '',
    percentage_gain: ''
  });
  const [showAddHighlight, setShowAddHighlight] = useState(false);
  const [activeTab, setActiveTab] = useState('preview'); // 'preview', 'edit', 'highlights', 'social'
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const HIGHLIGHT_TYPES = [
    'pnl_screenshot',
    'achievement', 
    'trade_analysis',
    'portfolio'
  ];

  useEffect(() => {
    fetchTradingHighlights();
    fetchSocialLinks();
  }, []);

  const fetchTradingHighlights = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/trading-highlights/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setTradingHighlights(data);
      }
    } catch (err) {
      console.error('Failed to fetch highlights:', err);
    }
  };

  const fetchSocialLinks = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/social-links/${currentUser.user_id}`);
      if (response.ok) {
        const data = await response.json();
        setSocialLinks({
          twitter: data.twitter || '',
          discord: data.discord || '',
          telegram: data.telegram || '',
          website: data.website || '',
          linkedin: data.linkedin || ''
        });
      }
    } catch (err) {
      console.error('Failed to fetch social links:', err);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/api/upload-trading-highlight/${currentUser.user_id}`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setNewHighlight(prev => ({ ...prev, image_data: data.image_data }));
      } else {
        alert('Failed to upload image');
      }
    } catch (err) {
      alert('Failed to upload image');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveHighlight = async () => {
    if (!newHighlight.title || !newHighlight.image_data) {
      alert('Please provide a title and upload an image');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/save-trading-highlight/${currentUser.user_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newHighlight)
      });

      if (response.ok) {
        alert('Highlight saved successfully!');
        fetchTradingHighlights();
        setNewHighlight({
          title: '',
          description: '',
          image_data: '',
          highlight_type: 'pnl_screenshot',
          date_achieved: '',
          profit_loss: '',
          percentage_gain: ''
        });
        setShowAddHighlight(false);
      } else {
        alert('Failed to save highlight');
      }
    } catch (err) {
      alert('Failed to save highlight');
    }
  };

  const handleDeleteHighlight = async (highlightId) => {
    if (!window.confirm('Are you sure you want to delete this highlight?')) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/trading-highlights/${highlightId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert('Highlight deleted successfully!');
        fetchTradingHighlights();
      } else {
        alert('Failed to delete highlight');
      }
    } catch (err) {
      alert('Failed to delete highlight');
    }
  };

  const handleSaveSocialLinks = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/update-social-links/${currentUser.user_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(socialLinks)
      });

      if (response.ok) {
        alert('Social links updated successfully!');
      } else {
        alert('Failed to update social links');
      }
    } catch (err) {
      alert('Failed to update social links');
    }
  };

  const getPublicProfileLink = () => {
    return `${window.location.origin}/profile/${currentUser.username}`;
  };

  const copyProfileLink = () => {
    navigator.clipboard.writeText(getPublicProfileLink());
    alert('Profile link copied to clipboard!');
  };

  const shareOnTwitter = () => {
    const text = `Check out my trading profile on Solm8! 🚀`;
    const url = getPublicProfileLink();
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
  };

  // Profile Preview Component (similar to PublicProfile but editable)
  const ProfilePreview = () => {
    if (!currentUser) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-600">Loading profile...</p>
        </div>
      );
    }

    // Add safety check for currentUser
    if (!currentUser) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-600">Loading profile...</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Profile Header */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-8">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            <img
              src={currentUser.avatar_url}
              alt={currentUser.display_name}
              className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
            />
            
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-2xl font-bold text-black mb-2">{currentUser.display_name}</h1>
              <p className="text-lg text-gray-600 mb-4">@{currentUser.username}</p>
              
              {currentUser.bio && (
                <p className="text-gray-700 mb-4">{currentUser.bio}</p>
              )}
              
              <div className="flex flex-wrap justify-center md:justify-start gap-2 mb-4">
                {currentUser.trading_experience && (
                  <span className="bg-black text-white px-3 py-1 rounded-full text-sm font-medium">
                    {currentUser.trading_experience}
                  </span>
                )}
                {currentUser.years_trading > 0 && (
                  <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                    {currentUser.years_trading} years trading
                  </span>
                )}
                {currentUser.trading_style && (
                  <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                    {currentUser.trading_style}
                  </span>
                )}
              </div>
              
              {currentUser.location && (
                <p className="text-gray-600 mb-2">📍 {currentUser.location}</p>
              )}
            </div>
          </div>
        </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <h4 className="font-semibold text-gray-800 mb-2">Trading Profile</h4>
          <div className="space-y-2 text-sm">
            {currentUser.portfolio_size && (
              <p><span className="text-gray-500">Portfolio:</span> {currentUser.portfolio_size}</p>
            )}
            {currentUser.risk_tolerance && (
              <p><span className="text-gray-500">Risk:</span> {currentUser.risk_tolerance}</p>
            )}
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <h4 className="font-semibold text-gray-800 mb-2">Platforms</h4>
          <div className="space-y-2 text-sm">
            {currentUser.preferred_trading_platform && (
              <p><span className="text-gray-500">Trading:</span> {currentUser.preferred_trading_platform}</p>
            )}
            {socialLinks.twitter && (
              <p><span className="text-gray-500">Twitter:</span> Connected</p>
            )}
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <h4 className="font-semibold text-gray-800 mb-2">Activity</h4>
          <div className="space-y-2 text-sm">
            <p><span className="text-gray-500">Highlights:</span> {tradingHighlights.length}</p>
            <p><span className="text-gray-500">Social Links:</span> {Object.values(socialLinks).filter(link => link).length}</p>
          </div>
        </div>
      </div>

      {/* Social Links */}
      {Object.values(socialLinks).some(link => link) && (
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-black mb-4">Connect With Me</h3>
          <div className="flex flex-wrap gap-3">
            {socialLinks.twitter && (
              <a href={socialLinks.twitter} target="_blank" rel="noopener noreferrer" 
                 className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-all">
                🐦 Twitter
              </a>
            )}
            {socialLinks.discord && (
              <a href={socialLinks.discord} target="_blank" rel="noopener noreferrer"
                 className="bg-indigo-500 text-white px-4 py-2 rounded-lg hover:bg-indigo-600 transition-all">
                💬 Discord
              </a>
            )}
            {socialLinks.telegram && (
              <a href={socialLinks.telegram} target="_blank" rel="noopener noreferrer"
                 className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all">
                📱 Telegram
              </a>
            )}
            {socialLinks.website && (
              <a href={socialLinks.website} target="_blank" rel="noopener noreferrer"
                 className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all">
                🌐 Website
              </a>
            )}
          </div>
        </div>
      )}

      {/* Trading Highlights */}
      {tradingHighlights.length > 0 && (
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-black mb-4">Trading Highlights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tradingHighlights.map(highlight => (
              <div key={highlight.highlight_id} className="border border-gray-200 rounded-lg p-4">
                {highlight.image_data && (
                  <img
                    src={`data:image/jpeg;base64,${highlight.image_data}`}
                    alt={highlight.title}
                    className="w-full h-32 object-cover rounded-lg mb-3"
                  />
                )}
                <h4 className="font-semibold text-black mb-2">{highlight.title}</h4>
                {highlight.description && (
                  <p className="text-gray-700 text-sm mb-3">{highlight.description}</p>
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
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty States */}
      {tradingHighlights.length === 0 && !Object.values(socialLinks).some(link => link) && (
        <div className="bg-gray-50 rounded-xl p-8 text-center">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Complete Your Profile</h3>
          <p className="text-gray-600 mb-4">Add trading highlights and social links to make your profile stand out!</p>
          <div className="space-x-4">
            <button
              onClick={() => setActiveTab('highlights')}
              className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-all"
            >
              Add Trading Highlights
            </button>
            <button
              onClick={() => setActiveTab('social')}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-all"
            >
              Add Social Links
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[95vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
          <h2 className="text-2xl font-bold text-black">Manage Your Public Profile</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-black transition-all"
          >
            ✕
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 pt-4 border-b border-gray-200">
          <div className="flex space-x-6">
            <button
              onClick={() => setActiveTab('preview')}
              className={`pb-4 px-2 font-medium transition-all ${
                activeTab === 'preview'
                  ? 'text-black border-b-2 border-black'
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              👁️ Preview Profile
            </button>
            <button
              onClick={() => setActiveTab('highlights')}
              className={`pb-4 px-2 font-medium transition-all ${
                activeTab === 'highlights'
                  ? 'text-black border-b-2 border-black'
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              📊 Trading Highlights ({tradingHighlights.length})
            </button>
            <button
              onClick={() => setActiveTab('social')}
              className={`pb-4 px-2 font-medium transition-all ${
                activeTab === 'social'
                  ? 'text-black border-b-2 border-black'
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              🔗 Social Links
            </button>
            <button
              onClick={() => setActiveTab('share')}
              className={`pb-4 px-2 font-medium transition-all ${
                activeTab === 'share'
                  ? 'text-black border-b-2 border-black'
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              📱 Share Profile
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Profile Preview Tab */}
          {activeTab === 'preview' && <ProfilePreview />}

          {/* Trading Highlights Tab */}
          {activeTab === 'highlights' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-black">Trading Highlights</h3>
                <button
                  onClick={() => setShowAddHighlight(true)}
                  className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-all"
                >
                  + Add Highlight
                </button>
              </div>

              {/* Existing Highlights */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {tradingHighlights.map(highlight => (
                  <div key={highlight.highlight_id} className="border border-gray-200 rounded-xl p-4">
                    {highlight.image_data && (
                      <img
                        src={`data:image/jpeg;base64,${highlight.image_data}`}
                        alt={highlight.title}
                        className="w-full h-32 object-cover rounded-lg mb-3"
                      />
                    )}
                    <h4 className="font-semibold text-black mb-2">{highlight.title}</h4>
                    {highlight.description && (
                      <p className="text-gray-700 text-sm mb-2">{highlight.description}</p>
                    )}
                    <div className="flex justify-between items-center">
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                        {highlight.highlight_type.replace('_', ' ')}
                      </span>
                      <button
                        onClick={() => handleDeleteHighlight(highlight.highlight_id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {tradingHighlights.length === 0 && (
                <div className="text-center py-12 bg-gray-50 rounded-xl">
                  <h4 className="text-lg font-semibold text-gray-800 mb-2">No Trading Highlights Yet</h4>
                  <p className="text-gray-600 mb-4">Showcase your best trades, PnL screenshots, and achievements!</p>
                  <button
                    onClick={() => setShowAddHighlight(true)}
                    className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium transition-all"
                  >
                    Add Your First Highlight
                  </button>
                </div>
              )}

              {/* Add New Highlight Form */}
              {showAddHighlight && (
                <div className="border border-gray-200 rounded-xl p-6 bg-gray-50">
                  <h4 className="text-lg font-semibold text-black mb-4">Add Trading Highlight</h4>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Title *</label>
                      <input
                        type="text"
                        value={newHighlight.title}
                        onChange={(e) => setNewHighlight(prev => ({ ...prev, title: e.target.value }))}
                        placeholder="e.g., 300% Gain on BONK Trade"
                        className="w-full border border-gray-300 rounded-lg px-4 py-2"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                      <textarea
                        value={newHighlight.description}
                        onChange={(e) => setNewHighlight(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Describe your achievement..."
                        rows="3"
                        className="w-full border border-gray-300 rounded-lg px-4 py-2"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                        <select
                          value={newHighlight.highlight_type}
                          onChange={(e) => setNewHighlight(prev => ({ ...prev, highlight_type: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg px-4 py-2"
                        >
                          {HIGHLIGHT_TYPES.map(type => (
                            <option key={type} value={type}>
                              {type.replace('_', ' ').toUpperCase()}
                            </option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                        <input
                          type="date"
                          value={newHighlight.date_achieved}
                          onChange={(e) => setNewHighlight(prev => ({ ...prev, date_achieved: e.target.value }))}
                          className="w-full border border-gray-300 rounded-lg px-4 py-2"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Profit/Loss</label>
                        <input
                          type="text"
                          value={newHighlight.profit_loss}
                          onChange={(e) => setNewHighlight(prev => ({ ...prev, profit_loss: e.target.value }))}
                          placeholder="e.g., +$5,000"
                          className="w-full border border-gray-300 rounded-lg px-4 py-2"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Percentage Gain</label>
                        <input
                          type="text"
                          value={newHighlight.percentage_gain}
                          onChange={(e) => setNewHighlight(prev => ({ ...prev, percentage_gain: e.target.value }))}
                          placeholder="e.g., +300%"
                          className="w-full border border-gray-300 rounded-lg px-4 py-2"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Screenshot/Image *</label>
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-gray-400 transition-all"
                      >
                        {newHighlight.image_data ? (
                          <div>
                            <img
                              src={`data:image/jpeg;base64,${newHighlight.image_data}`}
                              alt="Preview"
                              className="w-full h-48 object-cover rounded-lg mb-2"
                            />
                            <p className="text-sm text-green-600">Image uploaded! Click to change.</p>
                          </div>
                        ) : (
                          <div>
                            {loading ? (
                              <p className="text-gray-500">Uploading...</p>
                            ) : (
                              <>
                                <p className="text-gray-500">Click to upload PnL screenshot or trading image</p>
                                <p className="text-xs text-gray-400 mt-2">JPG, PNG or GIF. Max size 5MB.</p>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleImageUpload}
                        accept="image/*"
                        className="hidden"
                      />
                    </div>
                    
                    <div className="flex space-x-4">
                      <button
                        onClick={handleSaveHighlight}
                        className="bg-black hover:bg-gray-800 text-white px-6 py-2 rounded-lg font-medium transition-all"
                      >
                        Save Highlight
                      </button>
                      <button
                        onClick={() => setShowAddHighlight(false)}
                        className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Social Links Tab */}
          {activeTab === 'social' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-black">Social Media Links</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">🐦 Twitter Profile</label>
                  <input
                    type="text"
                    value={socialLinks.twitter}
                    onChange={(e) => setSocialLinks(prev => ({ ...prev, twitter: e.target.value }))}
                    placeholder="https://twitter.com/your-username"
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">💬 Discord</label>
                  <input
                    type="text"
                    value={socialLinks.discord}
                    onChange={(e) => setSocialLinks(prev => ({ ...prev, discord: e.target.value }))}
                    placeholder="https://discord.gg/your-invite"
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">📱 Telegram</label>
                  <input
                    type="text"
                    value={socialLinks.telegram}
                    onChange={(e) => setSocialLinks(prev => ({ ...prev, telegram: e.target.value }))}
                    placeholder="https://t.me/your-username"
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">🌐 Website</label>
                  <input
                    type="text"
                    value={socialLinks.website}
                    onChange={(e) => setSocialLinks(prev => ({ ...prev, website: e.target.value }))}
                    placeholder="https://your-website.com"
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">💼 LinkedIn</label>
                  <input
                    type="text"
                    value={socialLinks.linkedin}
                    onChange={(e) => setSocialLinks(prev => ({ ...prev, linkedin: e.target.value }))}
                    placeholder="https://linkedin.com/in/your-profile"
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  />
                </div>
              </div>
              
              <button
                onClick={handleSaveSocialLinks}
                className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium transition-all"
              >
                Update Social Links
              </button>
            </div>
          )}

          {/* Share Profile Tab */}
          {activeTab === 'share' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-xl">
                <h3 className="text-lg font-semibold text-black mb-4">Share Your Trading Profile</h3>
                <p className="text-gray-700 mb-4">
                  Your public profile is ready to share! Show off your trading achievements and connect with other traders.
                </p>
                
                <div className="bg-white p-4 rounded-lg mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Your Public Profile URL</label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={getPublicProfileLink()}
                      readOnly
                      className="flex-1 bg-gray-50 border border-gray-300 rounded-lg px-4 py-2 text-gray-700"
                    />
                    <button
                      onClick={copyProfileLink}
                      className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-all"
                    >
                      📋 Copy
                    </button>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={shareOnTwitter}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-all"
                  >
                    🐦 Share on Twitter
                  </button>
                  <a
                    href={getPublicProfileLink()}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium transition-all"
                  >
                    👁️ Preview Profile
                  </a>
                </div>
              </div>

              {/* Profile Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-xl border border-gray-200 text-center">
                  <div className="text-2xl font-bold text-black">{tradingHighlights.length}</div>
                  <div className="text-sm text-gray-600">Trading Highlights</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 text-center">
                  <div className="text-2xl font-bold text-black">{Object.values(socialLinks).filter(link => link).length}</div>
                  <div className="text-sm text-gray-600">Social Links</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 text-center">
                  <div className="text-2xl font-bold text-black">{currentUser.profile_complete ? '✅' : '⚠️'}</div>
                  <div className="text-sm text-gray-600">Profile Status</div>
                </div>
              </div>

              {/* Tips */}
              <div className="bg-blue-50 p-6 rounded-xl">
                <h4 className="font-semibold text-blue-800 mb-3">💡 Tips for Better Engagement</h4>
                <ul className="space-y-2 text-blue-700 text-sm">
                  <li>• Add PnL screenshots to showcase your trading success</li>
                  <li>• Connect your social media for better credibility</li>
                  <li>• Write detailed descriptions for your trading highlights</li>
                  <li>• Share your profile on Twitter and trading communities</li>
                  <li>• Keep your trading experience and preferences up to date</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileManager;