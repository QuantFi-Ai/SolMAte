import requests
import json
from pymongo import MongoClient
import uuid
import random
import string
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.solm8_db

# API base URL
BASE_URL = "https://8134b81b-ad13-497e-ba8a-ecdf0793b0b4.preview.emergentagent.com/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def check_user_profile(user_id):
    """Check a user's profile in the database"""
    print(f"🔍 Checking user profile for ID: {user_id}")
    
    user = db.users.find_one({"user_id": user_id})
    if not user:
        print(f"❌ User not found in database")
        return None
    
    print(f"✅ User found: {user.get('username')} ({user.get('display_name')})")
    print(f"Profile complete: {user.get('profile_complete')}")
    print(f"Trading experience: '{user.get('trading_experience')}'")
    print(f"Preferred tokens: {user.get('preferred_tokens')}")
    print(f"Trading style: '{user.get('trading_style')}'")
    print(f"Portfolio size: '{user.get('portfolio_size')}'")
    
    return user

def check_user_swipes(user_id):
    """Check a user's swipes in the database"""
    print(f"🔍 Checking swipes for user ID: {user_id}")
    
    swipes = list(db.swipes.find({"swiper_id": user_id}))
    print(f"Total swipes: {len(swipes)}")
    
    if swipes:
        print("Sample swipes:")
        for i, swipe in enumerate(swipes[:5]):
            print(f"{i+1}. Target: {swipe.get('target_id')}, Action: {swipe.get('action')}")
    
    return swipes

def check_discovery_api(user_id):
    """Check the discovery API for a user"""
    print(f"🔍 Testing discovery API for user ID: {user_id}")
    
    url = f"{BASE_URL}/discover/{user_id}"
    response = requests.get(url)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Discovery returned {len(data)} potential matches")
        
        if data:
            print("Sample matches:")
            for i, match in enumerate(data[:3]):
                print(f"{i+1}. User ID: {match.get('user_id')}, Username: {match.get('username')}")
                print(f"   Profile Complete: {match.get('profile_complete')}")
                print(f"   Trading Experience: '{match.get('trading_experience')}'")
        
        return data
    else:
        print(f"❌ API error: {response.text}")
        return None

def check_ai_recommendations_api(user_id):
    """Check the AI recommendations API for a user"""
    print(f"🔍 Testing AI recommendations API for user ID: {user_id}")
    
    url = f"{BASE_URL}/ai-recommendations/{user_id}"
    response = requests.get(url)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"AI recommendations returned {len(data)} potential matches")
        
        if data:
            print("Sample recommendations:")
            for i, match in enumerate(data[:3]):
                print(f"{i+1}. User ID: {match.get('user_id')}, Username: {match.get('username')}")
                print(f"   Compatibility: {match.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                print(f"   Profile Complete: {match.get('profile_complete')}")
        
        return data
    else:
        print(f"❌ API error: {response.text}")
        return None

def analyze_discovery_issue(user_id):
    """Analyze why a user might not be seeing any discovery results"""
    print(f"🔍 Analyzing discovery issue for user ID: {user_id}")
    
    # Step 1: Check user profile
    user = check_user_profile(user_id)
    if not user:
        return
    
    print_separator()
    
    # Step 2: Check user swipes
    swipes = check_user_swipes(user_id)
    swiped_ids = set([s['target_id'] for s in swipes])
    
    print_separator()
    
    # Step 3: Check available users with complete profiles
    complete_profiles = list(db.users.find({"profile_complete": True}))
    complete_ids = set([u['user_id'] for u in complete_profiles])
    
    print(f"Total users with complete profiles: {len(complete_profiles)}")
    
    # Step 4: Calculate remaining users to discover
    remaining = complete_ids - swiped_ids - set([user_id])
    
    print(f"Remaining users to discover: {len(remaining)}")
    if remaining:
        print(f"Sample remaining user IDs: {list(remaining)[:5]}")
    
    print_separator()
    
    # Step 5: Check discovery API
    discovery_results = check_discovery_api(user_id)
    
    print_separator()
    
    # Step 6: Check AI recommendations API
    ai_results = check_ai_recommendations_api(user_id)
    
    print_separator()
    
    # Step 7: Analyze results
    print("📊 Analysis:")
    
    if not user.get('profile_complete'):
        print("❌ User's profile is not complete - this will prevent discovery")
    
    if len(remaining) == 0:
        print("❌ User has already swiped on all available users with complete profiles")
    
    if discovery_results is not None and len(discovery_results) == 0 and len(remaining) > 0:
        print("❓ User should be seeing discovery results but isn't - possible API issue")
    
    if ai_results is not None and len(ai_results) == 0 and len(remaining) > 0:
        print("❓ User should be seeing AI recommendations but isn't - possible API issue")

def create_test_user():
    """Create a test user with a complete profile"""
    print("🔍 Creating a test user with complete profile")
    
    # Generate random user data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f"test_user_{random_suffix}"
    display_name = f"Test User {random_suffix}"
    
    # Create user document
    user_id = str(uuid.uuid4())
    user_data = {
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "email": f"{username}@example.com",
        "avatar_url": "https://images.pexels.com/photos/31610834/pexels-photo-31610834.jpeg",
        "bio": "Test user for debugging discovery",
        "location": "Test Location",
        "timezone": "UTC",
        "user_status": "active",
        "last_activity": datetime.utcnow(),
        "show_twitter": False,
        "twitter_username": "",
        "trading_experience": "Intermediate",
        "years_trading": 2,
        "preferred_tokens": ["Meme Coins", "DeFi"],
        "trading_style": "Day Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "best_trade": "Test trade",
        "worst_trade": "Test trade",
        "favorite_project": "Test project",
        "trading_hours": "Morning",
        "communication_style": "Casual",
        "preferred_communication_platform": "Discord",
        "preferred_trading_platform": "Jupiter",
        "looking_for": ["Learning", "Alpha Sharing"],
        "interested_in_token_launch": False,
        "token_launch_experience": "",
        "launch_timeline": "",
        "launch_budget": "",
        "profile_complete": True,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow(),
        "auth_method": "email"
    }
    
    # Insert user into database
    db.users.insert_one(user_data)
    
    print(f"✅ Created test user with ID: {user_id}")
    print(f"Username: {username}")
    print(f"Display name: {display_name}")
    
    return user_id

def test_discovery_with_new_users():
    """Test discovery with newly created users"""
    print("🔍 Testing discovery with new users")
    
    # Create two test users
    user_a_id = create_test_user()
    print_separator()
    user_b_id = create_test_user()
    print_separator()
    
    # Check if User A can discover User B
    print("Testing if User A can discover User B...")
    discovery_results = check_discovery_api(user_a_id)
    
    user_b_found = False
    if discovery_results:
        for user in discovery_results:
            if user.get('user_id') == user_b_id:
                user_b_found = True
                break
    
    if user_b_found:
        print("✅ User A can discover User B")
    else:
        print("❌ User A cannot discover User B")
    
    print_separator()
    
    # Check if User B can discover User A
    print("Testing if User B can discover User A...")
    discovery_results = check_discovery_api(user_b_id)
    
    user_a_found = False
    if discovery_results:
        for user in discovery_results:
            if user.get('user_id') == user_a_id:
                user_a_found = True
                break
    
    if user_a_found:
        print("✅ User B can discover User A")
    else:
        print("❌ User B cannot discover User A")
    
    return user_a_id, user_b_id

def test_discovery_with_specific_user(user_id):
    """Test discovery with a specific user ID"""
    print(f"🔍 Testing discovery for specific user ID: {user_id}")
    
    # Create a test user
    test_user_id = create_test_user()
    print_separator()
    
    # Check if the specific user can discover the test user
    print(f"Testing if user {user_id} can discover test user {test_user_id}...")
    discovery_results = check_discovery_api(user_id)
    
    test_user_found = False
    if discovery_results:
        for user in discovery_results:
            if user.get('user_id') == test_user_id:
                test_user_found = True
                break
    
    if test_user_found:
        print(f"✅ User {user_id} can discover test user {test_user_id}")
    else:
        print(f"❌ User {user_id} cannot discover test user {test_user_id}")
    
    print_separator()
    
    # Check if the test user can discover the specific user
    print(f"Testing if test user {test_user_id} can discover user {user_id}...")
    discovery_results = check_discovery_api(test_user_id)
    
    specific_user_found = False
    if discovery_results:
        for user in discovery_results:
            if user.get('user_id') == user_id:
                specific_user_found = True
                break
    
    if specific_user_found:
        print(f"✅ Test user {test_user_id} can discover user {user_id}")
    else:
        print(f"❌ Test user {test_user_id} cannot discover user {user_id}")
    
    return test_user_id

if __name__ == "__main__":
    # Analyze discovery issue for the specific user
    user_id = "17d9709a-9a6f-4418-8cb4-765faca422a8"
    analyze_discovery_issue(user_id)
    
    print_separator()
    print("TESTING WITH NEW USERS")
    print_separator()
    
    # Test discovery with new users
    test_discovery_with_new_users()
    
    print_separator()
    print("TESTING WITH SPECIFIC USER")
    print_separator()
    
    # Test discovery with the specific user
    test_discovery_with_specific_user(user_id)
