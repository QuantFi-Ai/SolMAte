import requests
import json
import time
from pprint import pprint

# Base URL from frontend .env
BASE_URL = "https://ad8c686b-31d6-433d-aa09-b025124c7c61.preview.emergentagent.com"

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

def check_discovery_with_large_limit(user_id, limit=100):
    """Check discovery with a large limit to see if newly created users appear"""
    print(f"Checking discovery with limit={limit} for user {user_id[:6]}...")
    
    response = requests.get(f"{BASE_URL}/api/discover/{user_id}?limit={limit}")
    if response.status_code != 200:
        print(f"❌ Discover endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    discover_results = response.json()
    print(f"Discover returned {len(discover_results)} users")
    
    return discover_results

def create_multiple_users_and_check_discovery(num_users=5):
    """Create multiple users and check if they can discover each other with a large limit"""
    print(f"Creating {num_users} users and checking discovery...")
    
    users = []
    for i in range(num_users):
        user = create_user()
        if not user:
            return False
        
        # Complete profile
        if not complete_user_profile(user['user_id']):
            return False
        
        users.append(user)
    
    # Check if the first user can discover all other users
    discover_results = check_discovery_with_large_limit(users[0]['user_id'], limit=100)
    if not discover_results:
        return False
    
    # Check if all other users are in the results
    found_users = 0
    for i in range(1, len(users)):
        user_found = False
        for result in discover_results:
            if result.get('user_id') == users[i]['user_id']:
                user_found = True
                found_users += 1
                print(f"✅ Found User {i+1} in discovery results")
                break
        
        if not user_found:
            print(f"❌ Could not find User {i+1} in discovery results")
    
    print(f"Found {found_users} out of {num_users-1} users in discovery results")
    
    if found_users == num_users - 1:
        print("✅ All users can be discovered with a large enough limit")
        return True
    else:
        print("❌ Not all users can be discovered even with a large limit")
        return False

def check_discover_sorting():
    """Check if the discover endpoint sorts users in a way that might hide new users"""
    print("Checking if discover endpoint sorts users...")
    
    # Create a user
    user = create_user()
    if not user:
        return False
    
    # Complete profile
    if not complete_user_profile(user['user_id']):
        return False
    
    # Get discovery results
    discover_results = check_discovery_with_large_limit(user['user_id'], limit=100)
    if not discover_results:
        return False
    
    # Check if results appear to be sorted
    if len(discover_results) >= 2:
        print("\nChecking first few users in discovery results:")
        for i in range(min(5, len(discover_results))):
            user_data = discover_results[i]
            print(f"  {i+1}. {user_data.get('display_name')} (@{user_data.get('username')})")
            print(f"     - Created at: {user_data.get('created_at')}")
            print(f"     - Last active: {user_data.get('last_active')}")
    
    return True

def main():
    print("🔍 SolM8 Discovery System Final Check")
    print_separator()
    
    # Check discover sorting
    check_discover_sorting()
    print_separator()
    
    # Create multiple users and check discovery
    create_multiple_users_and_check_discovery(num_users=5)
    print_separator()
    
    print("🔍 Final Check Complete")

if __name__ == "__main__":
    main()