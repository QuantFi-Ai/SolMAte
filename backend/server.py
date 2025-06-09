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

# Pydantic models
class UserProfile(BaseModel):
    user_id: str
    twitter_id: str
    username: str
    display_name: str
    avatar_url: str
    bio: str = ""
    trading_experience: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    preferred_tokens: List[str]  # ["Meme Coins", "DeFi", "GameFi", "NFTs", "Blue Chips"]
    trading_style: str  # "Day Trader", "Swing Trader", "HODLer", "Scalper"
    portfolio_size: str  # "Under $1K", "$1K-$10K", "$10K-$100K", "$100K+", "Prefer not to say"
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
    redirect_uri = f"{request.base_url}api/auth/twitter/callback"
    return await oauth.twitter.authorize_redirect(request, redirect_uri)

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
                "trading_experience": "",
                "preferred_tokens": [],
                "trading_style": "",
                "portfolio_size": "",
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            users_collection.insert_one(user_data)
        
        # Redirect to frontend with user data
        frontend_url = f"{request.base_url.replace(request.base_url.path, '')}?auth_success=true&user_id={user_data['user_id']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        return RedirectResponse(url=f"{request.base_url.replace(request.base_url.path, '')}?auth_error=true")

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
    allowed_fields = ["bio", "trading_experience", "preferred_tokens", "trading_style", "portfolio_size"]
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    update_data["last_active"] = datetime.utcnow()
    
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
        "trading_experience": {"$ne": ""},
        "preferred_tokens": {"$ne": []},
        "trading_style": {"$ne": ""},
        "portfolio_size": {"$ne": ""}
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