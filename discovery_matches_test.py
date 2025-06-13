import requests
import unittest
import uuid
import os
import json
import random
import string
from datetime import datetime

class Solm8DiscoveryMatchesTester:
    def __init__(self, base_url="https://8134b81b-ad13-497e-ba8a-ecdf0793b0b4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.email_user = None
        self.email_user2 = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        default_headers = {'Content-Type': 'application/json'} if not files else {}
        if headers:
            default_headers.update(headers)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_email_signup(self, email=None, password=None, display_name=None):
        """Test email signup"""
        if not email:
            # Generate random email to avoid conflicts
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"test_{random_suffix}@example.com"
        
        if not password:
            password = "TestPassword123!"
            
        if not display_name:
            display_name = f"Test User {random_suffix}"
            
        data = {
            "email": email,
            "password": password,
            "display_name": display_name
        }
        
        success, response = self.run_test(
            "Email Signup",
            "POST",
            "auth/email/signup",
            200,
            data=data
        )
        
        if success:
            self.email_user = response.get("user")
            print(f"Created email user: {self.email_user['username']}")
            
        return success, response

    def test_get_user(self, user_id):
        """Test getting a user profile"""
        return self.run_test(
            "Get User Profile",
            "GET",
            f"user/{user_id}",
            200
        )

    def test_update_user_profile(self, user_id, profile_data):
        """Test updating a user profile"""
        return self.run_test(
            "Update User Profile",
            "PUT",
            f"user/{user_id}",
            200,
            data=profile_data
        )

    def test_discover_users(self, user_id):
        """Test discovering potential matches"""
        return self.run_test(
            "Discover Users",
            "GET",
            f"discover/{user_id}",
            200
        )

    def test_ai_recommendations(self, user_id):
        """Test getting AI recommendations"""
        return self.run_test(
            "AI Recommendations",
            "GET",
            f"ai-recommendations/{user_id}",
            200
        )

    def test_swipe(self, swiper_id, target_id, action="like"):
        """Test swiping on a user"""
        data = {
            "swiper_id": swiper_id,
            "target_id": target_id,
            "action": action
        }
        
        return self.run_test(
            f"Swipe {action} on user",
            "POST",
            "swipe",
            200,
            data=data
        )

    def test_get_matches(self, user_id):
        """Test getting user matches"""
        return self.run_test(
            "Get User Matches",
            "GET",
            f"matches/{user_id}",
            200
        )

    def test_get_matches_with_messages(self, user_id):
        """Test getting user matches with messages"""
        return self.run_test(
            "Get User Matches with Messages",
            "GET",
            f"matches-with-messages/{user_id}",
            200
        )

    def test_send_message(self, match_id, sender_id, content):
        """Test sending a message"""
        data = {
            "match_id": match_id,
            "sender_id": sender_id,
            "content": content
        }
        
        return self.run_test(
            "Send Message",
            "POST",
            "messages",
            200,
            data=data
        )

    def test_get_messages(self, match_id):
        """Test getting messages for a match"""
        return self.run_test(
            "Get Match Messages",
            "GET",
            f"messages/{match_id}",
            200
        )

    def test_discovery_and_matches(self):
        """Test the discovery and matches functionality"""
        print("\n===== TESTING DISCOVERY AND MATCHES FUNCTIONALITY =====")
        
        # Step 1: Create two test users
        print("\n1️⃣ Creating two test users...")
        
        # User A
        random_suffix_a = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_a = f"test_a_{random_suffix_a}@example.com"
        display_name_a = f"Test User A {random_suffix_a}"
        
        success, signup_response_a = self.test_email_signup(email_a, "TestPassword123!", display_name_a)
        if not success:
            print("❌ Failed to create User A")
            return False
        
        user_a_id = self.email_user['user_id']
        
        # User B
        random_suffix_b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_b = f"test_b_{random_suffix_b}@example.com"
        display_name_b = f"Test User B {random_suffix_b}"
        
        success, signup_response_b = self.test_email_signup(email_b, "TestPassword123!", display_name_b)
        if not success:
            print("❌ Failed to create User B")
            return False
        
        self.email_user2 = signup_response_b.get("user")
        user_b_id = self.email_user2['user_id']
        
        print(f"Created User A (ID: {user_a_id}) and User B (ID: {user_b_id})")
        
        # Step 2: Complete profiles for both users
        print("\n2️⃣ Completing profiles for both users...")
        
        complete_profile_a = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        complete_profile_b = {
            "trading_experience": "Advanced",
            "preferred_tokens": ["NFTs", "GameFi"],
            "trading_style": "Swing Trader",
            "portfolio_size": "$100K+"
        }
        
        success, _ = self.test_update_user_profile(user_a_id, complete_profile_a)
        if not success:
            print("❌ Failed to update User A's profile")
            return False
        
        success, _ = self.test_update_user_profile(user_b_id, complete_profile_b)
        if not success:
            print("❌ Failed to update User B's profile")
            return False
        
        # Verify both profiles are marked as complete
        success, user_a = self.test_get_user(user_a_id)
        success, user_b = self.test_get_user(user_b_id)
        
        if not user_a.get('profile_complete') or not user_b.get('profile_complete'):
            print("❌ One or both user profiles not marked as complete")
            return False
        
        print("✅ Both user profiles marked as complete")
        
        # Step 3: Test discovery endpoints
        print("\n3️⃣ Testing discovery endpoints...")
        
        # Test regular discovery
        success, discover_results_a = self.test_discover_users(user_a_id)
        if not success:
            print("❌ Failed to get discovery results for User A")
            return False
        
        print(f"Discovery returned {len(discover_results_a)} potential matches for User A")
        print("Discovery response format:")
        if discover_results_a and len(discover_results_a) > 0:
            print(f"First item type: {type(discover_results_a)}")
            print(f"First item keys: {discover_results_a[0].keys() if isinstance(discover_results_a, list) else 'Not a list'}")
            
            # Check if User B is in the discovery results
            user_b_found = False
            for user in discover_results_a:
                if user.get('user_id') == user_b_id:
                    user_b_found = True
                    break
            
            if user_b_found:
                print("✅ User A can discover User B")
            else:
                print("⚠️ User A cannot discover User B in regular discovery")
        
        # Test AI recommendations
        success, ai_results_a = self.test_ai_recommendations(user_a_id)
        if not success:
            print("❌ Failed to get AI recommendations for User A")
            return False
        
        print(f"AI recommendations returned {len(ai_results_a)} potential matches for User A")
        print("AI recommendations response format:")
        if ai_results_a and len(ai_results_a) > 0:
            print(f"First item type: {type(ai_results_a)}")
            print(f"First item keys: {ai_results_a[0].keys() if isinstance(ai_results_a, list) else 'Not a list'}")
            
            # Check if User B is in the AI recommendations
            user_b_found = False
            for user in ai_results_a:
                if user.get('user_id') == user_b_id:
                    user_b_found = True
                    break
            
            if user_b_found:
                print("✅ User A can find User B in AI recommendations")
            else:
                print("⚠️ User A cannot find User B in AI recommendations")
        
        # Step 4: Create a match between the users
        print("\n4️⃣ Creating a match between the users...")
        
        # User A swipes right on User B
        success, swipe_result_a = self.test_swipe(user_a_id, user_b_id, "like")
        if not success:
            print("❌ Failed when User A swiped on User B")
            return False
        
        print(f"User A swiped right on User B: {swipe_result_a}")
        
        # User B swipes right on User A
        success, swipe_result_b = self.test_swipe(user_b_id, user_a_id, "like")
        if not success:
            print("❌ Failed when User B swiped on User A")
            return False
        
        print(f"User B swiped right on User A: {swipe_result_b}")
        
        # Check if a match was created
        match_created = swipe_result_b.get('matched', False)
        match_id = swipe_result_b.get('match_id')
        
        if match_created and match_id:
            print(f"✅ Match created with ID: {match_id}")
        else:
            print("❌ No match was created")
            return False
        
        # Step 5: Test matches endpoints
        print("\n5️⃣ Testing matches endpoints...")
        
        # Get matches for User A
        success, matches_a = self.test_get_matches(user_a_id)
        if not success:
            print("❌ Failed to get matches for User A")
            return False
        
        print(f"User A has {len(matches_a)} matches")
        print("Matches response format:")
        if matches_a and len(matches_a) > 0:
            print(f"First match type: {type(matches_a)}")
            print(f"First match keys: {matches_a[0].keys() if isinstance(matches_a, list) else 'Not a list'}")
            
            # Check if the match with User B is in the results
            match_found = False
            for match in matches_a:
                if match.get('match_id') == match_id:
                    match_found = True
                    print("Match details:")
                    print(f"  Match ID: {match.get('match_id')}")
                    print(f"  User1 ID: {match.get('user1_id')}")
                    print(f"  User2 ID: {match.get('user2_id')}")
                    print(f"  Created At: {match.get('created_at')}")
                    
                    # Check if other_user field exists and has the correct data
                    if 'other_user' in match:
                        print("  Other User details:")
                        print(f"    User ID: {match['other_user'].get('user_id')}")
                        print(f"    Username: {match['other_user'].get('username')}")
                        print(f"    Display Name: {match['other_user'].get('display_name')}")
                        print(f"    Avatar URL: {match['other_user'].get('avatar_url')}")
                    else:
                        print("  ❌ other_user field is missing from the match")
                    break
            
            if match_found:
                print("✅ User A can see the match with User B")
            else:
                print("❌ User A cannot see the match with User B")
                return False
        
        # Get matches with messages for User A
        success, matches_with_messages_a = self.test_get_matches_with_messages(user_a_id)
        if not success:
            print("❌ Failed to get matches with messages for User A")
            return False
        
        print(f"User A has {len(matches_with_messages_a)} matches with messages")
        print("Matches with messages response format:")
        if matches_with_messages_a and len(matches_with_messages_a) > 0:
            print(f"First match type: {type(matches_with_messages_a)}")
            print(f"First match keys: {matches_with_messages_a[0].keys() if isinstance(matches_with_messages_a, list) else 'Not a list'}")
            
            # Check if the match with User B is in the results
            match_found = False
            for match in matches_with_messages_a:
                if match.get('match_id') == match_id:
                    match_found = True
                    print("Match with messages details:")
                    print(f"  Match ID: {match.get('match_id')}")
                    print(f"  User1 ID: {match.get('user1_id')}")
                    print(f"  User2 ID: {match.get('user2_id')}")
                    print(f"  Created At: {match.get('created_at')}")
                    
                    # Check if other_user field exists and has the correct data
                    if 'other_user' in match:
                        print("  Other User details:")
                        print(f"    User ID: {match['other_user'].get('user_id')}")
                        print(f"    Username: {match['other_user'].get('username')}")
                        print(f"    Display Name: {match['other_user'].get('display_name')}")
                        print(f"    Avatar URL: {match['other_user'].get('avatar_url')}")
                    else:
                        print("  ❌ other_user field is missing from the match")
                    
                    # Check latest message
                    if 'latest_message' in match:
                        print("  Latest Message:")
                        print(f"    Content: {match['latest_message'].get('content')}")
                        print(f"    Timestamp: {match['latest_message'].get('timestamp')}")
                        print(f"    Sender ID: {match['latest_message'].get('sender_id')}")
                    else:
                        print("  ℹ️ No messages yet")
                    break
            
            if match_found:
                print("✅ User A can see the match with User B in matches with messages")
            else:
                print("❌ User A cannot see the match with User B in matches with messages")
                return False
        
        # Step 6: Test sending and receiving messages
        print("\n6️⃣ Testing sending and receiving messages...")
        
        # User A sends a message to User B
        message_content = f"Hello from User A! {random.randint(1000, 9999)}"
        success, send_result = self.test_send_message(match_id, user_a_id, message_content)
        if not success:
            print("❌ Failed to send message from User A to User B")
            return False
        
        print(f"User A sent message to User B: {send_result}")
        
        # Get messages for the match
        success, messages = self.test_get_messages(match_id)
        if not success:
            print("❌ Failed to get messages for the match")
            return False
        
        print(f"Match has {len(messages)} messages")
        
        # Check if the message from User A is in the results
        message_found = False
        for message in messages:
            if message.get('sender_id') == user_a_id and message.get('content') == message_content:
                message_found = True
                print("Message details:")
                print(f"  Message ID: {message.get('message_id')}")
                print(f"  Match ID: {message.get('match_id')}")
                print(f"  Sender ID: {message.get('sender_id')}")
                print(f"  Content: {message.get('content')}")
                print(f"  Timestamp: {message.get('timestamp')}")
                break
        
        if message_found:
            print("✅ Message from User A to User B was found")
        else:
            print("❌ Message from User A to User B was not found")
            return False
        
        # Get matches with messages again to check if the message appears
        success, matches_with_messages_updated = self.test_get_matches_with_messages(user_a_id)
        if not success:
            print("❌ Failed to get updated matches with messages for User A")
            return False
        
        # Check if the latest message is updated
        latest_message_updated = False
        for match in matches_with_messages_updated:
            if match.get('match_id') == match_id:
                if match.get('latest_message', {}).get('content') == message_content:
                    latest_message_updated = True
                    print("✅ Latest message is updated in matches with messages")
                break
        
        if not latest_message_updated:
            print("❌ Latest message is not updated in matches with messages")
            return False
        
        print("\n✅ All discovery and matches tests passed successfully!")
        return True

if __name__ == "__main__":
    tester = Solm8DiscoveryMatchesTester()
    tester.test_discovery_and_matches()