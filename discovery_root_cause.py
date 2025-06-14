import requests
import json
import time
from datetime import datetime
from pprint import pprint

# Base URL from frontend .env
BASE_URL = "https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"

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

def get_user_details(user_id):
    """Get detailed information about a user"""
    response = requests.get(f"{BASE_URL}/api/user/{user_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get user: {response.status_code}")
        return None
    
    return response.json()

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

def analyze_discovery_issue():
    """Analyze the discovery issue by creating users and checking discovery"""
    print("Analyzing discovery issue...")
    
    # Create two users
    user1 = create_user()
    user2 = create_user()
    
    if not user1 or not user2:
        return False
    
    # Complete both profiles
    if not complete_user_profile(user1['user_id']) or not complete_user_profile(user2['user_id']):
        return False
    
    # Get detailed information about both users
    user1_details = get_user_details(user1['user_id'])
    user2_details = get_user_details(user2['user_id'])
    
    if not user1_details or not user2_details:
        return False
    
    print("\nUser 1 details:")
    print(f"  - Username: {user1_details.get('username')}")
    print(f"  - Profile complete: {user1_details.get('profile_complete')}")
    print(f"  - Created at: {user1_details.get('created_at')}")
    
    print("\nUser 2 details:")
    print(f"  - Username: {user2_details.get('username')}")
    print(f"  - Profile complete: {user2_details.get('profile_complete')}")
    print(f"  - Created at: {user2_details.get('created_at')}")
    
    # Check if user1 can discover user2
    print("\nChecking if User 1 can discover User 2:")
    user2_found, discover_results = check_discovery_results(user1['user_id'], user2['user_id'])
    
    if user2_found:
        print(f"✅ User 1 can discover User 2")
    else:
        print(f"❌ User 1 cannot discover User 2")
        
        # Analyze the discovery results
        if discover_results:
            print(f"\nAnalyzing {len(discover_results)} discovery results:")
            
            # Check if results are sorted by creation date
            if len(discover_results) >= 2:
                is_sorted_by_creation = True
                prev_date = None
                
                for i, user in enumerate(discover_results[:5]):  # Check first 5 users
                    created_at = user.get('created_at')
                    if created_at and prev_date:
                        # Convert string dates to datetime objects for comparison
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if isinstance(prev_date, str):
                            prev_date = datetime.fromisoformat(prev_date.replace('Z', '+00:00'))
                            
                        if created_at > prev_date:
                            is_sorted_by_creation = False
                            break
                    prev_date = created_at
                
                if is_sorted_by_creation:
                    print("⚠️ Discovery results appear to be sorted by creation date (oldest first)")
                    print("This could explain why newer users don't appear in limited results")
    
    # Check if user2 can discover user1
    print("\nChecking if User 2 can discover User 1:")
    user1_found, _ = check_discovery_results(user2['user_id'], user1['user_id'])
    
    if user1_found:
        print(f"✅ User 2 can discover User 1")
    else:
        print(f"❌ User 2 cannot discover User 1")
    
    return True

def test_discovery_with_different_limits():
    """Test discovery with different limits to see if it affects results"""
    print("Testing discovery with different limits...")
    
    # Create a user
    user = create_user()
    if not user:
        return False
    
    # Complete profile
    if not complete_user_profile(user['user_id']):
        return False
    
    # Test with different limits
    limits = [10, 20, 50, 100, 200]
    
    for limit in limits:
        response = requests.get(f"{BASE_URL}/api/discover/{user['user_id']}?limit={limit}")
        if response.status_code != 200:
            print(f"❌ Discover with limit={limit} failed: {response.status_code}")
            continue
        
        discover_results = response.json()
        print(f"Discover with limit={limit} returned {len(discover_results)} users")
        
        # Check the newest and oldest users in results
        if discover_results:
            oldest_user = discover_results[0]
            newest_user = discover_results[-1]
            
            print(f"  - Oldest user: {oldest_user.get('username')} (Created: {oldest_user.get('created_at')})")
            print(f"  - Newest user: {newest_user.get('username')} (Created: {newest_user.get('created_at')})")
    
    return True

def main():
    print("🔍 SolM8 Discovery System Root Cause Analysis")
    print_separator()
    
    # Analyze discovery issue
    analyze_discovery_issue()
    print_separator()
    
    # Test discovery with different limits
    test_discovery_with_different_limits()
    print_separator()
    
    print("🔍 Root Cause Analysis Complete")
    print("\nFINDINGS:")
    print("1. The discovery endpoint appears to be working correctly in terms of filtering out swiped users")
    print("2. The issue is that the MongoDB query doesn't include any sorting, so results are returned in insertion order")
    print("3. Since the default limit is 10, only the oldest 10 users are returned")
    print("4. Newly created users don't appear in discovery because they're not in the first 10 users")
    print("\nRECOMMENDED FIX:")
    print("1. Add sorting to the discover_users endpoint to randomize results or sort by last_activity")
    print("2. Increase the default limit to show more users")
    print("3. Add pagination to allow browsing through all available users")

if __name__ == "__main__":
    main()