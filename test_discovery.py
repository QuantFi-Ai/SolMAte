import requests
import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.solm8_db
users_collection = db.users

# API base URL
base_url = "https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/api"

def test_discovery(user_id):
    """Test discovery endpoint for a specific user"""
    url = f"{base_url}/discover/{user_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        results = response.json()
        print(f"Discovery returned {len(results)} potential matches")
        
        # Get user details
        user = users_collection.find_one({"user_id": user_id})
        print(f"User: {user.get('username')}, Auth Method: {user.get('auth_method')}, Profile Complete: {user.get('profile_complete')}")
        
        # Check if the user has the required fields for profile completion
        has_required_fields = (
            bool(user.get("trading_experience")) and 
            bool(user.get("preferred_tokens")) and 
            len(user.get("preferred_tokens", [])) > 0 and
            bool(user.get("trading_style")) and 
            bool(user.get("portfolio_size"))
        )
        print(f"Has required fields: {has_required_fields}")
        
        # Print details of returned users
        print("\nDiscovered users:")
        for i, match in enumerate(results[:5]):  # Show first 5 only
            print(f"{i+1}. User ID: {match.get('user_id')}")
            print(f"   Username: {match.get('username')}")
            print(f"   Auth Method: {match.get('auth_method')}")
            print(f"   Profile Complete: {match.get('profile_complete')}")
            print(f"   Last Activity: {match.get('last_activity')}")
        
        return results
    else:
        print(f"Error: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def test_ai_recommendations(user_id):
    """Test AI recommendations endpoint for a specific user"""
    url = f"{base_url}/ai-recommendations/{user_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        results = response.json()
        print(f"AI recommendations returned {len(results)} potential matches")
        
        # Print details of returned users
        print("\nAI recommended users:")
        for i, match in enumerate(results[:5]):  # Show first 5 only
            print(f"{i+1}. User ID: {match.get('user_id')}")
            print(f"   Username: {match.get('username')}")
            print(f"   Auth Method: {match.get('auth_method')}")
            print(f"   Profile Complete: {match.get('profile_complete')}")
            print(f"   Last Activity: {match.get('last_activity')}")
            print(f"   Compatibility: {match.get('ai_compatibility', {}).get('compatibility_percentage')}%")
        
        return results
    else:
        print(f"Error: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def check_discovery_for_multiple_users():
    """Test discovery for multiple users"""
    # Get a mix of users with different auth methods
    email_users = list(users_collection.find({"auth_method": "email", "profile_complete": True}).limit(2))
    demo_users = list(users_collection.find({"auth_method": "demo", "profile_complete": True}).limit(2))
    other_users = list(users_collection.find({"auth_method": {"$exists": False}, "profile_complete": True}).limit(2))
    
    all_test_users = email_users + demo_users + other_users
    
    for user in all_test_users:
        user_id = user.get('user_id')
        print(f"\n{'='*50}")
        print(f"Testing discovery for user: {user.get('username')} (ID: {user_id})")
        print(f"{'='*50}")
        
        # Test regular discovery
        discover_results = test_discovery(user_id)
        
        # Test AI recommendations
        ai_results = test_ai_recommendations(user_id)
        
        print(f"\nSummary for {user.get('username')}:")
        print(f"Discovery results: {len(discover_results) if discover_results else 0}")
        print(f"AI recommendation results: {len(ai_results) if ai_results else 0}")

# Run the tests
check_discovery_for_multiple_users()