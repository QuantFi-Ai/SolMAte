import requests
import json
import random
import time
from datetime import datetime
from pprint import pprint

# Base URL from frontend .env
BASE_URL = "https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com"

def print_separator():
    print("\n" + "="*80 + "\n")

def create_user():
    """Create a test user"""
    response = requests.post(f"{BASE_URL}/api/create-demo-user")
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code}")
        return None
    
    user = response.json()
    print(f"✅ Created user: {user['username']} (ID: {user['user_id']})")
    return user

def complete_user_profile(user_id):
    """Complete a user's profile"""
    profile_data = {
        "bio": f"Test bio for user {user_id[:6]}",
        "location": "Test Location",
        "trading_experience": "Intermediate",
        "years_trading": 3,
        "preferred_tokens": ["Meme Coins", "DeFi", "NFTs"],
        "trading_style": "Day Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "looking_for": ["Alpha Sharing", "Research Partner"]
    }
    
    response = requests.put(
        f"{BASE_URL}/api/user/{user_id}",
        json=profile_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to update profile: {response.status_code}")
        return False
    
    # Verify profile is complete
    response = requests.get(f"{BASE_URL}/api/user/{user_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get user: {response.status_code}")
        return False
    
    user = response.json()
    if user.get('profile_complete'):
        print(f"✅ Profile marked as complete")
        return True
    else:
        print(f"❌ Profile not marked as complete")
        return False

def check_discovery_results(user_id, target_user_id, limit=100):
    """Check if target_user_id appears in discovery results for user_id"""
    response = requests.get(f"{BASE_URL}/api/discover/{user_id}?limit={limit}")
    if response.status_code != 200:
        print(f"❌ Discover endpoint failed: {response.status_code}")
        return False, None
    
    discover_results = response.json()
    
    # Check if target_user_id is in the results
    target_found = False
    for user in discover_results:
        if user.get('user_id') == target_user_id:
            target_found = True
            break
    
    return target_found, discover_results

def test_discovery_between_users():
    """Test if two newly created users can discover each other"""
    print("Testing discovery between newly created users...")
    
    # Create two users
    user1 = create_user()
    user2 = create_user()
    
    if not user1 or not user2:
        return False
    
    # Complete both profiles
    if not complete_user_profile(user1['user_id']) or not complete_user_profile(user2['user_id']):
        return False
    
    # Check if user1 can discover user2
    print("\nChecking if User 1 can discover User 2:")
    user2_found, _ = check_discovery_results(user1['user_id'], user2['user_id'])
    
    if user2_found:
        print(f"✅ User 1 can discover User 2")
    else:
        print(f"❌ User 1 cannot discover User 2")
    
    # Check if user2 can discover user1
    print("\nChecking if User 2 can discover User 1:")
    user1_found, _ = check_discovery_results(user2['user_id'], user1['user_id'])
    
    if user1_found:
        print(f"✅ User 2 can discover User 1")
    else:
        print(f"❌ User 2 cannot discover User 1")
    
    return user1_found or user2_found

def test_ai_recommendations():
    """Test if AI recommendations include newly created users"""
    print("Testing AI recommendations with newly created users...")
    
    # Create two users
    user1 = create_user()
    user2 = create_user()
    
    if not user1 or not user2:
        return False
    
    # Complete both profiles
    if not complete_user_profile(user1['user_id']) or not complete_user_profile(user2['user_id']):
        return False
    
    # Check if user1 can get AI recommendations including user2
    print("\nChecking if User 1's AI recommendations include User 2:")
    response = requests.get(f"{BASE_URL}/api/ai-recommendations/{user1['user_id']}")
    if response.status_code != 200:
        print(f"❌ AI recommendations endpoint failed: {response.status_code}")
        return False
    
    recommendations = response.json()
    
    # Check if user2 is in the recommendations
    user2_found = False
    for user in recommendations:
        if user.get('user_id') == user2['user_id']:
            user2_found = True
            break
    
    if user2_found:
        print(f"✅ User 1's AI recommendations include User 2")
    else:
        print(f"❌ User 1's AI recommendations do not include User 2")
    
    return user2_found

def main():
    print("🧪 SolM8 Discovery System Fix Verification")
    print_separator()
    
    print("RECOMMENDED FIX:")
    print("1. Add sorting to both endpoints to randomize results or sort by last_activity")
    print("2. For discover_users, modify line 1514-1517 to:")
    print("   potential_matches = list(users_collection.find({")
    print("       \"user_id\": {\"$nin\": swiped_user_ids},")
    print("       \"profile_complete\": True")
    print("   }).sort(\"last_activity\", -1).limit(limit))")
    
    print("\n3. For get_ai_recommendations, add sorting before calculating scores (around line 1480):")
    print("   potential_matches = list(users_collection.find({")
    print("       \"user_id\": {\"$nin\": swiped_user_ids},")
    print("       \"profile_complete\": True")
    print("   }).sort(\"last_activity\", -1))")
    
    print_separator()
    
    print("After implementing the fix, run this script again to verify that:")
    print("1. Newly created users can discover each other")
    print("2. AI recommendations include newly created users")
    
    print_separator()
    
    # Test discovery between users
    discovery_working = test_discovery_between_users()
    print_separator()
    
    # Test AI recommendations
    ai_recommendations_working = test_ai_recommendations()
    print_separator()
    
    # Print summary
    print("📊 Test Summary:")
    print(f"- Discovery between users: {'✅ Working' if discovery_working else '❌ Not working'}")
    print(f"- AI recommendations: {'✅ Working' if ai_recommendations_working else '❌ Not working'}")
    
    if not discovery_working or not ai_recommendations_working:
        print("\n🔴 FIX NOT VERIFIED: Users still cannot see each other in the discovery feed.")
        print("Please implement the recommended fix and run this script again.")
    else:
        print("\n✅ FIX VERIFIED: Users can now see each other in the discovery feed.")

if __name__ == "__main__":
    main()