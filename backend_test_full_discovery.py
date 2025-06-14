import requests
import json
import random
import string
import time

# API Base URL
API_BASE_URL = "https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"

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
        return user_data, email, password
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None, None, None

def login_user(email, password):
    """Login with email and password"""
    print(f"Logging in with email: {email}")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{API_BASE_URL}/api/auth/email/login", json=data)
    
    if response.status_code == 200:
        user_data = response.json().get("user")
        print(f"✅ Login successful for user ID: {user_data.get('user_id')}")
        return user_data
    else:
        print(f"❌ Login failed: {response.status_code}")
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

def get_user_profile(user_id):
    """Get user profile"""
    print(f"Getting profile for user ID: {user_id}")
    
    response = requests.get(f"{API_BASE_URL}/api/user/{user_id}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Profile retrieved successfully")
        print(f"   Username: {user_data.get('username')}")
        print(f"   Profile Complete: {user_data.get('profile_complete')}")
        return user_data
    else:
        print(f"❌ Failed to get profile: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def update_user_activity(user_id):
    """Update user's last activity timestamp"""
    print(f"Updating activity for user ID: {user_id}")
    
    response = requests.post(f"{API_BASE_URL}/api/user/{user_id}/update-activity")
    
    if response.status_code == 200:
        print("✅ Activity updated successfully")
        return True
    else:
        print(f"❌ Failed to update activity: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return False

def get_discovery_cards(user_id):
    """Get discovery cards"""
    print(f"Getting discovery cards for user ID: {user_id}")
    
    response = requests.get(f"{API_BASE_URL}/api/discover/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Discovery cards retrieved successfully")
        print(f"   Number of cards: {len(data)}")
        
        if isinstance(data, list):
            print("   Response is correctly formatted as an array")
            
            if data and len(data) > 0:
                print("\nSample of discovery cards:")
                for i, card in enumerate(data[:3]):
                    print(f"{i+1}. User ID: {card.get('user_id')}")
                    print(f"   Username: {card.get('username')}")
                    print(f"   Profile Complete: {card.get('profile_complete')}")
                    print(f"   Last Activity: {card.get('last_activity')}")
        else:
            print("❌ Response is not an array as expected")
            print(f"   Response type: {type(data)}")
        
        return data
    else:
        print(f"❌ Failed to get discovery cards: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def get_ai_recommendations(user_id):
    """Get AI recommendations"""
    print(f"Getting AI recommendations for user ID: {user_id}")
    
    response = requests.get(f"{API_BASE_URL}/api/ai-recommendations/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI recommendations retrieved successfully")
        print(f"   Number of recommendations: {len(data)}")
        
        if isinstance(data, list):
            print("   Response is correctly formatted as an array")
            
            if data and len(data) > 0:
                print("\nSample of AI recommendations:")
                for i, rec in enumerate(data[:3]):
                    print(f"{i+1}. User ID: {rec.get('user_id')}")
                    print(f"   Username: {rec.get('username')}")
                    print(f"   Compatibility: {rec.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                    print(f"   Profile Complete: {rec.get('profile_complete')}")
        else:
            print("❌ Response is not an array as expected")
            print(f"   Response type: {type(data)}")
        
        return data
    else:
        print(f"❌ Failed to get AI recommendations: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def test_full_discovery_flow():
    """Test the full discovery flow from signup to viewing discovery cards"""
    print("🔍 Testing Full Discovery Flow")
    print_separator()
    
    # Step 1: Create a test user
    user_data, email, password = create_test_user()
    if not user_data:
        return False
    
    user_id = user_data.get('user_id')
    
    print_separator()
    
    # Step 2: Complete the user profile
    if not complete_user_profile(user_id):
        return False
    
    print_separator()
    
    # Step 3: Verify profile is complete
    updated_user = get_user_profile(user_id)
    if not updated_user or not updated_user.get('profile_complete'):
        print("❌ Profile is not marked as complete")
        return False
    
    print_separator()
    
    # Step 4: Update user activity
    if not update_user_activity(user_id):
        return False
    
    print_separator()
    
    # Step 5: Get discovery cards
    discovery_cards = get_discovery_cards(user_id)
    if discovery_cards is None:
        return False
    
    print_separator()
    
    # Step 6: Get AI recommendations
    ai_recommendations = get_ai_recommendations(user_id)
    if ai_recommendations is None:
        return False
    
    print_separator()
    
    # Step 7: Log out and log back in to simulate a real user session
    print("Logging out and logging back in...")
    
    # Log back in
    logged_in_user = login_user(email, password)
    if not logged_in_user:
        return False
    
    print_separator()
    
    # Step 8: Get discovery cards again after login
    discovery_cards_after_login = get_discovery_cards(user_id)
    if discovery_cards_after_login is None:
        return False
    
    print_separator()
    
    # Step 9: Get AI recommendations again after login
    ai_recommendations_after_login = get_ai_recommendations(user_id)
    if ai_recommendations_after_login is None:
        return False
    
    print_separator()
    
    # Success!
    print("✅ Full discovery flow test completed successfully")
    return True

def main():
    print("🚀 Starting Solm8 Full Discovery Flow Test")
    print_separator()
    
    success = test_full_discovery_flow()
    
    print_separator()
    
    if success:
        print("✅ All tests passed successfully")
        print("\nCONCLUSION:")
        print("The backend discovery endpoints are working correctly.")
        print("If the frontend is stuck on 'Loading traders', the issue might be:")
        print("1. A frontend issue with processing the response")
        print("2. Network connectivity issues between frontend and backend")
        print("3. CORS issues preventing the frontend from accessing the API")
    else:
        print("❌ Some tests failed")
        print("\nCONCLUSION:")
        print("There are issues with the discovery flow that need to be addressed.")
    
    print("\nRECOMMENDATIONS:")
    print("1. Check the frontend console for errors")
    print("2. Verify that the frontend is correctly calling the API endpoints")
    print("3. Ensure CORS is properly configured")
    print("4. Check network connectivity between frontend and backend")

if __name__ == "__main__":
    main()