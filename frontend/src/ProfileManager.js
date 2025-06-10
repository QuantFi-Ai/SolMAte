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
        setSocialLinks(data);
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
    const text = `Check out my trading profile on SolMatch!`;
    const url = getPublicProfileLink();
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
          <h2 className="text-2xl font-bold text-black">Manage Your Public Profile</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-black transition-all"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-8">
          {/* Public Profile Link */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-xl">
            <h3 className="text-lg font-semibold text-black mb-4">Your Public Profile</h3>
            <div className="flex flex-col sm:flex-row gap-4">
              <input
                type="text"
                value={getPublicProfileLink()}
                readOnly
                className="flex-1 bg-white border border-gray-300 rounded-lg px-4 py-2 text-gray-700"
              />
              <div className="flex space-x-2">
                <button
                  onClick={copyProfileLink}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-all"
                >
                  📋 Copy
                </button>
                <button
                  onClick={shareOnTwitter}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-all"
                >
                  🐦 Share
                </button>
                <a
                  href={getPublicProfileLink()}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-all"
                >
                  👁️ Preview
                </a>
              </div>
            </div>
          </div>

          {/* Social Links */}
          <div>
            <h3 className="text-lg font-semibold text-black mb-4">Social Media Links</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Discord</label>
                <input
                  type="text"
                  value={socialLinks.discord}
                  onChange={(e) => setSocialLinks(prev => ({ ...prev, discord: e.target.value }))}
                  placeholder="https://discord.gg/your-invite"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Telegram</label>
                <input
                  type="text"
                  value={socialLinks.telegram}
                  onChange={(e) => setSocialLinks(prev => ({ ...prev, telegram: e.target.value }))}
                  placeholder="https://t.me/your-username"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Website</label>
                <input
                  type="text"
                  value={socialLinks.website}
                  onChange={(e) => setSocialLinks(prev => ({ ...prev, website: e.target.value }))}
                  placeholder="https://your-website.com"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">LinkedIn</label>
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
              className="mt-4 bg-black hover:bg-gray-800 text-white px-6 py-2 rounded-lg font-medium transition-all"
            >
              Update Social Links
            </button>
          </div>

          {/* Trading Highlights */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-black">Trading Highlights</h3>
              <button
                onClick={() => setShowAddHighlight(true)}
                className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-all"
              >
                + Add Highlight
              </button>
            </div>

            {/* Existing Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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

            {/* Add New Highlight Modal */}
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
        </div>
      </div>
    </div>
  );
};

export default ProfileManager;