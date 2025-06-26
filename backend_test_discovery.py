import requests
import json
import uuid
import random
import string
from datetime import datetime

# API Base URL
API_BASE_URL = "https://5f628bdb-f499-4e4d-ba90-973d0a8be29a.preview.emergentagent.com"

def print_separator():
    print("\n" + "="*80 + "\n")

def create_test_user():
    """Create a test user with email authentication"""
    # Generate random email to avoid conflicts
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"test_{random_suffix}@example.com"
    password = "TestPassword123!"
    display_name = f"Test User {random_suffix}"
    
    print(f"Creating test user with email: {email}")
    
    data = {
        "email": email,
        "password": password,
        "display_name": display_name
    }
    
    response = requests.post(f"{API_BASE_URL}/api/auth/email/signup", json=data)
    
    if response.status_code == 200:
        user_data = response.json().get("user")
        print(f"✅ User created successfully with ID: {user_data.get('user_id')}")
        return user_data
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def complete_user_profile(user_id):
    """Complete the user profile to make it discoverable"""
    profile_data = {
        "trading_experience": "Intermediate",
        "preferred_tokens": ["Meme Coins", "DeFi"],
        "trading_style": "Day Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "bio": "Test user for API testing",
        "location": "Test Location"
    }
    
    print(f"Completing profile for user ID: {user_id}")
    
    response = requests.put(f"{API_BASE_URL}/api/user/{user_id}", json=profile_data)
    
    if response.status_code == 200:
        print("✅ Profile completed successfully")
        return True
    else:
        print(f"❌ Failed to complete profile: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return False

def test_get_user(user_id):
    """Test getting a user profile"""
    print(f"Testing GET /api/user/{user_id}")
    
    response = requests.get(f"{API_BASE_URL}/api/user/{user_id}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Successfully retrieved user data")
        print(f"   Username: {user_data.get('username')}")
        print(f"   Profile Complete: {user_data.get('profile_complete')}")
        return user_data
    else:
        print(f"❌ Failed to get user data: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def test_discover_endpoint(user_id):
    """Test the discover endpoint"""
    print(f"Testing GET /api/discover/{user_id}")
    
    response = requests.get(f"{API_BASE_URL}/api/discover/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved discovery data")
        print(f"   Number of users returned: {len(data)}")
        
        # Check if the response is an array
        if isinstance(data, list):
            print("   Response is correctly formatted as an array")
            
            # Check the first user if available
            if data and len(data) > 0:
                first_user = data[0]
                print(f"   Sample user: {first_user.get('username')}")
                print(f"   Profile complete: {first_user.get('profile_complete')}")
                print(f"   User status: {first_user.get('user_status')}")
                print(f"   Last activity: {first_user.get('last_activity')}")
        else:
            print("❌ Response is not an array as expected")
            
        return data
    else:
        print(f"❌ Failed to get discovery data: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def test_ai_recommendations_endpoint(user_id):
    """Test the AI recommendations endpoint"""
    print(f"Testing GET /api/ai-recommendations/{user_id}")
    
    response = requests.get(f"{API_BASE_URL}/api/ai-recommendations/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved AI recommendations data")
        print(f"   Number of recommendations: {len(data)}")
        
        # Check if the response is an array
        if isinstance(data, list):
            print("   Response is correctly formatted as an array")
            
            # Check the first recommendation if available
            if data and len(data) > 0:
                first_rec = data[0]
                print(f"   Sample user: {first_rec.get('username')}")
                print(f"   Profile complete: {first_rec.get('profile_complete')}")
                print(f"   User status: {first_rec.get('user_status')}")
                
                # Check AI compatibility data
                ai_compat = first_rec.get('ai_compatibility')
                if ai_compat:
                    print(f"   Compatibility: {ai_compat.get('compatibility_percentage')}%")
                    print(f"   Recommendations: {ai_compat.get('recommendations')}")
                else:
                    print("❌ AI compatibility data missing")
        else:
            print("❌ Response is not an array as expected")
            
        return data
    else:
        print(f"❌ Failed to get AI recommendations: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def create_second_user_and_test_discovery():
    """Create a second user and test if they can discover each other"""
    # Create first user
    user1 = create_test_user()
    if not user1:
        return False
    
    # Complete first user's profile
    if not complete_user_profile(user1.get('user_id')):
        return False
    
    # Create second user
    user2 = create_test_user()
    if not user2:
        return False
    
    # Complete second user's profile
    if not complete_user_profile(user2.get('user_id')):
        return False
    
    print_separator()
    print("Testing if users can discover each other...")
    
    # Check if user1 can discover user2
    discover_results1 = test_discover_endpoint(user1.get('user_id'))
    
    user2_found = False
    if discover_results1:
        for user in discover_results1:
            if user.get('user_id') == user2.get('user_id'):
                user2_found = True
                break
    
    if user2_found:
        print("✅ User 1 can discover User 2")
    else:
        print("❌ User 1 cannot discover User 2")
    
    # Check if user2 can discover user1
    discover_results2 = test_discover_endpoint(user2.get('user_id'))
    
    user1_found = False
    if discover_results2:
        for user in discover_results2:
            if user.get('user_id') == user1.get('user_id'):
                user1_found = True
                break
    
    if user1_found:
        print("✅ User 2 can discover User 1")
    else:
        print("❌ User 2 cannot discover User 1")
    
    # Test AI recommendations
    print_separator()
    print("Testing AI recommendations...")
    
    ai_results1 = test_ai_recommendations_endpoint(user1.get('user_id'))
    ai_results2 = test_ai_recommendations_endpoint(user2.get('user_id'))
    
    return user1_found and user2_found

def check_users_in_database():
    """Check the number of users with complete profiles in the database"""
    print("Checking users in database...")
    
    # Create a test user to use for API calls
    test_user = create_test_user()
    if not test_user:
        return
    
    # Complete the test user's profile
    if not complete_user_profile(test_user.get('user_id')):
        return
    
    # Get discovery results to see how many users are available
    discover_results = test_discover_endpoint(test_user.get('user_id'))
    
    if discover_results:
        print(f"\nFound {len(discover_results)} discoverable users in the database")
        
        # Check if users are sorted by last_activity
        if len(discover_results) >= 2:
            print("\nChecking if users are sorted by last_activity...")
            
            prev_time = None
            sorted_correctly = True
            
            for i, user in enumerate(discover_results[:5]):  # Check first 5 users
                activity_time = user.get('last_activity')
                if activity_time and prev_time:
                    # Convert string times to datetime objects for comparison
                    if isinstance(activity_time, str):
                        current_time = datetime.fromisoformat(activity_time.replace('Z', '+00:00'))
                    else:
                        current_time = activity_time
                        
                    if isinstance(prev_time, str):
                        previous_time = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))
                    else:
                        previous_time = prev_time
                    
                    if current_time > previous_time:
                        print(f"❌ User at position {i} has more recent activity than user at position {i-1}")
                        sorted_correctly = False
                
                prev_time = activity_time
            
            if sorted_correctly:
                print("✅ Users appear to be correctly sorted by last_activity (most recent first)")
            else:
                print("❌ Users are not correctly sorted by last_activity")
    
    # Test AI recommendations
    ai_results = test_ai_recommendations_endpoint(test_user.get('user_id'))
    
    if ai_results:
        print(f"\nFound {len(ai_results)} AI recommendations")

def main():
    print("🚀 Starting Solm8 Discovery API Tests")
    print_separator()
    
    # Test with existing user
    print("TESTING WITH NEW USER")
    user = create_test_user()
    if not user:
        print("Failed to create test user, aborting tests")
        return
    
    print_separator()
    
    # Test getting user profile
    user_data = test_get_user(user.get('user_id'))
    
    print_separator()
    
    # Test discovery endpoint with incomplete profile (should fail or return empty)
    print("Testing discovery with incomplete profile (should fail or return empty):")
    discover_results_incomplete = test_discover_endpoint(user.get('user_id'))
    
    print_separator()
    
    # Complete the user profile
    complete_user_profile(user.get('user_id'))
    
    print_separator()
    
    # Verify profile is now complete
    updated_user = test_get_user(user.get('user_id'))
    
    print_separator()
    
    # Test discovery endpoint with complete profile
    print("Testing discovery with complete profile:")
    discover_results_complete = test_discover_endpoint(user.get('user_id'))
    
    print_separator()
    
    # Test AI recommendations endpoint
    ai_results = test_ai_recommendations_endpoint(user.get('user_id'))
    
    print_separator()
    
    # Create a second user and test discovery between them
    print("TESTING DISCOVERY BETWEEN TWO NEW USERS")
    create_second_user_and_test_discovery()
    
    print_separator()
    
    # Check users in database
    print("CHECKING USERS IN DATABASE")
    check_users_in_database()
    
    print_separator()
    print("🏁 Discovery API Tests Completed")

if __name__ == "__main__":
    main()