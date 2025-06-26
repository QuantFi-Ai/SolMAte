import requests
import json
import random
import string
from datetime import datetime

# Base URL
base_url = "https://5f628bdb-f499-4e4d-ba90-973d0a8be29a.preview.emergentagent.com/api"

def create_test_user():
    """Create a test user and return the user ID"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"test_user_{random_suffix}@example.com"
    display_name = f"Test User {random_suffix}"
    
    data = {
        "email": email,
        "password": "TestPassword123!",
        "display_name": display_name
    }
    
    response = requests.post(f"{base_url}/auth/email/signup", json=data)
    if response.status_code == 200:
        user_data = response.json().get("user")
        print(f"Created test user: {user_data['display_name']} (ID: {user_data['user_id']})")
        return user_data
    else:
        print(f"Failed to create test user: {response.text}")
        return None

def complete_user_profile(user_id):
    """Complete a user's profile"""
    profile_data = {
        "trading_experience": "Intermediate",
        "preferred_tokens": ["Meme Coins", "DeFi"],
        "trading_style": "Day Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "bio": "Test user for API testing",
        "location": "Test Location"
    }
    
    response = requests.put(f"{base_url}/user/{user_id}", json=profile_data)
    if response.status_code == 200:
        print(f"Updated user profile successfully")
        return True
    else:
        print(f"Failed to update user profile: {response.text}")
        return False

def test_endpoint(name, endpoint, expected_keys=None):
    """Test an API endpoint and print the response"""
    print(f"\n===== Testing {name} =====")
    url = f"{base_url}/{endpoint}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Number of items: {len(data)}")
                if len(data) > 0:
                    first_item = data[0]
                    print(f"First item keys: {list(first_item.keys())}")
                    
                    # Check for expected keys
                    if expected_keys:
                        missing_keys = [key for key in expected_keys if key not in first_item]
                        if missing_keys:
                            print(f"❌ Missing expected keys: {missing_keys}")
                        else:
                            print(f"✅ All expected keys present")
                    
                    # Print sample data
                    print(f"Sample data: {json.dumps(first_item, indent=2)[:500]}...")
                    
                    return data
            else:
                print(f"Response keys: {list(data.keys())}")
                
                # Check for expected keys
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in data]
                    if missing_keys:
                        print(f"❌ Missing expected keys: {missing_keys}")
                    else:
                        print(f"✅ All expected keys present")
                
                # Print sample data
                print(f"Sample data: {json.dumps(data, indent=2)[:500]}...")
                
                return data
        else:
            print(f"Error: {response.text}")
            return None
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def create_match(user1_id, user2_id):
    """Create a match between two users by having them swipe on each other"""
    # User 1 swipes on User 2
    data1 = {
        "swiper_id": user1_id,
        "target_id": user2_id,
        "action": "like"
    }
    response1 = requests.post(f"{base_url}/swipe", json=data1)
    if response1.status_code != 200:
        print(f"Failed when User 1 swiped on User 2: {response1.text}")
        return None
    
    # User 2 swipes on User 1
    data2 = {
        "swiper_id": user2_id,
        "target_id": user1_id,
        "action": "like"
    }
    response2 = requests.post(f"{base_url}/swipe", json=data2)
    if response2.status_code != 200:
        print(f"Failed when User 2 swiped on User 1: {response2.text}")
        return None
    
    match_data = response2.json()
    if match_data.get('matched'):
        match_id = match_data.get('match_id')
        print(f"Created match with ID: {match_id}")
        return match_id
    else:
        print("No match was created")
        return None

def send_message(match_id, sender_id, content):
    """Send a message in a match"""
    data = {
        "match_id": match_id,
        "sender_id": sender_id,
        "content": content
    }
    
    response = requests.post(f"{base_url}/messages", json=data)
    if response.status_code == 200:
        print(f"Sent message successfully: {content}")
        return response.json()
    else:
        print(f"Failed to send message: {response.text}")
        return None

def test_discovery_and_matches():
    """Test the discovery and matches functionality with new users"""
    print("\n===== TESTING DISCOVERY AND MATCHES FUNCTIONALITY WITH NEW USERS =====")
    
    # Create two test users
    user1 = create_test_user()
    user2 = create_test_user()
    
    if not user1 or not user2:
        print("Failed to create test users")
        return
    
    # Complete profiles for both users
    if not complete_user_profile(user1['user_id']) or not complete_user_profile(user2['user_id']):
        print("Failed to complete user profiles")
        return
    
    # Test discovery endpoints
    discover_expected_keys = ['user_id', 'username', 'display_name', 'avatar_url', 'trading_experience', 
                             'preferred_tokens', 'trading_style', 'portfolio_size']
    
    discover_results = test_endpoint("Discover Users", f"discover/{user1['user_id']}", discover_expected_keys)
    ai_results = test_endpoint("AI Recommendations", f"ai-recommendations/{user1['user_id']}", discover_expected_keys + ['ai_compatibility'])
    
    # Create a match between the users
    match_id = create_match(user1['user_id'], user2['user_id'])
    if not match_id:
        print("Failed to create match")
        return
    
    # Test matches endpoints
    matches_expected_keys = ['match_id', 'user1_id', 'user2_id', 'created_at', 'last_message_at', 'other_user']
    matches_with_messages_expected_keys = matches_expected_keys + ['latest_message', 'unread_count']
    
    matches = test_endpoint("User Matches", f"matches/{user1['user_id']}", matches_expected_keys)
    matches_with_messages = test_endpoint("Matches with Messages", f"matches-with-messages/{user1['user_id']}", matches_with_messages_expected_keys)
    
    # Check other_user structure
    if matches and len(matches) > 0:
        other_user = matches[0].get('other_user', {})
        other_user_keys = list(other_user.keys())
        print(f"\nOther User keys: {other_user_keys}")
        
        expected_other_user_keys = ['user_id', 'username', 'display_name', 'avatar_url']
        missing_keys = [key for key in expected_other_user_keys if key not in other_user]
        if missing_keys:
            print(f"❌ Missing expected keys in other_user: {missing_keys}")
        else:
            print(f"✅ All expected keys present in other_user")
    
    # Send a message
    if match_id:
        message = send_message(match_id, user1['user_id'], f"Test message from {user1['display_name']} at {datetime.now().strftime('%H:%M:%S')}")
        
        # Test getting messages
        messages = test_endpoint("Match Messages", f"messages/{match_id}")
        
        # Test matches with messages again to see the updated message
        updated_matches_with_messages = test_endpoint("Updated Matches with Messages", f"matches-with-messages/{user1['user_id']}")

def test_with_existing_users():
    """Test with existing user IDs"""
    print("\n===== TESTING WITH EXISTING USERS =====")
    
    # Use the user IDs from our previous test
    user_ids = [
        "087e057e-0b48-4222-b994-7e4208962470",  # User A from previous test
        "0a761e79-ba11-4333-bb10-23d714ffdf27"   # User B from previous test
    ]
    
    for user_id in user_ids:
        print(f"\n----- Testing with User ID: {user_id} -----")
        
        # Test discovery endpoints
        discover_expected_keys = ['user_id', 'username', 'display_name', 'avatar_url', 'trading_experience', 
                                'preferred_tokens', 'trading_style', 'portfolio_size']
        
        discover_results = test_endpoint("Discover Users", f"discover/{user_id}", discover_expected_keys)
        ai_results = test_endpoint("AI Recommendations", f"ai-recommendations/{user_id}", discover_expected_keys + ['ai_compatibility'])
        
        # Test matches endpoints
        matches_expected_keys = ['match_id', 'user1_id', 'user2_id', 'created_at', 'last_message_at', 'other_user']
        matches_with_messages_expected_keys = matches_expected_keys + ['latest_message', 'unread_count']
        
        matches = test_endpoint("User Matches", f"matches/{user_id}", matches_expected_keys)
        matches_with_messages = test_endpoint("Matches with Messages", f"matches-with-messages/{user_id}", matches_with_messages_expected_keys)
        
        # Check other_user structure
        if matches and len(matches) > 0:
            other_user = matches[0].get('other_user', {})
            other_user_keys = list(other_user.keys())
            print(f"\nOther User keys: {other_user_keys}")
            
            expected_other_user_keys = ['user_id', 'username', 'display_name', 'avatar_url']
            missing_keys = [key for key in expected_other_user_keys if key not in other_user]
            if missing_keys:
                print(f"❌ Missing expected keys in other_user: {missing_keys}")
            else:
                print(f"✅ All expected keys present in other_user")
            
            # Check if match has messages
            if matches_with_messages and len(matches_with_messages) > 0:
                match_id = matches_with_messages[0].get('match_id')
                if match_id:
                    messages = test_endpoint("Match Messages", f"messages/{match_id}")

if __name__ == "__main__":
    # Test with new users
    test_discovery_and_matches()
    
    # Test with existing users
    test_with_existing_users()