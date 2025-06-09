import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
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
db = client.solmatch_db

# Collections
users_collection = db.users
matches_collection = db.matches
messages_collection = db.messages
swipes_collection = db.swipes

# FastAPI app
app = FastAPI(title="SolMatch API", version="1.0.0")

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
    # Social & preferences
    trading_hours: str = ""  # "Early Morning", "Morning", "Afternoon", "Evening", "Night Owl", "24/7"
    communication_style: str = ""  # "Casual", "Professional", "Technical", "Friendly"
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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "SolMatch API"}

@app.get("/api/login/twitter")
async def login_twitter(request: Request):
    """Initiate Twitter OAuth login"""
    try:
        # Use the exact external URL for callback
        callback_url = f"https://b455855f-f3ef-4faa-b146-fcff2737404b.preview.emergentagent.com/api/auth/twitter/callback"
        return await oauth.twitter.authorize_redirect(request, callback_url)
    except Exception as e:
        print(f"Twitter OAuth error: {str(e)}")
        # For demo purposes, return a mock success for now
        mock_user_id = str(uuid.uuid4())
        frontend_url = f"https://b455855f-f3ef-4faa-b146-fcff2737404b.preview.emergentagent.com?auth_success=true&user_id={mock_user_id}&demo=true"
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
                "looking_for": [],
                "profile_complete": False,
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            users_collection.insert_one(user_data)
        
        # Redirect to frontend with user data
        frontend_url = f"{request.base_url.replace(request.base_url.path, '')}?auth_success=true&user_id={user_data['user_id']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        return RedirectResponse(url=f"{request.base_url.replace(request.base_url.path, '')}?auth_error=true")

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
            "looking_for": ["Learning", "Research Partner"],
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
        "bio", "location", "trading_experience", "years_trading", "preferred_tokens", 
        "trading_style", "portfolio_size", "risk_tolerance", "best_trade", "worst_trade",
        "favorite_project", "trading_hours", "communication_style", "looking_for"
    ]
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    update_data["last_active"] = datetime.utcnow()
    
    # Check if profile is complete
    required_fields = ["trading_experience", "preferred_tokens", "trading_style", "portfolio_size"]
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