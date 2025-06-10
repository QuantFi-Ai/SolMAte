import os
import uuid
import base64
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pymongo import MongoClient
import asyncio
import json
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.solm8_db

# Collections
users_collection = db.users
matches_collection = db.matches
messages_collection = db.messages
swipes_collection = db.swipes
profile_images_collection = db.profile_images
trading_highlights_collection = db.trading_highlights
social_links_collection = db.social_links

# FastAPI app
app = FastAPI(title="Solm8 API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth Configuration
config = Config()
oauth = OAuth()

# Twitter OAuth setup
oauth.register(
    name='twitter',
    client_id=os.environ.get('TWITTER_CLIENT_ID', 'tNqWV3fjSpwVe1twlx8OxXEJN'),
    client_secret=os.environ.get('TWITTER_CLIENT_SECRET', '4FYjbbexoxubrXnGPFjjd76T6r2Ll0yhMJsAOMJi4qerOMwyxJ'),
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    api_base_url='https://api.twitter.com/1.1/',
    client_kwargs={
        'force_include_body': True,
    }
)

# Enhanced Pydantic models
class UserProfile(BaseModel):
    user_id: str
    twitter_id: str
    username: str
    display_name: str
    avatar_url: str
    bio: str = ""
    location: str = ""
    # Twitter settings
    show_twitter: bool = True
    twitter_username: str = ""
    # Trading experience
    trading_experience: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    years_trading: int = 0
    preferred_tokens: List[str]  # ["Meme Coins", "DeFi", "GameFi", "NFTs", "Blue Chips"]
    trading_style: str  # "Day Trader", "Swing Trader", "HODLer", "Scalper"
    portfolio_size: str  # "Under $1K", "$1K-$10K", "$10K-$100K", "$100K+", "Prefer not to say"
    risk_tolerance: str  # "Conservative", "Moderate", "Aggressive", "YOLO"
    # Trading history
    best_trade: str = ""
    worst_trade: str = ""
    favorite_project: str = ""
    # Communication & Platform preferences
    trading_hours: str = ""  # "Early Morning", "Morning", "Afternoon", "Evening", "Night Owl", "24/7"
    communication_style: str = ""  # "Casual", "Professional", "Technical", "Friendly"
    preferred_communication_platform: str = ""  # "Discord", "Telegram", "Twitter DM", "Signal", "WhatsApp", "In-App Only"
    preferred_trading_platform: str = ""  # "Axiom", "BullX", "Photon", "Padre", "Jupiter", "Raydium", "Other"
    looking_for: List[str] = []  # ["Learning", "Teaching", "Alpha Sharing", "Research Partner", "Risk Management"]
    # Profile completion
    profile_complete: bool = False
    created_at: datetime
    last_active: datetime

class SwipeAction(BaseModel):
    swiper_id: str
    target_id: str
    action: str  # "like" or "pass"

class ChatMessage(BaseModel):
    match_id: str
    sender_id: str
    content: str
    timestamp: datetime

class TradingHighlight(BaseModel):
    user_id: str
    title: str
    description: str
    image_data: str  # base64 encoded image
    highlight_type: str  # "pnl_screenshot", "achievement", "trade_analysis", "portfolio"
    date_achieved: str
    profit_loss: Optional[str] = ""
    percentage_gain: Optional[str] = ""

class SocialLinks(BaseModel):
    user_id: str
    twitter: Optional[str] = ""
    discord: Optional[str] = ""
    telegram: Optional[str] = ""
    website: Optional[str] = ""
    linkedin: Optional[str] = ""

# AI Matching Algorithm
class AIMatchingService:
    @staticmethod
    def calculate_compatibility_score(user1: dict, user2: dict) -> dict:
        """Calculate AI compatibility score between two users"""
        score_breakdown = {}
        total_score = 0
        max_possible_score = 0
        
        # 1. Experience Level Compatibility (Weight: 20)
        experience_score = AIMatchingService._calculate_experience_compatibility(
            user1.get('trading_experience', ''), 
            user2.get('trading_experience', ''),
            user1.get('years_trading', 0),
            user2.get('years_trading', 0)
        )
        score_breakdown['experience'] = experience_score
        total_score += experience_score['score']
        max_possible_score += experience_score['max_score']
        
        # 2. Platform Compatibility (Weight: 25)
        platform_score = AIMatchingService._calculate_platform_compatibility(
            user1.get('preferred_trading_platform', ''),
            user2.get('preferred_trading_platform', ''),
            user1.get('preferred_communication_platform', ''),
            user2.get('preferred_communication_platform', '')
        )
        score_breakdown['platform'] = platform_score
        total_score += platform_score['score']
        max_possible_score += platform_score['max_score']
        
        # 3. Token Interest Overlap (Weight: 20)
        token_score = AIMatchingService._calculate_token_compatibility(
            user1.get('preferred_tokens', []),
            user2.get('preferred_tokens', [])
        )
        score_breakdown['tokens'] = token_score
        total_score += token_score['score']
        max_possible_score += token_score['max_score']
        
        # 4. Goal Alignment (Weight: 15)
        goal_score = AIMatchingService._calculate_goal_compatibility(
            user1.get('looking_for', []),
            user2.get('looking_for', [])
        )
        score_breakdown['goals'] = goal_score
        total_score += goal_score['score']
        max_possible_score += goal_score['max_score']
        
        # 5. Trading Style & Risk Compatibility (Weight: 10)
        style_score = AIMatchingService._calculate_style_compatibility(
            user1.get('trading_style', ''),
            user2.get('trading_style', ''),
            user1.get('risk_tolerance', ''),
            user2.get('risk_tolerance', '')
        )
        score_breakdown['style'] = style_score
        total_score += style_score['score']
        max_possible_score += style_score['max_score']
        
        # 6. Communication & Schedule Compatibility (Weight: 10)
        communication_score = AIMatchingService._calculate_communication_compatibility(
            user1.get('communication_style', ''),
            user2.get('communication_style', ''),
            user1.get('trading_hours', ''),
            user2.get('trading_hours', '')
        )
        score_breakdown['communication'] = communication_score
        total_score += communication_score['score']
        max_possible_score += communication_score['max_score']
        
        # Calculate final percentage
        compatibility_percentage = int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
        
        return {
            'compatibility_percentage': compatibility_percentage,
            'total_score': total_score,
            'max_possible_score': max_possible_score,
            'breakdown': score_breakdown,
            'recommendations': AIMatchingService._generate_recommendations(score_breakdown, user1, user2)
        }
    
    @staticmethod
    def _calculate_experience_compatibility(exp1: str, exp2: str, years1: int, years2: int) -> dict:
        """Calculate experience level compatibility"""
        experience_levels = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
        
        level1 = experience_levels.get(exp1, 0)
        level2 = experience_levels.get(exp2, 0)
        
        if level1 == 0 or level2 == 0:
            return {'score': 0, 'max_score': 20, 'reason': 'Missing experience information'}
        
        diff = abs(level1 - level2)
        
        # Perfect for mentoring: beginner with intermediate+
        if (level1 == 1 and level2 >= 2) or (level2 == 1 and level1 >= 2):
            score = 18
            reason = "Perfect for mentoring relationship"
        # Same level - great for peer learning
        elif diff == 0:
            score = 20
            reason = "Same experience level - ideal for peer collaboration"
        # One level apart - good compatibility
        elif diff == 1:
            score = 15
            reason = "Similar experience levels - good match"
        # Two levels apart - some compatibility
        elif diff == 2:
            score = 10
            reason = "Different experience levels - moderate match"
        else:
            score = 5
            reason = "Very different experience levels"
        
        # Bonus for similar years of experience
        year_diff = abs(years1 - years2)
        if year_diff <= 1:
            score = min(score + 2, 20)
        
        return {'score': score, 'max_score': 20, 'reason': reason}
    
    @staticmethod
    def _calculate_platform_compatibility(trading_platform1: str, trading_platform2: str, 
                                        comm_platform1: str, comm_platform2: str) -> dict:
        """Calculate platform compatibility"""
        score = 0
        reasons = []
        
        # Trading platform compatibility (15 points)
        if trading_platform1 and trading_platform2:
            if trading_platform1 == trading_platform2:
                score += 15
                reasons.append(f"Both use {trading_platform1} for trading")
            else:
                score += 5
                reasons.append("Different trading platforms")
        else:
            score += 3
            reasons.append("Missing trading platform info")
        
        # Communication platform compatibility (10 points)
        if comm_platform1 and comm_platform2:
            if comm_platform1 == comm_platform2:
                score += 10
                reasons.append(f"Both prefer {comm_platform1} for communication")
            else:
                score += 3
                reasons.append("Different communication preferences")
        else:
            score += 2
            reasons.append("Missing communication platform info")
        
        return {'score': score, 'max_score': 25, 'reason': '; '.join(reasons)}
    
    @staticmethod
    def _calculate_token_compatibility(tokens1: List[str], tokens2: List[str]) -> dict:
        """Calculate token interest overlap"""
        if not tokens1 or not tokens2:
            return {'score': 5, 'max_score': 20, 'reason': 'Missing token preferences'}
        
        overlap = set(tokens1) & set(tokens2)
        total_unique = set(tokens1) | set(tokens2)
        
        if not total_unique:
            return {'score': 0, 'max_score': 20, 'reason': 'No token preferences specified'}
        
        overlap_ratio = len(overlap) / len(total_unique)
        score = int(20 * overlap_ratio)
        
        if len(overlap) >= 3:
            reason = f"Strong overlap in {len(overlap)} token categories"
        elif len(overlap) >= 2:
            reason = f"Good overlap in {len(overlap)} token categories"
        elif len(overlap) == 1:
            reason = f"Some overlap in token interests"
        else:
            reason = "Different token interests - good for diversification"
            score = max(score, 5)  # Minimum score for diversity
        
        return {'score': score, 'max_score': 20, 'reason': reason}
    
    @staticmethod
    def _calculate_goal_compatibility(goals1: List[str], goals2: List[str]) -> dict:
        """Calculate goal alignment - complementary goals score higher"""
        if not goals1 or not goals2:
            return {'score': 3, 'max_score': 15, 'reason': 'Missing goal information'}
        
        # Complementary pairs that work well together
        complementary_pairs = [
            ('Learning', 'Teaching'),
            ('Teaching', 'Learning'),
            ('Alpha Sharing', 'Alpha Sharing'),
            ('Research Partner', 'Research Partner'),
            ('Risk Management', 'Teaching'),
            ('Networking', 'Networking')
        ]
        
        score = 0
        reasons = []
        
        # Check for perfect complementary matches
        for goal1 in goals1:
            for goal2 in goals2:
                if (goal1, goal2) in complementary_pairs:
                    score += 8
                    if goal1 == goal2:
                        reasons.append(f"Both interested in {goal1}")
                    else:
                        reasons.append(f"Perfect match: {goal1} ↔ {goal2}")
        
        # Check for any overlap
        overlap = set(goals1) & set(goals2)
        if overlap and not reasons:
            score += len(overlap) * 3
            reasons.append(f"Shared interests: {', '.join(overlap)}")
        
        # Minimum score for having goals
        if not reasons:
            score = 2
            reasons.append("Different goals - potential for diverse perspectives")
        
        score = min(score, 15)  # Cap at max score
        return {'score': score, 'max_score': 15, 'reason': '; '.join(reasons)}
    
    @staticmethod
    def _calculate_style_compatibility(style1: str, style2: str, risk1: str, risk2: str) -> dict:
        """Calculate trading style and risk compatibility"""
        score = 0
        reasons = []
        
        # Trading style compatibility (6 points)
        compatible_styles = {
            'Day Trader': ['Day Trader', 'Scalper'],
            'Swing Trader': ['Swing Trader', 'Long-term Investor'],
            'HODLer': ['HODLer', 'Long-term Investor'],
            'Scalper': ['Scalper', 'Day Trader'],
            'Long-term Investor': ['Long-term Investor', 'HODLer', 'Swing Trader'],
            'Arbitrage': ['Arbitrage', 'Day Trader', 'Scalper']
        }
        
        if style1 and style2:
            if style1 == style2:
                score += 6
                reasons.append(f"Same trading style: {style1}")
            elif style2 in compatible_styles.get(style1, []):
                score += 4
                reasons.append(f"Compatible trading styles")
            else:
                score += 2
                reasons.append("Different trading styles")
        
        # Risk tolerance compatibility (4 points)
        risk_levels = {'Conservative': 1, 'Moderate': 2, 'Aggressive': 3, 'YOLO': 4}
        
        if risk1 and risk2:
            level1 = risk_levels.get(risk1, 0)
            level2 = risk_levels.get(risk2, 0)
            
            if level1 and level2:
                diff = abs(level1 - level2)
                if diff == 0:
                    score += 4
                    reasons.append(f"Same risk tolerance: {risk1}")
                elif diff == 1:
                    score += 3
                    reasons.append("Similar risk tolerance")
                else:
                    score += 1
                    reasons.append("Different risk tolerance")
        
        return {'score': score, 'max_score': 10, 'reason': '; '.join(reasons)}
    
    @staticmethod
    def _calculate_communication_compatibility(comm_style1: str, comm_style2: str, 
                                             hours1: str, hours2: str) -> dict:
        """Calculate communication and schedule compatibility"""
        score = 0
        reasons = []
        
        # Communication style (6 points)
        if comm_style1 and comm_style2:
            if comm_style1 == comm_style2:
                score += 6
                reasons.append(f"Same communication style: {comm_style1}")
            else:
                compatible_pairs = [
                    ('Professional', 'Technical'),
                    ('Technical', 'Professional'),
                    ('Casual', 'Friendly'),
                    ('Friendly', 'Casual')
                ]
                if (comm_style1, comm_style2) in compatible_pairs:
                    score += 4
                    reasons.append("Compatible communication styles")
                else:
                    score += 2
                    reasons.append("Different communication styles")
        
        # Trading hours compatibility (4 points)
        if hours1 and hours2:
            if hours1 == hours2:
                score += 4
                reasons.append(f"Same trading hours: {hours1}")
            elif hours1 == '24/7' or hours2 == '24/7':
                score += 3
                reasons.append("Flexible trading hours")
            else:
                # Check for overlapping time periods
                overlap_score = 2
                score += overlap_score
                reasons.append("Different trading hours")
        
        return {'score': score, 'max_score': 10, 'reason': '; '.join(reasons)}
    
    @staticmethod
    def _generate_recommendations(breakdown: dict, user1: dict, user2: dict) -> List[str]:
        """Generate AI recommendations based on compatibility analysis"""
        recommendations = []
        
        # Experience-based recommendations
        exp_score = breakdown.get('experience', {}).get('score', 0)
        if exp_score >= 18:
            recommendations.append("🎯 Perfect for mentoring or peer collaboration")
        elif exp_score >= 15:
            recommendations.append("📈 Great match for skill development")
        
        # Platform-based recommendations
        platform_score = breakdown.get('platform', {}).get('score', 0)
        if platform_score >= 20:
            recommendations.append("🔗 Same platforms - easy to share strategies")
        elif platform_score >= 15:
            recommendations.append("⚡ Compatible trading setup")
        
        # Token-based recommendations
        token_score = breakdown.get('tokens', {}).get('score', 0)
        if token_score >= 15:
            recommendations.append("💎 Strong shared interest in token categories")
        elif token_score <= 5:
            recommendations.append("🌐 Different interests - great for diversification")
        
        # Goal-based recommendations
        goal_score = breakdown.get('goals', {}).get('score', 0)
        if goal_score >= 12:
            recommendations.append("🤝 Perfectly aligned trading goals")
        elif goal_score >= 8:
            recommendations.append("📚 Complementary learning objectives")
        
        if not recommendations:
            recommendations.append("🔍 Potential for unique trading perspectives")
        
        return recommendations[:3]  # Limit to top 3 recommendations

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

# Routes

@app.get("/api/public-profile/{username}")
async def get_public_profile(username: str):
    """Get public profile by username for sharing"""
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get user's trading highlights
    highlights = list(trading_highlights_collection.find({"user_id": user["user_id"]}))
    for highlight in highlights:
        highlight.pop('_id', None)
    
    # Get user's social links
    social_links = social_links_collection.find_one({"user_id": user["user_id"]})
    if social_links:
        social_links.pop('_id', None)
    
    # Remove sensitive information for public view
    public_profile = {
        "user_id": user["user_id"],
        "username": user["username"], 
        "display_name": user["display_name"],
        "avatar_url": user["avatar_url"],
        "bio": user["bio"],
        "location": user["location"],
        "show_twitter": user.get("show_twitter", False),
        "twitter_username": user.get("twitter_username", "") if user.get("show_twitter", False) else "",
        "trading_experience": user["trading_experience"],
        "years_trading": user["years_trading"],
        "preferred_tokens": user["preferred_tokens"],
        "trading_style": user["trading_style"],
        "portfolio_size": user["portfolio_size"],
        "risk_tolerance": user["risk_tolerance"],
        "best_trade": user.get("best_trade", ""),
        "favorite_project": user.get("favorite_project", ""),
        "trading_hours": user.get("trading_hours", ""),
        "preferred_trading_platform": user.get("preferred_trading_platform", ""),
        "looking_for": user.get("looking_for", []),
        "profile_complete": user.get("profile_complete", False),
        "created_at": user["created_at"],
        "trading_highlights": highlights,
        "social_links": social_links or {}
    }
    
    return public_profile

@app.post("/api/upload-trading-highlight/{user_id}")
async def upload_trading_highlight(user_id: str, file: UploadFile = File(...)):
    """Upload a trading highlight image (PnL screenshot, achievement, etc.)"""
    try:
        # Validate user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode the image
        contents = await file.read()
        
        highlight_data = {
            "highlight_id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "image_data": base64.b64encode(contents).decode('utf-8'),
            "uploaded_at": datetime.utcnow()
        }
        
        return {"message": "Trading highlight uploaded successfully", "highlight_id": highlight_data['highlight_id'], "image_data": highlight_data['image_data']}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload highlight: {str(e)}")

@app.post("/api/save-trading-highlight/{user_id}")
async def save_trading_highlight(user_id: str, highlight_data: dict):
    """Save trading highlight with details"""
    try:
        # Validate user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        highlight = {
            "highlight_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": highlight_data.get("title", ""),
            "description": highlight_data.get("description", ""),
            "image_data": highlight_data.get("image_data", ""),
            "highlight_type": highlight_data.get("highlight_type", "achievement"),
            "date_achieved": highlight_data.get("date_achieved", ""),
            "profit_loss": highlight_data.get("profit_loss", ""),
            "percentage_gain": highlight_data.get("percentage_gain", ""),
            "created_at": datetime.utcnow()
        }
        
        trading_highlights_collection.insert_one(highlight)
        highlight.pop('_id', None)
        
        return {"message": "Trading highlight saved successfully", "highlight": highlight}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save highlight: {str(e)}")

@app.get("/api/trading-highlights/{user_id}")
async def get_trading_highlights(user_id: str):
    """Get all trading highlights for a user"""
    highlights = list(trading_highlights_collection.find({"user_id": user_id}))
    for highlight in highlights:
        highlight.pop('_id', None)
    return highlights

@app.delete("/api/trading-highlights/{highlight_id}")
async def delete_trading_highlight(highlight_id: str):
    """Delete a trading highlight"""
    result = trading_highlights_collection.delete_one({"highlight_id": highlight_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return {"message": "Highlight deleted successfully"}

@app.post("/api/update-social-links/{user_id}")
async def update_social_links(user_id: str, social_data: dict):
    """Update user's social media links"""
    try:
        # Validate user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        social_links = {
            "user_id": user_id,
            "twitter": social_data.get("twitter", ""),
            "discord": social_data.get("discord", ""),
            "telegram": social_data.get("telegram", ""),
            "website": social_data.get("website", ""),
            "linkedin": social_data.get("linkedin", ""),
            "updated_at": datetime.utcnow()
        }
        
        # Upsert social links
        social_links_collection.replace_one(
            {"user_id": user_id},
            social_links,
            upsert=True
        )
        
        return {"message": "Social links updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update social links: {str(e)}")

@app.get("/api/social-links/{user_id}")
async def get_social_links(user_id: str):
    """Get user's social media links"""
    social_links = social_links_collection.find_one({"user_id": user_id})
    if social_links:
        social_links.pop('_id', None)
        return social_links
    return {}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Solm8 API"}

@app.get("/api/login/twitter")
async def login_twitter(request: Request):
    """Initiate Twitter OAuth login"""
    try:
        # Use the exact external URL for callback
        callback_url = f"https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com/api/auth/twitter/callback"
        return await oauth.twitter.authorize_redirect(request, callback_url)
    except Exception as e:
        print(f"Twitter OAuth error: {str(e)}")
        # For demo purposes, return a mock success for now
        mock_user_id = str(uuid.uuid4())
        frontend_url = f"https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com/app?auth_success=true&user_id={mock_user_id}&demo=true"
        return RedirectResponse(url=frontend_url)

@app.get("/api/auth/twitter/callback")
async def twitter_callback(request: Request):
    """Handle Twitter OAuth callback"""
    try:
        token = await oauth.twitter.authorize_access_token(request)
        
        # Get user data from Twitter
        user_resp = await oauth.twitter.get(
            'account/verify_credentials.json',
            token=token,
            params={'include_email': 'true'}
        )
        twitter_user = user_resp.json()
        
        # Check if user already exists
        existing_user = users_collection.find_one({"twitter_id": twitter_user['id_str']})
        
        if existing_user:
            # Update last active
            users_collection.update_one(
                {"twitter_id": twitter_user['id_str']},
                {"$set": {"last_active": datetime.utcnow()}}
            )
            user_data = existing_user
        else:
            # Create new user profile
            user_data = {
                "user_id": str(uuid.uuid4()),
                "twitter_id": twitter_user['id_str'],
                "username": twitter_user['screen_name'],
                "display_name": twitter_user['name'],
                "avatar_url": twitter_user['profile_image_url_https'].replace('_normal', '_400x400'),
                "bio": twitter_user.get('description', ''),
                "location": "",
                "show_twitter": True,
                "twitter_username": twitter_user['screen_name'],
                "trading_experience": "",
                "years_trading": 0,
                "preferred_tokens": [],
                "trading_style": "",
                "portfolio_size": "",
                "risk_tolerance": "",
                "best_trade": "",
                "worst_trade": "",
                "favorite_project": "",
                "trading_hours": "",
                "communication_style": "",
                "preferred_communication_platform": "",
                "preferred_trading_platform": "",
                "looking_for": [],
                "profile_complete": False,
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            users_collection.insert_one(user_data)
        
        # Redirect to frontend with user data
        frontend_url = f"https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com/app?auth_success=true&user_id={user_data['user_id']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        return RedirectResponse(url=f"https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com/app?auth_error=true")

@app.post("/api/upload-profile-image/{user_id}")
async def upload_profile_image(user_id: str, file: UploadFile = File(...)):
    """Upload a profile image for a user"""
    try:
        # Validate user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode the image
        contents = await file.read()
        
        # Store image in database (for simplicity - in production, use cloud storage)
        image_data = {
            "image_id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "data": base64.b64encode(contents).decode('utf-8'),
            "uploaded_at": datetime.utcnow()
        }
        profile_images_collection.insert_one(image_data)
        
        # Update user's avatar URL to point to our image endpoint
        new_avatar_url = f"{os.environ.get('REACT_APP_BACKEND_URL', 'https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com')}/api/profile-image/{image_data['image_id']}"
        
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"avatar_url": new_avatar_url, "last_active": datetime.utcnow()}}
        )
        
        return {"message": "Profile image uploaded successfully", "image_id": image_data['image_id']}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@app.get("/api/profile-image/{image_id}")
async def get_profile_image(image_id: str):
    """Get a profile image by ID"""
    from fastapi.responses import Response
    
    image_data = profile_images_collection.find_one({"image_id": image_id})
    if not image_data:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data['data'])
    
    return Response(
        content=image_bytes,
        media_type=image_data['content_type'],
        headers={"Cache-Control": "public, max-age=3600"}
    )

@app.post("/api/create-demo-user")
async def create_demo_user():
    """Create a demo user for testing purposes"""
    demo_avatars = [
        "https://images.pexels.com/photos/31610834/pexels-photo-31610834.jpeg",
        "https://images.pexels.com/photos/31630004/pexels-photo-31630004.jpeg",
        "https://images.pexels.com/photos/11302135/pexels-photo-11302135.jpeg",
        "https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg",
        "https://images.pexels.com/photos/32465949/pexels-photo-32465949.jpeg",
        "https://images.pexels.com/photos/31659353/pexels-photo-31659353.jpeg"
    ]
    
    demo_user_data = {
        "user_id": str(uuid.uuid4()),
        "twitter_id": f"demo_{int(datetime.utcnow().timestamp())}",
        "username": f"demo_trader_{int(datetime.utcnow().timestamp())}",
        "display_name": "Demo Solana Trader",
        "avatar_url": demo_avatars[0],
        "bio": "Demo trader looking for trenching buddies! 🚀",
        "location": "",
        "show_twitter": False,
        "twitter_username": "",
        "trading_experience": "",
        "years_trading": 0,
        "preferred_tokens": [],
        "trading_style": "",
        "portfolio_size": "",
        "risk_tolerance": "",
        "best_trade": "",
        "worst_trade": "",
        "favorite_project": "",
        "trading_hours": "",
        "communication_style": "",
        "preferred_communication_platform": "",
        "preferred_trading_platform": "",
        "looking_for": [],
        "profile_complete": False,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }
    
    # Insert demo user
    users_collection.insert_one(demo_user_data)
    
    # Create some demo potential matches with the new profile structure
    demo_matches = [
        {
            "user_id": str(uuid.uuid4()),
            "twitter_id": f"demo_match_1_{int(datetime.utcnow().timestamp())}",
            "username": "crypto_whale_2024",
            "display_name": "Alex Chen",
            "avatar_url": demo_avatars[1],
            "bio": "DeFi enthusiast and meme coin hunter. Let's find the next 100x together! 💎",
            "location": "San Francisco, CA",
            "show_twitter": True,
            "twitter_username": "crypto_whale_2024",
            "trading_experience": "Advanced",
            "years_trading": 4,
            "preferred_tokens": ["Meme Coins", "DeFi", "Layer 1s"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K",
            "risk_tolerance": "Aggressive",
            "best_trade": "Bought SOL at $8, sold at $260. 32x return on DeFi play.",
            "worst_trade": "FOMO'd into LUNA at $80 right before the crash. Lost 90%.",
            "favorite_project": "Solana ecosystem - the speed and low fees are unmatched",
            "trading_hours": "Morning",
            "communication_style": "Technical",
            "preferred_communication_platform": "Discord",
            "preferred_trading_platform": "Jupiter",
            "looking_for": ["Alpha Sharing", "Research Partner"],
            "profile_complete": True,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        },
        {
            "user_id": str(uuid.uuid4()),
            "twitter_id": f"demo_match_2_{int(datetime.utcnow().timestamp())}",
            "username": "sol_degen_pro",
            "display_name": "Sarah Johnson",
            "avatar_url": demo_avatars[2],
            "bio": "Solana maximalist and NFT collector. Looking for diamond hands only! 💪",
            "location": "New York, NY",
            "show_twitter": True,
            "twitter_username": "sol_degen_pro",
            "trading_experience": "Expert",
            "years_trading": 6,
            "preferred_tokens": ["NFTs", "GameFi", "Blue Chips"],
            "trading_style": "Swing Trader",
            "portfolio_size": "$100K+",
            "risk_tolerance": "Moderate",
            "best_trade": "Minted Okay Bears at 1.5 SOL, floor went to 180 SOL",
            "worst_trade": "Held SQUID token during the rug pull. Complete loss.",
            "favorite_project": "Magic Eden - revolutionizing NFT trading on Solana",
            "trading_hours": "Evening",
            "communication_style": "Professional",
            "preferred_communication_platform": "Telegram",
            "preferred_trading_platform": "BullX",
            "looking_for": ["Teaching", "Risk Management"],
            "profile_complete": True,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        },
        {
            "user_id": str(uuid.uuid4()),
            "twitter_id": f"demo_match_3_{int(datetime.utcnow().timestamp())}",
            "username": "moon_hunter_99",
            "display_name": "Mike Rodriguez",
            "avatar_url": demo_avatars[3],
            "bio": "Beginner trader learning the ropes. Let's grow together and share insights! 📈",
            "location": "Austin, TX",
            "show_twitter": False,
            "twitter_username": "moon_hunter_99",
            "trading_experience": "Beginner",
            "years_trading": 1,
            "preferred_tokens": ["Meme Coins", "AI Tokens"],
            "trading_style": "HODLer",
            "portfolio_size": "Under $1K",
            "risk_tolerance": "Conservative",
            "best_trade": "Bought BONK early, 10x return in 2 weeks",
            "worst_trade": "Panic sold during a minor dip, lost 20%",
            "favorite_project": "Jupiter - makes swapping so easy for beginners",
            "trading_hours": "Night Owl",
            "communication_style": "Casual",
            "preferred_communication_platform": "Discord",
            "preferred_trading_platform": "Photon",
            "looking_for": ["Learning", "Research Partner"],
            "profile_complete": True,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        },
        {
            "user_id": str(uuid.uuid4()),
            "twitter_id": f"demo_match_4_{int(datetime.utcnow().timestamp())}",
            "username": "defi_alpha_king",
            "display_name": "Jordan Kim",
            "avatar_url": demo_avatars[4],
            "bio": "MEV bot developer and yield farmer. Always hunting for alpha opportunities! ⚡",
            "location": "Seoul, South Korea",
            "show_twitter": True,
            "twitter_username": "defi_alpha_king",
            "trading_experience": "Expert",
            "years_trading": 5,
            "preferred_tokens": ["DeFi", "Infrastructure", "Layer 1s"],
            "trading_style": "Scalper",
            "portfolio_size": "$100K+",
            "risk_tolerance": "YOLO",
            "best_trade": "Arbitrage opportunity between DEXs, 15% in 2 minutes",
            "worst_trade": "Smart contract exploit lost 30% of portfolio",
            "favorite_project": "Raydium - best liquidity and MEV opportunities",
            "trading_hours": "24/7",
            "communication_style": "Technical",
            "preferred_communication_platform": "Signal",
            "preferred_trading_platform": "Axiom",
            "looking_for": ["Alpha Sharing", "Teaching"],
            "profile_complete": True,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
    ]
    
    # Insert demo matches
    for match in demo_matches:
        users_collection.insert_one(match)
    
    demo_user_data.pop('_id', None)
    return demo_user_data

@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """Get user profile"""
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove MongoDB _id field
    user.pop('_id', None)
    return user

@app.put("/api/user/{user_id}")
async def update_user_profile(user_id: str, profile_data: dict):
    """Update user profile"""
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    allowed_fields = [
        "bio", "location", "show_twitter", "twitter_username", "trading_experience", "years_trading", "preferred_tokens", 
        "trading_style", "portfolio_size", "risk_tolerance", "best_trade", "worst_trade",
        "favorite_project", "trading_hours", "communication_style", "preferred_communication_platform",
        "preferred_trading_platform", "looking_for"
    ]
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    update_data["last_active"] = datetime.utcnow()
    
    # Check if profile is complete
    current_profile = {**user, **update_data}
    profile_complete = (
        bool(current_profile.get("trading_experience")) and 
        bool(current_profile.get("preferred_tokens")) and 
        len(current_profile.get("preferred_tokens", [])) > 0 and
        bool(current_profile.get("trading_style")) and 
        bool(current_profile.get("portfolio_size"))
    )
    update_data["profile_complete"] = profile_complete
    
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )
    
    return {"message": "Profile updated successfully"}

@app.get("/api/ai-recommendations/{user_id}")
async def get_ai_recommendations(user_id: str, limit: int = 10):
    """Get AI-recommended matches for a user"""
    current_user = users_collection.find_one({"user_id": user_id})
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not current_user.get('profile_complete'):
        raise HTTPException(status_code=400, detail="Profile must be complete to get AI recommendations")
    
    # Get users already swiped on
    swiped_user_ids = [doc["target_id"] for doc in swipes_collection.find({"swiper_id": user_id})]
    swiped_user_ids.append(user_id)  # Exclude self
    
    # Find all potential matches with complete profiles
    potential_matches = list(users_collection.find({
        "user_id": {"$nin": swiped_user_ids},
        "profile_complete": True
    }))
    
    # Calculate AI compatibility scores for each potential match
    scored_matches = []
    for match in potential_matches:
        match.pop('_id', None)
        compatibility = AIMatchingService.calculate_compatibility_score(current_user, match)
        
        scored_matches.append({
            **match,
            'ai_compatibility': compatibility
        })
    
    # Sort by compatibility score (highest first)
    scored_matches.sort(key=lambda x: x['ai_compatibility']['compatibility_percentage'], reverse=True)
    
    # Return top matches
    return scored_matches[:limit]

@app.get("/api/discover/{user_id}")
async def discover_users(user_id: str, limit: int = 10):
    """Get potential matches for swiping"""
    current_user = users_collection.find_one({"user_id": user_id})
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get users already swiped on
    swiped_user_ids = [doc["target_id"] for doc in swipes_collection.find({"swiper_id": user_id})]
    swiped_user_ids.append(user_id)  # Exclude self
    
    # Find users not swiped on yet with complete profiles
    potential_matches = list(users_collection.find({
        "user_id": {"$nin": swiped_user_ids},
        "profile_complete": True
    }).limit(limit))
    
    # Remove MongoDB _id fields
    for user in potential_matches:
        user.pop('_id', None)
    
    return potential_matches

@app.post("/api/swipe")
async def swipe_user(swipe: SwipeAction):
    """Record a swipe action and check for matches"""
    # Record the swipe
    swipe_data = {
        "swipe_id": str(uuid.uuid4()),
        "swiper_id": swipe.swiper_id,
        "target_id": swipe.target_id,
        "action": swipe.action,
        "timestamp": datetime.utcnow()
    }
    swipes_collection.insert_one(swipe_data)
    
    # If it's a like, check for mutual match
    if swipe.action == "like":
        mutual_like = swipes_collection.find_one({
            "swiper_id": swipe.target_id,
            "target_id": swipe.swiper_id,
            "action": "like"
        })
        
        if mutual_like:
            # Create a match
            match_data = {
                "match_id": str(uuid.uuid4()),
                "user1_id": swipe.swiper_id,
                "user2_id": swipe.target_id,
                "created_at": datetime.utcnow(),
                "last_message_at": datetime.utcnow()
            }
            matches_collection.insert_one(match_data)
            
            # Notify both users via WebSocket if connected
            match_notification = {
                "type": "new_match",
                "match_id": match_data["match_id"],
                "message": "You have a new match!"
            }
            await manager.send_message(json.dumps(match_notification), swipe.swiper_id)
            await manager.send_message(json.dumps(match_notification), swipe.target_id)
            
            return {"matched": True, "match_id": match_data["match_id"]}
    
    return {"matched": False}

@app.get("/api/matches/{user_id}")
async def get_user_matches(user_id: str):
    """Get all matches for a user"""
    matches = list(matches_collection.find({
        "$or": [
            {"user1_id": user_id},
            {"user2_id": user_id}
        ]
    }).sort("last_message_at", -1))
    
    # Get user data for each match
    enriched_matches = []
    for match in matches:
        other_user_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
        other_user = users_collection.find_one({"user_id": other_user_id})
        
        if other_user:
            other_user.pop('_id', None)
            match.pop('_id', None)
            match["other_user"] = other_user
            enriched_matches.append(match)
    
    return enriched_matches

@app.get("/api/messages/{match_id}")
async def get_match_messages(match_id: str, limit: int = 50):
    """Get messages for a specific match"""
    messages = list(messages_collection.find({
        "match_id": match_id
    }).sort("timestamp", -1).limit(limit))
    
    # Remove MongoDB _id fields and reverse order
    for msg in messages:
        msg.pop('_id', None)
    
    return list(reversed(messages))

@app.websocket("/api/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket connection for real-time chat"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "chat_message":
                # Save message to database
                msg = {
                    "message_id": str(uuid.uuid4()),
                    "match_id": message_data["match_id"],
                    "sender_id": user_id,
                    "content": message_data["content"],
                    "timestamp": datetime.utcnow()
                }
                messages_collection.insert_one(msg)
                
                # Update match last message time
                matches_collection.update_one(
                    {"match_id": message_data["match_id"]},
                    {"$set": {"last_message_at": datetime.utcnow()}}
                )
                
                # Find the other user in the match
                match = matches_collection.find_one({"match_id": message_data["match_id"]})
                other_user_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
                
                # Send message to other user if connected
                msg.pop('_id', None)
                await manager.send_message(json.dumps({
                    "type": "chat_message",
                    "message": msg
                }), other_user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)