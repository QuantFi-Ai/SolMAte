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

def check_discovery_endpoint(user_id):
    """Check the raw response from the discovery endpoint"""
    print(f"Checking raw discovery response for user {user_id[:6]}...")
    
    response = requests.get(f"{BASE_URL}/api/discover/{user_id}")
    if response.status_code != 200:
        print(f"❌ Discover endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    discover_results = response.json()
    print(f"Discover returned {len(discover_results)} users")
    
    # Print the first few users
    if discover_results:
        print("Sample of discovered users:")
        for i, user in enumerate(discover_results[:3]):
            print(f"  {i+1}. {user.get('display_name')} (@{user.get('username')})")
            print(f"     - User ID: {user.get('user_id')}")
            print(f"     - Profile complete: {user.get('profile_complete')}")
    
    return discover_results

def check_swipes_collection(user_id):
    """Try to check the swipes collection indirectly"""
    print(f"Checking swipes for user {user_id[:6]}...")
    
    # Create a new user to test swiping
    test_user = create_user()
    if not test_user:
        return False
    
    # Complete the profile
    complete_user_profile(test_user['user_id'])
    
    # Try to swipe on the original user
    swipe_data = {
        "swiper_id": test_user['user_id'],
        "target_id": user_id,
        "action": "like"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/swipe",
        json=swipe_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Swipe failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    print(f"✅ Successfully swiped on user {user_id[:6]}")
    
    # Now check if the original user can discover the test user
    # (they shouldn't be able to if swipes are working correctly)
    response = requests.get(f"{BASE_URL}/api/discover/{user_id}")
    if response.status_code != 200:
        print(f"❌ Discover endpoint failed: {response.status_code}")
        return False
    
    discover_results = response.json()
    
    # Check if test_user is in the results
    test_user_found = False
    for user in discover_results:
        if user.get('user_id') == test_user['user_id']:
            test_user_found = True
            break
    
    if test_user_found:
        print(f"❌ User {user_id[:6]} can still discover User {test_user['user_id'][:6]} after being swiped on")
        print("This suggests swipes are not being properly excluded from discovery")
    else:
        print(f"✅ User {user_id[:6]} cannot discover User {test_user['user_id'][:6]} after being swiped on")
        print("This suggests swipes are working correctly")
    
    return not test_user_found

def check_discover_implementation():
    """Check if the discover endpoint is working as expected"""
    print("Checking discover endpoint implementation...")
    
    # Create two users
    user1 = create_user()
    user2 = create_user()
    
    if not user1 or not user2:
        return False
    
    # Complete both profiles
    if not complete_user_profile(user1['user_id']) or not complete_user_profile(user2['user_id']):
        return False
    
    # Check if user1 can discover user2
    print("\nChecking if User 1 can discover User 2 (before any swipes):")
    discover_results = check_discovery_endpoint(user1['user_id'])
    
    if not discover_results:
        return False
    
    # Check if user2 is in the results
    user2_found = False
    for user in discover_results:
        if user.get('user_id') == user2['user_id']:
            user2_found = True
            break
    
    if user2_found:
        print(f"✅ User 1 can discover User 2 (as expected)")
    else:
        print(f"❌ User 1 cannot discover User 2 (unexpected)")
        print("This suggests there's an issue with the discovery implementation")
    
    # Now test swipe functionality
    print("\nTesting swipe functionality:")
    swipe_data = {
        "swiper_id": user1['user_id'],
        "target_id": user2['user_id'],
        "action": "like"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/swipe",
        json=swipe_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Swipe failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    print(f"✅ User 1 successfully swiped on User 2")
    
    # Check if user1 can still discover user2 (they shouldn't)
    print("\nChecking if User 1 can discover User 2 (after swiping):")
    discover_results = check_discovery_endpoint(user1['user_id'])
    
    if not discover_results:
        return False
    
    # Check if user2 is in the results
    user2_found = False
    for user in discover_results:
        if user.get('user_id') == user2['user_id']:
            user2_found = True
            break
    
    if user2_found:
        print(f"❌ User 1 can still discover User 2 after swiping (unexpected)")
        print("This suggests swipes are not being properly excluded from discovery")
    else:
        print(f"✅ User 1 cannot discover User 2 after swiping (as expected)")
    
    return True

def check_discover_limit():
    """Check if the discover endpoint has a limit that's too low"""
    print("Checking if discover endpoint limit is too low...")
    
    # Create a user
    user = create_user()
    if not user:
        return False
    
    # Complete profile
    if not complete_user_profile(user['user_id']):
        return False
    
    # Check discovery with different limits
    limits = [10, 20, 50, 100]
    
    for limit in limits:
        response = requests.get(f"{BASE_URL}/api/discover/{user['user_id']}?limit={limit}")
        if response.status_code != 200:
            print(f"❌ Discover with limit={limit} failed: {response.status_code}")
            continue
        
        discover_results = response.json()
        print(f"Discover with limit={limit} returned {len(discover_results)} users")
        
        # If we get fewer users than the limit, we might have hit the total number of users
        if len(discover_results) < limit:
            print(f"⚠️ Discover returned fewer users ({len(discover_results)}) than requested ({limit})")
            print("This suggests we've reached the total number of available users")
            break
    
    return True

def main():
    print("🔍 SolM8 Discovery System Debug")
    print_separator()
    
    # Check discover implementation
    check_discover_implementation()
    print_separator()
    
    # Check discover limit
    check_discover_limit()
    print_separator()
    
    # Check swipes collection
    user = create_user()
    if user:
        complete_user_profile(user['user_id'])
        check_swipes_collection(user['user_id'])
    
    print_separator()
    print("🔍 Debug Complete")

if __name__ == "__main__":
    main()