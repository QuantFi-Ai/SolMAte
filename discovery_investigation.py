import requests
import json
import time
from pprint import pprint

# Base URL from frontend .env
BASE_URL = "https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com"

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

def check_discovery(user_id, other_user_id):
    """Check if a user can discover another user"""
    response = requests.get(f"{BASE_URL}/api/discover/{user_id}")
    if response.status_code != 200:
        print(f"❌ Discover endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    discover_results = response.json()
    print(f"Discover returned {len(discover_results)} users")
    
    # Check if other_user_id is in the results
    other_user_found = False
    for user in discover_results:
        if user.get('user_id') == other_user_id:
            other_user_found = True
            break
    
    if other_user_found:
        print(f"✅ User {user_id[:6]} can discover User {other_user_id[:6]}")
    else:
        print(f"❌ User {user_id[:6]} cannot discover User {other_user_id[:6]}")
    
    return other_user_found

def check_swipes(user_id, other_user_id):
    """Check if a user has already swiped on another user"""
    # This requires direct database access, so we'll simulate by checking the swipe endpoint
    swipe_data = {
        "swiper_id": user_id,
        "target_id": other_user_id,
        "action": "like"
    }
    
    # First, let's check if we can swipe (which would indicate no prior swipe)
    response = requests.post(
        f"{BASE_URL}/api/swipe",
        json=swipe_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print(f"✅ User {user_id[:6]} successfully swiped on User {other_user_id[:6]} (no prior swipe)")
        return False  # No prior swipe
    else:
        print(f"❓ User {user_id[:6]} may have already swiped on User {other_user_id[:6]}")
        return True  # Possibly a prior swipe

def check_user_status(user_id):
    """Check a user's status and profile completion"""
    response = requests.get(f"{BASE_URL}/api/user/{user_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get user: {response.status_code}")
        return None
    
    user = response.json()
    print(f"User {user_id[:6]} status:")
    print(f"  - Username: {user.get('username')}")
    print(f"  - Display name: {user.get('display_name')}")
    print(f"  - Profile complete: {user.get('profile_complete')}")
    print(f"  - User status: {user.get('user_status')}")
    print(f"  - Last activity: {user.get('last_activity')}")
    
    return user

def update_user_status(user_id, status):
    """Update a user's status (active/offline)"""
    status_data = {
        "user_status": status
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user-status/{user_id}",
        json=status_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to update user status: {response.status_code}")
        return False
    
    print(f"✅ Updated user {user_id[:6]} status to {status}")
    return True

def test_discovery_with_status():
    """Test if user status affects discovery"""
    print("Testing if user status affects discovery...")
    
    # Create two users
    user1 = create_user()
    user2 = create_user()
    
    if not user1 or not user2:
        return False
    
    # Complete both profiles
    if not complete_user_profile(user1['user_id']) or not complete_user_profile(user2['user_id']):
        return False
    
    # Set both users to active
    update_user_status(user1['user_id'], "active")
    update_user_status(user2['user_id'], "active")
    
    # Check discovery with both active
    print("\nTesting discovery with both users active:")
    can_discover_active = check_discovery(user1['user_id'], user2['user_id'])
    
    # Set user2 to offline
    update_user_status(user2['user_id'], "offline")
    
    # Check discovery with one offline
    print("\nTesting discovery with one user offline:")
    can_discover_offline = check_discovery(user1['user_id'], user2['user_id'])
    
    return can_discover_active, can_discover_offline

def test_discovery_with_multiple_users():
    """Create multiple users and test discovery between them"""
    print("Testing discovery with multiple users...")
    
    # Create several users
    users = []
    for i in range(3):
        user = create_user()
        if not user:
            return False
        
        # Complete profile
        if not complete_user_profile(user['user_id']):
            return False
        
        # Set to active
        update_user_status(user['user_id'], "active")
        
        users.append(user)
    
    # Check discovery between all pairs
    discovery_results = []
    for i in range(len(users)):
        for j in range(len(users)):
            if i != j:  # Don't check discovery of self
                print(f"\nChecking if User {i+1} can discover User {j+1}:")
                result = check_discovery(users[i]['user_id'], users[j]['user_id'])
                discovery_results.append(result)
    
    return all(discovery_results)

def check_database_users():
    """Check how many users are in the database and their status"""
    print("Checking database users...")
    
    # Get active users
    response = requests.get(f"{BASE_URL}/api/users/active")
    if response.status_code != 200:
        print(f"❌ Failed to get active users: {response.status_code}")
        return False
    
    active_users = response.json().get('active_users', [])
    print(f"Found {len(active_users)} active users in the database")
    
    # Get a sample of users through discovery
    sample_user = create_user()
    if not sample_user:
        return False
    
    complete_user_profile(sample_user['user_id'])
    
    response = requests.get(f"{BASE_URL}/api/discover/{sample_user['user_id']}")
    if response.status_code != 200:
        print(f"❌ Failed to get discover users: {response.status_code}")
        return False
    
    discover_results = response.json()
    print(f"Discover endpoint returned {len(discover_results)} users")
    
    # Check profile completion status of discovered users
    incomplete_profiles = 0
    for user in discover_results:
        if not user.get('profile_complete'):
            incomplete_profiles += 1
    
    if incomplete_profiles > 0:
        print(f"⚠️ Found {incomplete_profiles} users with incomplete profiles in discovery results")
    else:
        print(f"✅ All discovered users have complete profiles")
    
    return True

def main():
    print("🔍 SolM8 Discovery System Investigation")
    print_separator()
    
    # Check database users
    check_database_users()
    print_separator()
    
    # Test discovery with user status
    active_discovery, offline_discovery = test_discovery_with_status()
    print_separator()
    
    # Test discovery with multiple users
    multi_user_discovery = test_discovery_with_multiple_users()
    print_separator()
    
    # Print summary
    print("📊 Investigation Summary:")
    print(f"- Discovery between active users: {'✅ Working' if active_discovery else '❌ Not working'}")
    print(f"- Discovery with offline users: {'✅ Working' if offline_discovery else '❌ Not working'}")
    print(f"- Multi-user discovery: {'✅ Working' if multi_user_discovery else '❌ Not working'}")
    
    if not active_discovery or not offline_discovery or not multi_user_discovery:
        print("\n🔴 ISSUE IDENTIFIED: Users cannot discover each other in the discovery feed.")
        print("Possible causes:")
        print("1. The swipes collection may contain records preventing discovery")
        print("2. The profile_complete flag may not be set correctly")
        print("3. There may be a limit on the number of users returned")
    else:
        print("\n✅ No issues identified with the discovery system.")

if __name__ == "__main__":
    main()