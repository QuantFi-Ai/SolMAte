import os
import uuid
import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
import asyncio
import json
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import bcrypt

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'solm8_db')

# Handle MongoDB Atlas connection with proper SSL and authentication
try:
    if 'mongodb+srv://' in MONGO_URL or 'mongodb.net' in MONGO_URL:
        # MongoDB Atlas connection
        client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=False)
    else:
        # Local MongoDB connection
        client = MongoClient(MONGO_URL)
    
    # Test connection
    client.admin.command('ping')
    print(f"✅ MongoDB connected successfully to: {MONGO_URL}")
    
    # Use environment variable for database name
    db = client[DB_NAME]
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print(f"MONGO_URL: {MONGO_URL}")
    print(f"DB_NAME: {DB_NAME}")
    # Re-raise to prevent app from starting with broken DB
    raise

# Collections
users_collection = db.users
matches_collection = db.matches
messages_collection = db.messages
swipes_collection = db.swipes
profile_images_collection = db.profile_images
trading_highlights_collection = db.trading_highlights
social_links_collection = db.social_links
token_launch_profiles_collection = db.token_launch_profiles
referrals_collection = db.referrals
subscriptions_collection = db.subscriptions
swipe_history_collection = db.swipe_history
likes_received_collection = db.likes_received
portfolio_connections_collection = db.portfolio_connections
trading_signals_collection = db.trading_signals
trading_groups_collection = db.trading_groups
trading_calendar_collection = db.trading_calendar
analytics_collection = db.analytics

# Authentication utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user_profile(user_data: dict) -> dict:
    """Create a standardized user profile"""
    return {
        "user_id": str(uuid.uuid4()),
        "email": user_data.get("email", ""),
        "wallet_address": user_data.get("wallet_address", ""),
        "twitter_id": user_data.get("twitter_id", ""),
        "username": user_data.get("username", ""),
        "display_name": user_data.get("display_name", ""),
        "avatar_url": user_data.get("avatar_url", "https://images.pexels.com/photos/31610834/pexels-photo-31610834.jpeg"),
        "bio": user_data.get("bio", ""),
        "location": user_data.get("location", ""),
        "timezone": user_data.get("timezone", ""),
        "user_status": "active",
        "last_activity": datetime.utcnow(),
        "show_twitter": user_data.get("show_twitter", False),
        "twitter_username": user_data.get("twitter_username", ""),
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
        "interested_in_token_launch": False,
        "token_launch_experience": "",
        "launch_timeline": "",
        "launch_budget": "",
        "profile_complete": False,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow(),
        "auth_method": user_data.get("auth_method", "email"),  # "email", "wallet", "twitter", "demo"
        "subscription_plan": "free"  # Default to free tier
    }

# FastAPI app
app = FastAPI(title="Solm8 API", version="1.0.0")

# Production-ready CORS middleware
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # More restrictive CORS for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    # More permissive CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Global exception handlers for production
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors gracefully"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "message": "The request data is invalid"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions gracefully"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    print(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
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
    timezone: str = ""  # User's timezone (e.g., "America/New_York", "UTC")
    # Status tracking
    user_status: str = "offline"  # "active", "offline"
    last_activity: datetime
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
    # Token launch interest
    interested_in_token_launch: bool = False
    token_launch_experience: str = ""  # "None", "Beginner", "Experienced", "Expert"
    launch_timeline: str = ""  # "Immediate", "1-3 months", "3-6 months", "6+ months", "Just researching"
    launch_budget: str = ""  # "Under $10K", "$10K-$50K", "$50K-$100K", "$100K+", "Prefer not to say"
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

class UserStatusUpdate(BaseModel):
    user_status: str  # "active" or "offline"

class TokenLaunchProfile(BaseModel):
    user_id: str
    interested_in_token_launch: bool
    token_launch_experience: str = ""  # "None", "Beginner", "Experienced", "Expert"
    launch_timeline: str = ""  # "Immediate", "1-3 months", "3-6 months", "6+ months", "Just researching"
    launch_budget: str = ""  # "Under $10K", "$10K-$50K", "$50K-$100K", "$100K+", "Prefer not to say"
    project_type: str = ""  # "Meme Coin", "Utility Token", "DeFi Protocol", "GameFi", "NFT Project", "Other"
    looking_for_help_with: List[str] = []  # ["Technical Development", "Marketing", "Community Building", "Funding", "Legal/Compliance"]

class ReferralCode(BaseModel):
    user_id: str

class ReferralStats(BaseModel):
    user_id: str

# Premium Subscription Models
class SubscriptionPlan(BaseModel):
    user_id: str
    plan_type: str  # "free", "basic_premium", "pro_trader"
    status: str  # "active", "cancelled", "expired"
    expires_at: Optional[datetime] = None

class SwipeLimit(BaseModel):
    user_id: str
    daily_swipes_used: int = 0
    last_reset_date: str

class LikesReceived(BaseModel):
    user_id: str
    liked_by_user_id: str
    liked_at: datetime

# TIER 2: Pro Trader Models
class PortfolioConnection(BaseModel):
    user_id: str
    wallet_address: str
    exchange_name: Optional[str] = ""  # "Binance", "Coinbase", "Phantom", etc.
    verified: bool = False
    portfolio_value: Optional[float] = 0.0
    last_sync: Optional[datetime] = None

class TradingSignal(BaseModel):
    signal_id: str
    sender_id: str
    recipient_ids: List[str]  # Can send to multiple users
    signal_type: str  # "entry", "exit", "alert", "analysis"
    token_symbol: str
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    risk_level: str  # "low", "medium", "high"
    message: str
    encrypted: bool = True
    expires_at: Optional[datetime] = None

class TradingGroup(BaseModel):
    group_id: str
    creator_id: str
    name: str
    description: str
    member_ids: List[str]
    max_members: int = 10
    is_private: bool = False
    created_at: datetime

class TradingEvent(BaseModel):
    event_id: str
    creator_id: str
    title: str
    description: str
    event_type: str  # "trading_session", "market_analysis", "strategy_call"
    start_time: datetime
    duration_minutes: int
    attendee_ids: List[str]
    max_attendees: int = 10

class UserAnalytics(BaseModel):
    user_id: str
    profile_views: int = 0
    matches_made: int = 0
    messages_sent: int = 0
    signals_sent: int = 0
    groups_created: int = 0
    match_success_rate: float = 0.0
    last_updated: datetime

# Premium utility functions
def get_user_subscription(user_id: str) -> dict:
    """Get user's current subscription status"""
    subscription = subscriptions_collection.find_one({"user_id": user_id})
    if not subscription:
        # Create free tier entry if doesn't exist
        free_sub = {
            "user_id": user_id,
            "plan_type": "free",
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": None
        }
        subscriptions_collection.insert_one(free_sub)
        return free_sub
    
    # Check if premium subscription is expired
    if subscription.get("expires_at") and subscription["expires_at"] < datetime.utcnow():
        # Downgrade to free
        subscriptions_collection.update_one(
            {"user_id": user_id},
            {"$set": {"plan_type": "free", "status": "expired"}}
        )
        subscription["plan_type"] = "free"
        subscription["status"] = "expired"
    
    return subscription

def check_swipe_limit(user_id: str) -> dict:
    """Check if user has reached daily swipe limit"""
    subscription = get_user_subscription(user_id)
    
    # Premium users have unlimited swipes
    if subscription["plan_type"] != "free":
        return {"can_swipe": True, "swipes_remaining": "unlimited", "is_premium": True}
    
    # Check daily swipe count for free users
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_swipes = swipes_collection.count_documents({
        "swiper_id": user_id,
        "swiped_at": {
            "$gte": datetime.strptime(today, "%Y-%m-%d"),
            "$lt": datetime.strptime(today, "%Y-%m-%d") + timedelta(days=1)
        }
    })
    
    daily_limit = 20  # Free tier limit
    swipes_remaining = max(0, daily_limit - today_swipes)
    
    return {
        "can_swipe": swipes_remaining > 0,
        "swipes_remaining": swipes_remaining,
        "swipes_used": today_swipes,
        "daily_limit": daily_limit,
        "is_premium": False
    }

def can_see_likes(user_id: str) -> bool:
    """Check if user can see who liked them"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] != "free"

def can_rewind_swipe(user_id: str) -> bool:
    """Check if user can rewind last swipe"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] != "free"

def get_priority_boost(user_id: str) -> bool:
    """Check if user gets priority in discovery"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] != "free"

def can_send_trading_signals(user_id: str) -> bool:
    """Check if user can send trading signals (Pro Trader feature)"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] == "pro_trader"

def can_create_groups(user_id: str) -> bool:
    """Check if user can create trading groups (Pro Trader feature)"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] == "pro_trader"

def can_schedule_events(user_id: str) -> bool:
    """Check if user can schedule trading events (Pro Trader feature)"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] == "pro_trader"

def can_view_analytics(user_id: str) -> bool:
    """Check if user can view performance analytics (Pro Trader feature)"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] == "pro_trader"

def can_connect_portfolio(user_id: str) -> bool:
    """Check if user can connect portfolio (Pro Trader feature)"""
    subscription = get_user_subscription(user_id)
    return subscription["plan_type"] == "pro_trader"

def update_user_analytics(user_id: str, action_type: str):
    """Update user analytics for Pro Trader features"""
    try:
        current_analytics = analytics_collection.find_one({"user_id": user_id})
        
        if not current_analytics:
            # Create new analytics entry
            analytics_data = {
                "user_id": user_id,
                "profile_views": 0,
                "matches_made": 0,
                "messages_sent": 0,
                "signals_sent": 0,
                "groups_created": 0,
                "match_success_rate": 0.0,
                "last_updated": datetime.utcnow()
            }
            analytics_collection.insert_one(analytics_data)
            current_analytics = analytics_data
        
        # Update based on action type
        update_data = {"last_updated": datetime.utcnow()}
        
        if action_type == "profile_view":
            update_data["profile_views"] = current_analytics.get("profile_views", 0) + 1
        elif action_type == "match_made":
            update_data["matches_made"] = current_analytics.get("matches_made", 0) + 1
        elif action_type == "message_sent":
            update_data["messages_sent"] = current_analytics.get("messages_sent", 0) + 1
        elif action_type == "signal_sent":
            update_data["signals_sent"] = current_analytics.get("signals_sent", 0) + 1
        elif action_type == "group_created":
            update_data["groups_created"] = current_analytics.get("groups_created", 0) + 1
        
        # Calculate match success rate
        swipes_made = swipes_collection.count_documents({"swiper_id": user_id, "action": "like"})
        matches_made = current_analytics.get("matches_made", 0)
        if swipes_made > 0:
            update_data["match_success_rate"] = round((matches_made / swipes_made) * 100, 2)
        
        analytics_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
    except Exception as e:
        print(f"Error updating analytics: {e}")

# Referral utility functions
def generate_referral_code(user_id: str) -> str:
    """Generate a unique referral code for a user"""
    # Create a unique code based on user ID and random string
    import hashlib
    import time
    
    # Get user data to create a more personalized code
    user = users_collection.find_one({"user_id": user_id})
    if user:
        username = user.get('username', '')
        # Create code: first 3 letters of username + 4 random chars
        if len(username) >= 3:
            prefix = username[:3].upper()
        else:
            prefix = 'SOL'
        
        # Add timestamp-based suffix to ensure uniqueness
        timestamp = str(int(time.time()))[-4:]
        referral_code = f"{prefix}{timestamp}"
        
        # Ensure it's unique
        while referrals_collection.find_one({"referral_code": referral_code}):
            timestamp = str(int(time.time() * 1000))[-4:]
            referral_code = f"{prefix}{timestamp}"
        
        return referral_code
    else:
        # Fallback random code
        return f"SOL{secrets.token_hex(4)[:6].upper()}"

def create_referral_entry(user_id: str, referral_code: str) -> dict:
    """Create a referral entry in the database"""
    referral_data = {
        "referral_id": str(uuid.uuid4()),
        "referrer_user_id": user_id,
        "referral_code": referral_code,
        "referred_user_id": None,
        "created_at": datetime.utcnow(),
        "used_at": None,
        "status": "pending",  # "pending", "completed"
        "bonus_awarded": False
    }
    
    referrals_collection.insert_one(referral_data)
    return referral_data

def process_referral_signup(referred_user_id: str, referral_code: str) -> bool:
    """Process a referral when someone signs up with a referral code"""
    try:
        # Find the referral entry
        referral = referrals_collection.find_one({
            "referral_code": referral_code,
            "status": "pending"
        })
        
        if not referral:
            return False
        
        # Update the referral with the new user
        referrals_collection.update_one(
            {"referral_id": referral["referral_id"]},
            {
                "$set": {
                    "referred_user_id": referred_user_id,
                    "used_at": datetime.utcnow(),
                    "status": "completed"
                }
            }
        )
        
        # You could add bonus logic here (e.g., reward points, premium features, etc.)
        # award_referral_bonus(referral["referrer_user_id"], referred_user_id)
        
        return True
    except Exception as e:
        print(f"Error processing referral: {e}")
        return False

# New Authentication Models
class EmailSignup(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    referral_code: Optional[str] = None

class EmailLogin(BaseModel):
    email: EmailStr
    password: str

class WalletAuth(BaseModel):
    wallet_address: str
    signature: str
    message: str

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

# Authentication Endpoints

@app.post("/api/auth/email/signup")
async def email_signup(signup_data: EmailSignup):
    """Sign up with email and password"""
    try:
        # Check if email already exists
        existing_user = users_collection.find_one({"email": signup_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate referral code if provided
        referral_valid = False
        if signup_data.referral_code:
            referral = referrals_collection.find_one({
                "referral_code": signup_data.referral_code,
                "status": "pending"
            })
            if referral:
                referral_valid = True
            else:
                raise HTTPException(status_code=400, detail="Invalid referral code")
        
        # Hash password
        hashed_password = hash_password(signup_data.password)
        
        # Create user profile
        user_data = create_user_profile({
            "email": signup_data.email,
            "display_name": signup_data.display_name,
            "username": f"trader_{secrets.token_hex(4)}",
            "auth_method": "email"
        })
        
        # Add password hash (not stored in main profile for security)
        user_data["password_hash"] = hashed_password
        
        # Insert user
        users_collection.insert_one(user_data)
        
        # Process referral if valid
        if referral_valid and signup_data.referral_code:
            process_referral_signup(user_data["user_id"], signup_data.referral_code)
        
        # Remove sensitive data before returning
        user_data.pop('_id', None)
        user_data.pop('password_hash', None)
        
        response_data = {"message": "Account created successfully", "user": user_data}
        if referral_valid:
            response_data["referral_applied"] = True
            response_data["message"] = "Account created successfully with referral bonus!"
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")

@app.post("/api/auth/email/login")
async def email_login(login_data: EmailLogin):
    """Login with email and password"""
    try:
        # Find user by email
        user = users_collection.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last activity
        users_collection.update_one(
            {"email": login_data.email},
            {"$set": {"last_active": datetime.utcnow(), "user_status": "active"}}
        )
        
        # Remove sensitive data before returning
        user.pop('_id', None)
        user.pop('password_hash', None)
        
        return {"message": "Login successful", "user": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/auth/wallet/connect")
async def wallet_connect(wallet_data: WalletAuth):
    """Connect with Solana wallet"""
    try:
        # For this demo, we'll do basic wallet address validation
        # In production, you'd verify the signature against the message
        if not wallet_data.wallet_address or len(wallet_data.wallet_address) < 32:
            raise HTTPException(status_code=400, detail="Invalid wallet address")
        
        # Check if wallet already exists
        existing_user = users_collection.find_one({"wallet_address": wallet_data.wallet_address})
        
        if existing_user:
            # Update last activity
            users_collection.update_one(
                {"wallet_address": wallet_data.wallet_address},
                {"$set": {"last_active": datetime.utcnow(), "user_status": "active"}}
            )
            
            existing_user.pop('_id', None)
            existing_user.pop('password_hash', None)
            return {"message": "Wallet connected successfully", "user": existing_user}
        else:
            # Create new user profile
            user_data = create_user_profile({
                "wallet_address": wallet_data.wallet_address,
                "display_name": f"Trader {wallet_data.wallet_address[:8]}...",
                "username": f"wallet_{secrets.token_hex(4)}",
                "auth_method": "wallet"
            })
            
            # Insert user
            users_collection.insert_one(user_data)
            
            # Remove sensitive data before returning
            user_data.pop('_id', None)
            
            return {"message": "New wallet account created", "user": user_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wallet connection failed: {str(e)}")

@app.get("/api/auth/wallet/message")
async def get_wallet_message():
    """Get message for wallet signature verification"""
    timestamp = int(datetime.utcnow().timestamp())
    message = f"Sign this message to authenticate with Solm8: {timestamp}"
    return {"message": message, "timestamp": timestamp}

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
        "timezone": user.get("timezone", ""),
        "user_status": user.get("user_status", "offline"),
        "last_activity": user.get("last_activity"),
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
        "interested_in_token_launch": user.get("interested_in_token_launch", False),
        "token_launch_experience": user.get("token_launch_experience", ""),
        "launch_timeline": user.get("launch_timeline", ""),
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

# User Status Management Endpoints

@app.post("/api/user-status/{user_id}")
async def update_user_status(user_id: str, status_update: UserStatusUpdate):
    """Update user's online/offline status"""
    try:
        # Validate user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate status value
        if status_update.user_status not in ["active", "offline"]:
            raise HTTPException(status_code=400, detail="Status must be 'active' or 'offline'")
        
        # Update user status and last activity
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_status": status_update.user_status,
                    "last_activity": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Status updated successfully", "status": status_update.user_status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@app.get("/api/user-status/{user_id}")
async def get_user_status(user_id: str):
    """Get user's current status"""
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Auto-update status if user has been inactive for more than 30 minutes
    last_activity = user.get('last_activity', datetime.utcnow())
    if isinstance(last_activity, str):
        last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
    
    inactive_threshold = datetime.utcnow() - timedelta(minutes=30)
    
    if last_activity < inactive_threshold and user.get('user_status') == 'active':
        # Auto-switch to offline
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"user_status": "offline"}}
        )
        user['user_status'] = 'offline'
    
    return {
        "user_id": user_id,
        "user_status": user.get('user_status', 'offline'),
        "last_activity": user.get('last_activity'),
        "display_name": user.get('display_name', ''),
        "timezone": user.get('timezone', '')
    }

@app.get("/api/users/active")
async def get_active_users():
    """Get list of currently active users"""
    try:
        # Get all users who are marked as active
        active_users = list(users_collection.find({"user_status": "active"}))
        
        # Filter out users who have been inactive for more than 30 minutes
        inactive_threshold = datetime.utcnow() - timedelta(minutes=30)
        truly_active_users = []
        users_to_update = []
        
        for user in active_users:
            last_activity = user.get('last_activity', datetime.utcnow())
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            
            if last_activity >= inactive_threshold:
                # Remove sensitive data and MongoDB ObjectId
                user.pop('_id', None)
                user.pop('twitter_id', None)
                truly_active_users.append({
                    "user_id": user['user_id'],
                    "username": user['username'],
                    "display_name": user['display_name'],
                    "avatar_url": user['avatar_url'],
                    "bio": user.get('bio', ''),
                    "location": user.get('location', ''),
                    "timezone": user.get('timezone', ''),
                    "trading_experience": user.get('trading_experience', ''),
                    "trading_style": user.get('trading_style', ''),
                    "preferred_tokens": user.get('preferred_tokens', []),
                    "looking_for": user.get('looking_for', []),
                    "interested_in_token_launch": user.get('interested_in_token_launch', False),
                    "last_activity": user.get('last_activity')
                })
            else:
                # Mark for status update
                users_to_update.append(user['user_id'])
        
        # Bulk update inactive users to offline status
        if users_to_update:
            users_collection.update_many(
                {"user_id": {"$in": users_to_update}},
                {"$set": {"user_status": "offline"}}
            )
        
        return {
            "active_users": truly_active_users,
            "count": len(truly_active_users),
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active users: {str(e)}")

@app.post("/api/user/{user_id}/update-activity")
async def update_user_activity(user_id: str):
    """Update user's last activity timestamp (called on app usage)"""
    try:
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Activity updated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update activity: {str(e)}")

# Token Launch Management Endpoints

@app.post("/api/token-launch-profile/{user_id}")
async def update_token_launch_profile(user_id: str, token_profile: TokenLaunchProfile):
    """Update user's token launch interests and profile"""
    try:
        # Validate user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user's token launch fields in main profile
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "interested_in_token_launch": token_profile.interested_in_token_launch,
                    "token_launch_experience": token_profile.token_launch_experience,
                    "launch_timeline": token_profile.launch_timeline,
                    "launch_budget": token_profile.launch_budget,
                    "last_activity": datetime.utcnow()
                }
            }
        )
        
        # Create or update detailed token launch profile
        token_launch_data = {
            "user_id": user_id,
            "interested_in_token_launch": token_profile.interested_in_token_launch,
            "token_launch_experience": token_profile.token_launch_experience,
            "launch_timeline": token_profile.launch_timeline,
            "launch_budget": token_profile.launch_budget,
            "project_type": token_profile.project_type,
            "looking_for_help_with": token_profile.looking_for_help_with,
            "updated_at": datetime.utcnow()
        }
        
        # Upsert token launch profile
        token_launch_profiles_collection.replace_one(
            {"user_id": user_id},
            token_launch_data,
            upsert=True
        )
        
        return {"message": "Token launch profile updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update token launch profile: {str(e)}")

@app.get("/api/token-launch-profile/{user_id}")
async def get_token_launch_profile(user_id: str):
    """Get user's token launch profile"""
    token_profile = token_launch_profiles_collection.find_one({"user_id": user_id})
    if token_profile:
        token_profile.pop('_id', None)
        return token_profile
    
    # Return basic info from user profile if detailed profile doesn't exist
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return {
            "user_id": user_id,
            "interested_in_token_launch": user.get('interested_in_token_launch', False),
            "token_launch_experience": user.get('token_launch_experience', ''),
            "launch_timeline": user.get('launch_timeline', ''),
            "launch_budget": user.get('launch_budget', ''),
            "project_type": '',
            "looking_for_help_with": []
        }
    
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/users/token-launchers")
async def get_token_launchers():
    """Get users interested in token launches"""
    try:
        # Get users who are interested in token launches
        token_launchers = list(users_collection.find({
            "interested_in_token_launch": True,
            "profile_complete": True
        }))
        
        result_users = []
        for user in token_launchers:
            # Remove sensitive data
            user.pop('_id', None)
            user.pop('twitter_id', None)
            
            # Get detailed token launch profile if exists
            token_profile = token_launch_profiles_collection.find_one({"user_id": user['user_id']})
            
            user_data = {
                "user_id": user['user_id'],
                "username": user['username'],
                "display_name": user['display_name'],
                "avatar_url": user['avatar_url'],
                "bio": user.get('bio', ''),
                "location": user.get('location', ''),
                "timezone": user.get('timezone', ''),
                "user_status": user.get('user_status', 'offline'),
                "trading_experience": user.get('trading_experience', ''),
                "years_trading": user.get('years_trading', 0),
                "token_launch_experience": user.get('token_launch_experience', ''),
                "launch_timeline": user.get('launch_timeline', ''),
                "launch_budget": user.get('launch_budget', ''),
                "last_activity": user.get('last_activity')
            }
            
            # Add detailed token launch info if available
            if token_profile:
                user_data.update({
                    "project_type": token_profile.get('project_type', ''),
                    "looking_for_help_with": token_profile.get('looking_for_help_with', [])
                })
            
            result_users.append(user_data)
        
        return {
            "token_launchers": result_users,
            "count": len(result_users)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token launchers: {str(e)}")

# Referral System Endpoints

@app.post("/api/referrals/generate/{user_id}")
async def generate_user_referral_code(user_id: str):
    """Generate a referral code for a user"""
    try:
        # Check if user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user already has an active referral code
        existing_referral = referrals_collection.find_one({
            "referrer_user_id": user_id,
            "status": "pending"
        })
        
        if existing_referral:
            return {
                "referral_code": existing_referral["referral_code"],
                "created_at": existing_referral["created_at"],
                "message": "Existing referral code returned"
            }
        
        # Generate new referral code
        referral_code = generate_referral_code(user_id)
        referral_data = create_referral_entry(user_id, referral_code)
        
        # Remove MongoDB _id
        referral_data.pop('_id', None)
        
        return {
            "referral_code": referral_code,
            "created_at": referral_data["created_at"],
            "message": "New referral code generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate referral code: {str(e)}")

@app.get("/api/referrals/stats/{user_id}")
async def get_referral_stats(user_id: str):
    """Get referral statistics for a user"""
    try:
        # Check if user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's referral code
        user_referral = referrals_collection.find_one({
            "referrer_user_id": user_id,
            "status": "pending"
        })
        
        # Get completed referrals (people who signed up using their code)
        completed_referrals = list(referrals_collection.find({
            "referrer_user_id": user_id,
            "status": "completed"
        }))
        
        # Get details of referred users
        referred_users = []
        for referral in completed_referrals:
            if referral.get("referred_user_id"):
                referred_user = users_collection.find_one({"user_id": referral["referred_user_id"]})
                if referred_user:
                    referred_users.append({
                        "user_id": referred_user["user_id"],
                        "username": referred_user["username"],
                        "display_name": referred_user["display_name"],
                        "avatar_url": referred_user["avatar_url"],
                        "joined_at": referral["used_at"],
                        "profile_complete": referred_user.get("profile_complete", False)
                    })
        
        return {
            "referral_code": user_referral["referral_code"] if user_referral else None,
            "total_referrals": len(completed_referrals),
            "successful_signups": len([r for r in referred_users if r["profile_complete"]]),
            "pending_signups": len([r for r in referred_users if not r["profile_complete"]]),
            "referred_users": referred_users,
            "referral_link": f"https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/?ref={user_referral['referral_code']}" if user_referral else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get referral stats: {str(e)}")

@app.get("/api/referrals/validate/{referral_code}")
async def validate_referral_code(referral_code: str):
    """Validate a referral code"""
    try:
        referral = referrals_collection.find_one({
            "referral_code": referral_code,
            "status": "pending"
        })
        
        if not referral:
            return {"valid": False, "message": "Invalid or expired referral code"}
        
        # Get referrer user info
        referrer = users_collection.find_one({"user_id": referral["referrer_user_id"]})
        if not referrer:
            return {"valid": False, "message": "Referrer user not found"}
        
        return {
            "valid": True,
            "referrer": {
                "display_name": referrer["display_name"],
                "username": referrer["username"],
                "avatar_url": referrer["avatar_url"]
            },
            "message": f"Valid referral code from {referrer['display_name']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate referral code: {str(e)}")

@app.post("/api/auth/change-password")
async def change_password(request_data: dict):
    """Change user password"""
    try:
        user_id = request_data.get("user_id")
        current_password = request_data.get("current_password")
        new_password = request_data.get("new_password")
        
        if not all([user_id, current_password, new_password]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Find user
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not verify_password(current_password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
        
        # Hash new password
        new_password_hash = hash_password(new_password)
        
        # Update password
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"password_hash": new_password_hash, "last_activity": datetime.utcnow()}}
        )
        
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Enhanced health check for production deployment"""
    try:
        # Test database connectivity
        client.admin.command('ping')
        db_status = "healthy"
        
        # Get database info
        db_info = {
            "name": DB_NAME,
            "connected": True,
            "collections": len(db.list_collection_names())
        }
        
    except Exception as e:
        db_status = "unhealthy"
        db_info = {
            "name": DB_NAME,
            "connected": False,
            "error": str(e)
        }
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "Solm8 API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "database": db_info,
        "timestamp": datetime.utcnow().isoformat()
    }

# Premium Subscription Endpoints

@app.get("/api/subscription/{user_id}")
async def get_subscription_status(user_id: str):
    """Get user's subscription status and limits"""
    subscription = get_user_subscription(user_id)
    swipe_status = check_swipe_limit(user_id)
    
    # Define features by plan type
    premium_features = {
        "unlimited_swipes": subscription["plan_type"] != "free",
        "see_who_liked_you": can_see_likes(user_id),
        "rewind_swipes": can_rewind_swipe(user_id),
        "priority_discovery": get_priority_boost(user_id),
        "advanced_filters": subscription["plan_type"] != "free"
    }
    
    # Pro Trader specific features
    pro_trader_features = {
        "portfolio_integration": can_connect_portfolio(user_id),
        "trading_signals": can_send_trading_signals(user_id),
        "group_chats": can_create_groups(user_id),
        "trading_calendar": can_schedule_events(user_id),
        "performance_analytics": can_view_analytics(user_id)
    }
    
    return {
        "subscription": subscription,
        "swipe_limits": swipe_status,
        "premium_features": premium_features,
        "pro_trader_features": pro_trader_features,
        "plan_info": {
            "current_plan": subscription["plan_type"],
            "is_free": subscription["plan_type"] == "free",
            "is_basic_premium": subscription["plan_type"] == "basic_premium",
            "is_pro_trader": subscription["plan_type"] == "pro_trader"
        }
    }

@app.post("/api/subscription/upgrade/{user_id}")
async def upgrade_subscription(user_id: str, plan_data: dict):
    """Upgrade user to premium subscription"""
    try:
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For demo, we'll just upgrade them directly
        # In production, integrate with payment processor like Stripe
        plan_type = plan_data.get("plan_type", "basic_premium")
        
        subscription_data = {
            "user_id": user_id,
            "plan_type": plan_type,
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30),  # 30-day subscription
            "payment_method": "demo",
            "amount": 9.99 if plan_type == "basic_premium" else 0
        }
        
        # Upsert subscription
        subscriptions_collection.replace_one(
            {"user_id": user_id},
            subscription_data,
            upsert=True
        )
        
        return {
            "message": "Successfully upgraded to Premium!",
            "subscription": subscription_data,
            "features_unlocked": [
                "Unlimited swipes",
                "See who liked you",
                "Rewind last swipe",
                "Advanced filters",
                "Priority in discovery"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")

@app.get("/api/likes-received/{user_id}")
async def get_likes_received(user_id: str):
    """Get users who liked this user (Premium feature)"""
    if not can_see_likes(user_id):
        # Return teaser for free users
        like_count = likes_received_collection.count_documents({"user_id": user_id})
        return {
            "premium_required": True,
            "like_count": like_count,
            "message": f"You have {like_count} likes! Upgrade to Premium to see who liked you.",
            "upgrade_url": "/premium"
        }
    
    # Get actual likes for premium users
    likes = list(likes_received_collection.find({"user_id": user_id}).sort("liked_at", -1))
    
    # Get user details for each like
    liked_users = []
    for like in likes:
        liked_user = users_collection.find_one({"user_id": like["liked_by_user_id"]})
        if liked_user:
            liked_user.pop('_id', None)
            liked_users.append({
                "user_id": liked_user["user_id"],
                "username": liked_user["username"],
                "display_name": liked_user["display_name"],
                "avatar_url": liked_user["avatar_url"],
                "bio": liked_user.get("bio", ""),
                "trading_experience": liked_user.get("trading_experience", ""),
                "preferred_tokens": liked_user.get("preferred_tokens", []),
                "liked_at": like["liked_at"]
            })
    
    return {
        "premium_required": False,
        "liked_users": liked_users,
        "total_likes": len(liked_users)
    }

@app.post("/api/rewind-swipe/{user_id}")
async def rewind_last_swipe(user_id: str):
    """Rewind the last swipe (Premium feature)"""
    if not can_rewind_swipe(user_id):
        return {
            "premium_required": True,
            "message": "Rewind is a Premium feature. Upgrade to undo your last swipe!",
            "upgrade_url": "/premium"
        }
    
    # Get last swipe
    last_swipe_history = swipe_history_collection.find_one(
        {"user_id": user_id},
        sort=[("_id", -1)]
    )
    
    if not last_swipe_history:
        return {"error": "No swipes to rewind"}
    
    last_swipe = last_swipe_history["swipe_data"]
    
    # Remove the swipe from swipes collection
    swipes_collection.delete_one({"swipe_id": last_swipe["swipe_id"]})
    
    # Remove from likes_received if it was a like
    if last_swipe["action"] == "like":
        likes_received_collection.delete_one({
            "user_id": last_swipe["target_id"],
            "liked_by_user_id": last_swipe["swiper_id"]
        })
    
    # Remove from swipe history
    swipe_history_collection.delete_one({"_id": last_swipe_history["_id"]})
    
    # Get the target user info to return
    target_user = users_collection.find_one({"user_id": last_swipe["target_id"]})
    if target_user:
        target_user.pop('_id', None)
    
    return {
        "success": True,
        "message": "Last swipe rewound successfully!",
        "rewound_user": target_user,
        "action_rewound": last_swipe["action"]
    }

@app.get("/api/discover/{user_id}")
async def discover_users(user_id: str, limit: int = 10, filters: dict = None):
    """Get potential matches for swiping with premium filters"""
    current_user = users_collection.find_one({"user_id": user_id})
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription = get_user_subscription(user_id)
    
    # Get users already swiped on
    swiped_user_ids = [doc["target_id"] for doc in swipes_collection.find({"swiper_id": user_id})]
    swiped_user_ids.append(user_id)  # Exclude self
    
    # Base query
    query = {
        "user_id": {"$nin": swiped_user_ids},
        "profile_complete": True
    }
    
    # Apply premium filters if available
    if subscription["plan_type"] != "free" and filters:
        if filters.get("portfolio_size"):
            query["portfolio_size"] = filters["portfolio_size"]
        if filters.get("trading_experience"):
            query["trading_experience"] = filters["trading_experience"]
        if filters.get("preferred_tokens"):
            query["preferred_tokens"] = {"$in": filters["preferred_tokens"]}
        if filters.get("years_trading_min"):
            query["years_trading"] = {"$gte": filters["years_trading_min"]}
        if filters.get("location"):
            query["location"] = {"$regex": filters["location"], "$options": "i"}
    
    # Premium users get priority (more recent activity first)
    # Free users get standard sorting
    sort_criteria = "last_activity" if subscription["plan_type"] != "free" else "created_at"
    
    potential_matches = list(users_collection.find(query).sort(sort_criteria, -1).limit(limit))
    
    # Remove MongoDB _id fields
    for user in potential_matches:
        user.pop('_id', None)
    
    # Track profile views for analytics (for the users being discovered)
    for user in potential_matches:
        update_user_analytics(user["user_id"], "profile_view")
    
    # Add premium indicator to response
    return {
        "users": potential_matches,
        "has_premium_filters": subscription["plan_type"] != "free",
        "applied_filters": filters if subscription["plan_type"] != "free" else None
    }

# TIER 2: Pro Trader Endpoints

@app.post("/api/portfolio/connect/{user_id}")
async def connect_portfolio(user_id: str, portfolio_data: dict):
    """Connect wallet/exchange for portfolio verification (Pro Trader feature)"""
    if not can_connect_portfolio(user_id):
        return {
            "pro_trader_required": True,
            "message": "Portfolio integration is a Pro Trader feature. Upgrade to connect your wallet/exchange!",
            "upgrade_url": "/premium"
        }
    
    try:
        wallet_address = portfolio_data.get("wallet_address", "")
        exchange_name = portfolio_data.get("exchange_name", "")
        
        if not wallet_address and not exchange_name:
            raise HTTPException(status_code=400, detail="Either wallet address or exchange name is required")
        
        # Create portfolio connection
        portfolio_connection = {
            "user_id": user_id,
            "wallet_address": wallet_address,
            "exchange_name": exchange_name,
            "verified": False,  # Would integrate with actual verification service
            "portfolio_value": 0.0,  # Would fetch from actual portfolio
            "last_sync": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        # Upsert portfolio connection
        portfolio_connections_collection.replace_one(
            {"user_id": user_id},
            portfolio_connection,
            upsert=True
        )
        
        # Update user profile with verified status
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"portfolio_verified": True, "last_active": datetime.utcnow()}}
        )
        
        return {
            "message": "Portfolio connected successfully!",
            "verified": False,  # Would be True after actual verification
            "next_steps": "Portfolio verification in progress. This may take a few minutes."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect portfolio: {str(e)}")

@app.get("/api/portfolio/{user_id}")
async def get_portfolio_info(user_id: str):
    """Get portfolio connection info"""
    portfolio = portfolio_connections_collection.find_one({"user_id": user_id})
    if portfolio:
        portfolio.pop('_id', None)
        return portfolio
    
    return {"connected": False, "message": "No portfolio connected"}

@app.post("/api/trading-signal/send")
async def send_trading_signal(signal_data: dict):
    """Send trading signal to matched users (Pro Trader feature)"""
    sender_id = signal_data.get("sender_id")
    
    if not can_send_trading_signals(sender_id):
        return {
            "pro_trader_required": True,
            "message": "Trading signals are a Pro Trader feature. Upgrade to share alpha with your network!",
            "upgrade_url": "/premium"
        }
    
    try:
        # Create trading signal
        signal = {
            "signal_id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "recipient_ids": signal_data.get("recipient_ids", []),
            "signal_type": signal_data.get("signal_type", "alert"),
            "token_symbol": signal_data.get("token_symbol", ""),
            "price_target": signal_data.get("price_target"),
            "stop_loss": signal_data.get("stop_loss"),
            "risk_level": signal_data.get("risk_level", "medium"),
            "message": signal_data.get("message", ""),
            "encrypted": True,
            "expires_at": datetime.utcnow() + timedelta(hours=24),
            "created_at": datetime.utcnow()
        }
        
        trading_signals_collection.insert_one(signal)
        
        # Update analytics
        update_user_analytics(sender_id, "signal_sent")
        
        # Notify recipients via WebSocket (if connected)
        for recipient_id in signal["recipient_ids"]:
            signal_notification = {
                "type": "trading_signal",
                "signal_id": signal["signal_id"],
                "sender_id": sender_id,
                "token_symbol": signal["token_symbol"],
                "message": f"New trading signal for {signal['token_symbol']}"
            }
            await manager.send_message(json.dumps(signal_notification), recipient_id)
        
        signal.pop('_id', None)
        return {
            "message": "Trading signal sent successfully!",
            "signal": signal,
            "recipients_notified": len(signal["recipient_ids"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send trading signal: {str(e)}")

@app.get("/api/trading-signals/{user_id}")
async def get_trading_signals(user_id: str, signal_type: str = "received"):
    """Get trading signals for user (sent or received)"""
    try:
        if signal_type == "sent":
            signals = list(trading_signals_collection.find({"sender_id": user_id}).sort("created_at", -1))
        else:
            signals = list(trading_signals_collection.find({"recipient_ids": user_id}).sort("created_at", -1))
        
        # Remove MongoDB _id and get sender info for received signals
        enriched_signals = []
        for signal in signals:
            signal.pop('_id', None)
            
            # Get sender info
            sender = users_collection.find_one({"user_id": signal["sender_id"]})
            if sender:
                signal["sender_info"] = {
                    "display_name": sender["display_name"],
                    "username": sender["username"],
                    "avatar_url": sender["avatar_url"]
                }
            
            enriched_signals.append(signal)
        
        return {
            "signals": enriched_signals,
            "count": len(enriched_signals),
            "type": signal_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trading signals: {str(e)}")

@app.post("/api/trading-group/create")
async def create_trading_group(group_data: dict):
    """Create trading group (Pro Trader feature)"""
    creator_id = group_data.get("creator_id")
    
    if not can_create_groups(creator_id):
        return {
            "pro_trader_required": True,
            "message": "Trading groups are a Pro Trader feature. Upgrade to create groups with your trading network!",
            "upgrade_url": "/premium"
        }
    
    try:
        # Check if user has reached group limit (5 groups for Pro Trader)
        user_groups = trading_groups_collection.count_documents({"creator_id": creator_id})
        if user_groups >= 5:
            return {
                "error": "group_limit_reached",
                "message": "You've reached the maximum of 5 trading groups. Delete a group to create a new one.",
                "current_groups": user_groups
            }
        
        # Create trading group
        group = {
            "group_id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "name": group_data.get("name", ""),
            "description": group_data.get("description", ""),
            "member_ids": [creator_id],  # Creator is automatically a member
            "max_members": 10,
            "is_private": group_data.get("is_private", False),
            "created_at": datetime.utcnow()
        }
        
        trading_groups_collection.insert_one(group)
        
        # Update analytics
        update_user_analytics(creator_id, "group_created")
        
        group.pop('_id', None)
        return {
            "message": "Trading group created successfully!",
            "group": group
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trading group: {str(e)}")

@app.post("/api/trading-group/{group_id}/join")
async def join_trading_group(group_id: str, user_data: dict):
    """Join a trading group"""
    user_id = user_data.get("user_id")
    
    try:
        group = trading_groups_collection.find_one({"group_id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Trading group not found")
        
        # Check if group is full
        if len(group["member_ids"]) >= group["max_members"]:
            return {
                "error": "group_full",
                "message": "This trading group is at maximum capacity",
                "max_members": group["max_members"]
            }
        
        # Check if user is already a member
        if user_id in group["member_ids"]:
            return {
                "error": "already_member",
                "message": "You are already a member of this group"
            }
        
        # Add user to group
        trading_groups_collection.update_one(
            {"group_id": group_id},
            {"$push": {"member_ids": user_id}}
        )
        
        # Notify group members
        for member_id in group["member_ids"]:
            if member_id != user_id:
                notification = {
                    "type": "group_member_joined",
                    "group_id": group_id,
                    "group_name": group["name"],
                    "new_member_id": user_id
                }
                await manager.send_message(json.dumps(notification), member_id)
        
        return {
            "message": f"Successfully joined {group['name']}!",
            "group_id": group_id,
            "member_count": len(group["member_ids"]) + 1
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join group: {str(e)}")

@app.get("/api/trading-groups/{user_id}")
async def get_user_trading_groups(user_id: str):
    """Get trading groups for user"""
    try:
        # Get groups where user is a member
        groups = list(trading_groups_collection.find({"member_ids": user_id}))
        
        enriched_groups = []
        for group in groups:
            group.pop('_id', None)
            
            # Get member info
            members = []
            for member_id in group["member_ids"]:
                member = users_collection.find_one({"user_id": member_id})
                if member:
                    members.append({
                        "user_id": member["user_id"],
                        "display_name": member["display_name"],
                        "username": member["username"],
                        "avatar_url": member["avatar_url"]
                    })
            
            group["members"] = members
            group["member_count"] = len(members)
            enriched_groups.append(group)
        
        return {
            "groups": enriched_groups,
            "count": len(enriched_groups)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trading groups: {str(e)}")

@app.post("/api/trading-event/schedule")
async def schedule_trading_event(event_data: dict):
    """Schedule trading event (Pro Trader feature)"""
    creator_id = event_data.get("creator_id")
    
    if not can_schedule_events(creator_id):
        return {
            "pro_trader_required": True,
            "message": "Trading calendar is a Pro Trader feature. Upgrade to schedule trading sessions!",
            "upgrade_url": "/premium"
        }
    
    try:
        # Create trading event
        event = {
            "event_id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "title": event_data.get("title", ""),
            "description": event_data.get("description", ""),
            "event_type": event_data.get("event_type", "trading_session"),
            "start_time": datetime.fromisoformat(event_data.get("start_time")),
            "duration_minutes": event_data.get("duration_minutes", 60),
            "attendee_ids": [creator_id],  # Creator is automatically an attendee
            "max_attendees": 10,
            "created_at": datetime.utcnow()
        }
        
        trading_calendar_collection.insert_one(event)
        
        event.pop('_id', None)
        return {
            "message": "Trading event scheduled successfully!",
            "event": event
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule event: {str(e)}")

@app.get("/api/trading-events/{user_id}")
async def get_trading_events(user_id: str):
    """Get trading events for user"""
    try:
        # Get events where user is creator or attendee
        events = list(trading_calendar_collection.find({
            "$or": [
                {"creator_id": user_id},
                {"attendee_ids": user_id}
            ]
        }).sort("start_time", 1))
        
        for event in events:
            event.pop('_id', None)
        
        return {
            "events": events,
            "count": len(events)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trading events: {str(e)}")

@app.get("/api/analytics/{user_id}")
async def get_user_analytics(user_id: str):
    """Get performance analytics (Pro Trader feature)"""
    if not can_view_analytics(user_id):
        return {
            "pro_trader_required": True,
            "message": "Performance analytics are a Pro Trader feature. Upgrade to track your trading network success!",
            "upgrade_url": "/premium"
        }
    
    try:
        analytics = analytics_collection.find_one({"user_id": user_id})
        if not analytics:
            # Create empty analytics
            analytics = {
                "user_id": user_id,
                "profile_views": 0,
                "matches_made": 0,
                "messages_sent": 0,
                "signals_sent": 0,
                "groups_created": 0,
                "match_success_rate": 0.0,
                "last_updated": datetime.utcnow()
            }
            analytics_collection.insert_one(analytics)
        
        analytics.pop('_id', None)
        
        # Add additional calculated metrics
        total_swipes = swipes_collection.count_documents({"swiper_id": user_id})
        total_likes_received = likes_received_collection.count_documents({"user_id": user_id})
        
        analytics["total_swipes"] = total_swipes
        analytics["likes_received"] = total_likes_received
        analytics["popularity_score"] = round((total_likes_received / max(total_swipes, 1)) * 100, 2)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.delete("/api/user/{user_id}")
async def delete_user_account(user_id: str):
    """Delete user account and all associated data"""
    try:
        # Verify user exists
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete all user-related data
        # 1. Delete user profile
        users_collection.delete_one({"user_id": user_id})
        
        # 2. Delete matches where user is involved
        matches_collection.delete_many({
            "$or": [
                {"user1_id": user_id},
                {"user2_id": user_id}
            ]
        })
        
        # 3. Delete messages sent by user
        messages_collection.delete_many({"sender_id": user_id})
        
        # 4. Delete swipes made by user
        swipes_collection.delete_many({"swiper_id": user_id})
        
        # 5. Delete likes received by user
        likes_received_collection.delete_many({"user_id": user_id})
        
        # 6. Delete likes made by user
        likes_received_collection.delete_many({"liked_by_user_id": user_id})
        
        # 7. Delete swipe history
        swipe_history_collection.delete_many({"user_id": user_id})
        
        # 8. Delete profile images
        profile_images_collection.delete_many({"user_id": user_id})
        
        # 9. Delete trading highlights
        trading_highlights_collection.delete_many({"user_id": user_id})
        
        # 10. Delete social links
        social_links_collection.delete_many({"user_id": user_id})
        
        # 11. Delete subscription
        subscriptions_collection.delete_many({"user_id": user_id})
        
        # 12. Delete portfolio connections
        portfolio_connections_collection.delete_many({"user_id": user_id})
        
        # 13. Delete trading signals (sent and received)
        trading_signals_collection.delete_many({
            "$or": [
                {"sender_id": user_id},
                {"recipient_ids": user_id}
            ]
        })
        
        # 14. Delete trading groups created by user
        trading_groups_collection.delete_many({"creator_id": user_id})
        
        # 15. Remove user from trading groups
        trading_groups_collection.update_many(
            {"member_ids": user_id},
            {"$pull": {"member_ids": user_id}}
        )
        
        # 16. Delete trading events created by user
        trading_calendar_collection.delete_many({"creator_id": user_id})
        
        # 17. Remove user from trading events
        trading_calendar_collection.update_many(
            {"attendee_ids": user_id},
            {"$pull": {"attendee_ids": user_id}}
        )
        
        # 18. Delete analytics
        analytics_collection.delete_many({"user_id": user_id})
        
        # 19. Delete referrals
        referrals_collection.delete_many({
            "$or": [
                {"referrer_id": user_id},
                {"referred_id": user_id}
            ]
        })
        
        return {
            "message": "Account deleted successfully",
            "deleted_user_id": user_id,
            "data_cleanup": "All associated data has been permanently removed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")

@app.post("/api/subscription/upgrade/{user_id}")
async def upgrade_subscription(user_id: str, plan_data: dict):
    """Upgrade user to premium subscription"""
    try:
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For demo, we'll just upgrade them directly
        # In production, integrate with payment processor like Stripe
        plan_type = plan_data.get("plan_type", "basic_premium")
        
        # Set pricing
        pricing = {
            "basic_premium": 9.99,
            "pro_trader": 19.99
        }
        
        subscription_data = {
            "user_id": user_id,
            "plan_type": plan_type,
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30),  # 30-day subscription
            "payment_method": "demo",
            "amount": pricing.get(plan_type, 0)
        }
        
        # Upsert subscription
        subscriptions_collection.replace_one(
            {"user_id": user_id},
            subscription_data,
            upsert=True
        )
        
        # Define features by plan
        features_unlocked = []
        if plan_type == "basic_premium":
            features_unlocked = [
                "Unlimited swipes",
                "See who liked you",
                "Rewind last swipe",
                "Advanced filters",
                "Priority in discovery"
            ]
        elif plan_type == "pro_trader":
            features_unlocked = [
                "All Basic Premium features",
                "Portfolio integration",
                "Trading signal sharing",
                "Group chats (up to 5 groups)",
                "Trading calendar",
                "Performance analytics"
            ]
        
        return {
            "message": f"Successfully upgraded to {plan_type.replace('_', ' ').title()}!",
            "subscription": subscription_data,
            "features_unlocked": features_unlocked
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")



@app.get("/api/login/twitter")
async def login_twitter(request: Request):
    """Initiate Twitter OAuth login"""
    try:
        # Use the exact external URL for callback
        callback_url = f"https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/api/auth/twitter/callback"
        return await oauth.twitter.authorize_redirect(request, callback_url)
    except Exception as e:
        print(f"Twitter OAuth error: {str(e)}")
        # For demo purposes, return a mock success for now
        mock_user_id = str(uuid.uuid4())
        frontend_url = f"https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/app?auth_success=true&user_id={mock_user_id}&demo=true"
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
            user_data = create_user_profile({
                "twitter_id": twitter_user['id_str'],
                "username": twitter_user['screen_name'],
                "display_name": twitter_user['name'],
                "avatar_url": twitter_user['profile_image_url_https'].replace('_normal', '_400x400'),
                "bio": twitter_user.get('description', ''),
                "show_twitter": True,
                "twitter_username": twitter_user['screen_name'],
                "auth_method": "twitter"
            })
            users_collection.insert_one(user_data)
        
        # Redirect to frontend with user data
        frontend_url = f"https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/app?auth_success=true&user_id={user_data['user_id']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        return RedirectResponse(url=f"https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/app?auth_error=true")

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
        new_avatar_url = f"{os.environ.get('REACT_APP_BACKEND_URL', 'https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com')}/api/profile-image/{image_data['image_id']}"
        
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
    
    # Find all potential matches with complete profiles, sorted by recent activity
    potential_matches = list(users_collection.find({
        "user_id": {"$nin": swiped_user_ids},
        "profile_complete": True
    }).sort("last_activity", -1))
    
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

@app.post("/api/swipe")
async def swipe_user(swipe: SwipeAction):
    """Record a swipe action and check for matches"""
    
    # Check swipe limits for free users
    swipe_status = check_swipe_limit(swipe.swiper_id)
    if not swipe_status["can_swipe"]:
        return {
            "error": "daily_limit_reached",
            "message": "You've reached your daily swipe limit. Upgrade to Premium for unlimited swipes!",
            "swipes_remaining": 0,
            "upgrade_required": True
        }
    
    # Record the swipe with timestamp
    swipe_data = {
        "swipe_id": str(uuid.uuid4()),
        "swiper_id": swipe.swiper_id,
        "target_id": swipe.target_id,
        "action": swipe.action,
        "swiped_at": datetime.utcnow(),
        "timestamp": datetime.utcnow()
    }
    swipes_collection.insert_one(swipe_data)
    
    # Store for rewind functionality (premium feature)
    swipe_history_collection.insert_one({
        "user_id": swipe.swiper_id,
        "swipe_data": swipe_data,
        "can_rewind": can_rewind_swipe(swipe.swiper_id)
    })
    
    # If it's a like, store in likes_received for premium "See Who Liked You" feature
    if swipe.action == "like":
        likes_received_collection.insert_one({
            "user_id": swipe.target_id,
            "liked_by_user_id": swipe.swiper_id,
            "liked_at": datetime.utcnow()
        })
        
        # Check for mutual match
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
            
            # Update analytics for both users
            update_user_analytics(swipe.swiper_id, "match_made")
            update_user_analytics(swipe.target_id, "match_made")
            
            # Notify both users via WebSocket if connected
            match_notification = {
                "type": "new_match",
                "match_id": match_data["match_id"],
                "message": "You have a new match!"
            }
            await manager.send_message(json.dumps(match_notification), swipe.swiper_id)
            await manager.send_message(json.dumps(match_notification), swipe.target_id)
            
            # Update swipe status after successful swipe
            updated_swipe_status = check_swipe_limit(swipe.swiper_id)
            
            return {
                "matched": True, 
                "match_id": match_data["match_id"],
                "swipes_remaining": updated_swipe_status["swipes_remaining"],
                "is_premium": updated_swipe_status["is_premium"]
            }
    
    # Update swipe status after successful swipe
    updated_swipe_status = check_swipe_limit(swipe.swiper_id)
    
    return {
        "matched": False,
        "swipes_remaining": updated_swipe_status["swipes_remaining"],
        "is_premium": updated_swipe_status["is_premium"]
    }

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

@app.get("/api/matches-with-messages/{user_id}")
async def get_matches_with_messages(user_id: str):
    """Get user's matches with latest message info and unread counts"""
    try:
        # Get user's matches
        matches = list(matches_collection.find({
            "$or": [{"user1_id": user_id}, {"user2_id": user_id}]
        }).sort("created_at", -1))
        
        result = []
        for match in matches:
            # Determine the other user
            other_user_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
            other_user = users_collection.find_one({"user_id": other_user_id})
            
            if not other_user:
                continue
                
            # Remove sensitive data from other_user
            other_user.pop('_id', None)
            other_user.pop('password_hash', None)
            
            # Get latest message for this match
            latest_message = messages_collection.find_one(
                {"match_id": match["match_id"]},
                sort=[("timestamp", -1)]
            )
            
            # Get unread message count based on actual read status
            read_status_collection = db.read_status
            read_status = read_status_collection.find_one({
                "user_id": user_id,
                "match_id": match["match_id"]
            })
            
            if read_status and read_status.get("last_read_at"):
                # Count messages from other user after last read time
                unread_count = messages_collection.count_documents({
                    "match_id": match["match_id"],
                    "sender_id": other_user_id,
                    "timestamp": {"$gt": read_status["last_read_at"]}
                })
            else:
                # If no read status exists, count all messages from other user
                unread_count = messages_collection.count_documents({
                    "match_id": match["match_id"],
                    "sender_id": other_user_id
                })
            
            match_data = {
                "match_id": match["match_id"],
                "user1_id": match["user1_id"],
                "user2_id": match["user2_id"],
                "created_at": match["created_at"],
                "last_message_at": match.get("last_message_at", match["created_at"]),
                "other_user": other_user,
                "latest_message": {
                    "content": latest_message.get("content", "") if latest_message else "",
                    "timestamp": latest_message.get("timestamp") if latest_message else None,
                    "sender_id": latest_message.get("sender_id") if latest_message else None
                },
                "unread_count": unread_count
            }
            result.append(match_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch matches: {str(e)}")

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

@app.post("/api/messages/{match_id}/mark-read")
async def mark_messages_read(match_id: str, user_data: dict):
    """Mark messages as read for a user in a match"""
    try:
        user_id = user_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        
        # Create or update a read_status collection to track when users last read messages
        read_status_collection = db.read_status
        
        read_status = {
            "user_id": user_id,
            "match_id": match_id,
            "last_read_at": datetime.utcnow()
        }
        
        # Upsert the read status
        read_status_collection.update_one(
            {"user_id": user_id, "match_id": match_id},
            {"$set": read_status},
            upsert=True
        )
        
        return {"message": "Messages marked as read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark messages as read: {str(e)}")

@app.post("/api/messages")
async def send_message(message_data: dict):
    """Send a message in a match"""
    try:
        # Validate required fields
        required_fields = ["match_id", "sender_id", "content"]
        for field in required_fields:
            if field not in message_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate match exists
        match = matches_collection.find_one({"match_id": message_data["match_id"]})
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate sender is part of the match
        if message_data["sender_id"] != match["user1_id"] and message_data["sender_id"] != match["user2_id"]:
            raise HTTPException(status_code=403, detail="Sender is not part of this match")
        
        # Create message
        msg = {
            "message_id": str(uuid.uuid4()),
            "match_id": message_data["match_id"],
            "sender_id": message_data["sender_id"],
            "content": message_data["content"],
            "timestamp": datetime.utcnow()
        }
        
        # Save message to database
        messages_collection.insert_one(msg)
        
        # Update analytics
        update_user_analytics(message_data["sender_id"], "message_sent")
        
        # Update match last message time
        matches_collection.update_one(
            {"match_id": message_data["match_id"]},
            {"$set": {"last_message_at": datetime.utcnow()}}
        )
        
        # Find the other user in the match
        other_user_id = match["user2_id"] if match["user1_id"] == message_data["sender_id"] else match["user1_id"]
        
        # Remove MongoDB _id field
        msg_response = msg.copy()
        msg_response.pop('_id', None)
        
        # Try to send real-time notification via WebSocket if user is connected
        try:
            await manager.send_message(json.dumps({
                "type": "chat_message",
                "message": msg_response
            }), other_user_id)
        except Exception as e:
            # WebSocket delivery failure shouldn't fail the API request
            print(f"WebSocket delivery failed: {str(e)}")
        
        return msg_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

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
    
    # Production server configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8001))
    WORKERS = int(os.environ.get('WORKERS', 1))
    
    # Production settings
    uvicorn.run(
        app, 
        host=HOST, 
        port=PORT,
        workers=WORKERS,
        log_level="info",
        access_log=ENVIRONMENT == "development"
    )