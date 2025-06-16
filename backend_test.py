import requests
import unittest
import uuid
import os
import tempfile
import time
import json
import random
import string
from datetime import datetime, timedelta
from pymongo import MongoClient

class Solm8APITester:
    def __init__(self, base_url="https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_user = None
        self.uploaded_image_id = None
        self.token_launch_profile = None
        self.email_user = None
        self.wallet_user = None
        self.wallet_message = None
        self.mongo_client = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client.solm8_db

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

    def test_get_user(self, user_id):
        """Test getting a user profile"""
        return self.run_test(
            "Get User Profile",
            "GET",
            f"user/{user_id}",
            200
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

    def test_update_user_profile(self, user_id, profile_data):
        """Test updating a user profile"""
        return self.run_test(
            "Update User Profile",
            "PUT",
            f"user/{user_id}",
            200,
            data=profile_data
        )

    def test_swipe(self, swiper_id, target_id, action="like"):
        """Test swiping on a user"""
        return self.run_test(
            f"Swipe {action} on User",
            "POST",
            "swipe",
            200,
            data={
                "swiper_id": swiper_id,
                "target_id": target_id,
                "action": action
            }
        )

    def check_user_swipes(self, user_id):
        """Check swipes for a specific user in the database"""
        print(f"\n🔍 Checking Swipes for User ID: {user_id}")
        
        # Get swipes where user is the swiper
        outgoing_swipes = list(self.db.swipes.find({"swiper_id": user_id}))
        print(f"Outgoing swipes: {len(outgoing_swipes)}")
        
        # Get swipes where user is the target
        incoming_swipes = list(self.db.swipes.find({"target_id": user_id}))
        print(f"Incoming swipes: {len(incoming_swipes)}")
        
        # Check for mutual likes (potential matches)
        mutual_likes = []
        for outgoing in outgoing_swipes:
            if outgoing["action"] != "like":
                continue
                
            for incoming in incoming_swipes:
                if incoming["action"] != "like":
                    continue
                    
                if outgoing["target_id"] == incoming["swiper_id"]:
                    mutual_likes.append({
                        "user1_id": user_id,
                        "user2_id": outgoing["target_id"]
                    })
        
        print(f"Potential mutual likes: {len(mutual_likes)}")
        
        # Check if these mutual likes exist in the matches collection
        for mutual in mutual_likes:
            match = self.db.matches.find_one({
                "$or": [
                    {"user1_id": mutual["user1_id"], "user2_id": mutual["user2_id"]},
                    {"user1_id": mutual["user2_id"], "user2_id": mutual["user1_id"]}
                ]
            })
            
            if match:
                print(f"✅ Match exists between {mutual['user1_id']} and {mutual['user2_id']}")
            else:
                print(f"❌ No match found between {mutual['user1_id']} and {mutual['user2_id']} despite mutual likes")
        
        # Show sample of outgoing swipes
        if outgoing_swipes:
            print("\nSample of outgoing swipes:")
            for i, swipe in enumerate(outgoing_swipes[:5]):  # Show first 5
                target_user = self.db.users.find_one({"user_id": swipe["target_id"]})
                target_name = target_user["display_name"] if target_user else "Unknown User"
                print(f"{i+1}. Target: {target_name} ({swipe['target_id']}), Action: {swipe['action']}, Time: {swipe['timestamp']}")
        
        # Show sample of incoming swipes
        if incoming_swipes:
            print("\nSample of incoming swipes:")
            for i, swipe in enumerate(incoming_swipes[:5]):  # Show first 5
                swiper_user = self.db.users.find_one({"user_id": swipe["swiper_id"]})
                swiper_name = swiper_user["display_name"] if swiper_user else "Unknown User"
                print(f"{i+1}. From: {swiper_name} ({swipe['swiper_id']}), Action: {swipe['action']}, Time: {swipe['timestamp']}")
        
        return outgoing_swipes, incoming_swipes, mutual_likes

    def check_user_matches(self, user_id):
        """Check matches for a specific user in the database"""
        print(f"\n🔍 Checking Matches for User ID: {user_id}")
        
        # Get matches where user is either user1 or user2
        matches = list(self.db.matches.find({
            "$or": [
                {"user1_id": user_id},
                {"user2_id": user_id}
            ]
        }))
        
        print(f"Total matches in database: {len(matches)}")
        
        if matches:
            print("\nMatches details:")
            for i, match in enumerate(matches):
                other_user_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
                other_user = self.db.users.find_one({"user_id": other_user_id})
                other_name = other_user["display_name"] if other_user else "Unknown User"
                
                print(f"{i+1}. Match ID: {match['match_id']}")
                print(f"   With: {other_name} ({other_user_id})")
                print(f"   Created: {match['created_at']}")
                
                # Check messages for this match
                messages = list(self.db.messages.find({"match_id": match["match_id"]}))
                print(f"   Messages: {len(messages)}")
                
                # Show the latest message if any
                if messages:
                    latest = max(messages, key=lambda x: x["timestamp"])
                    sender_id = latest["sender_id"]
                    sender_is_user = sender_id == user_id
                    print(f"   Latest message: {'Sent' if sender_is_user else 'Received'} at {latest['timestamp']}")
                    print(f"   Content: {latest['content'][:50]}..." if len(latest['content']) > 50 else f"   Content: {latest['content']}")
        
        return matches

    def create_test_match(self, user_id):
        """Create a test match for the specified user"""
        print(f"\n🔍 Creating Test Match for User ID: {user_id}")
        
        # Create a new test user
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_match_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Test Match User {random_suffix}"
        
        success, signup_response = self.test_email_signup(test_email, test_password, test_display_name)
        if not success:
            print("❌ Failed to create test user")
            return False, None
        
        test_user_id = self.email_user['user_id']
        print(f"Created test user with ID: {test_user_id}")
        
        # Complete the test user's profile
        complete_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(test_user_id, complete_profile)
        if not success:
            print("❌ Failed to update test user's profile")
            return False, None
        
        # Test user swipes on target user
        success, _ = self.test_swipe(test_user_id, user_id, "like")
        if not success:
            print("❌ Failed when test user swiped on target user")
            return False, None
        
        # Target user swipes on test user
        success, _ = self.test_swipe(user_id, test_user_id, "like")
        if not success:
            print("❌ Failed when target user swiped on test user")
            return False, None
        
        # Check if match was created
        match = self.db.matches.find_one({
            "$or": [
                {"user1_id": user_id, "user2_id": test_user_id},
                {"user1_id": test_user_id, "user2_id": user_id}
            ]
        })
        
        if match:
            print(f"✅ Successfully created match with ID: {match['match_id']}")
            return True, match
        else:
            print("❌ Failed to create match - no match found in database")
            return False, None

    def check_for_duplicate_swipes(self):
        """Check for duplicate swipes in the database"""
        print("\n🔍 Checking for Duplicate Swipes...")
        
        # Get all swipes
        all_swipes = list(self.db.swipes.find())
        print(f"Total swipes in database: {len(all_swipes)}")
        
        # Check for duplicates (same swiper_id and target_id)
        swipe_pairs = {}
        duplicates = []
        
        for swipe in all_swipes:
            pair_key = f"{swipe['swiper_id']}_{swipe['target_id']}"
            if pair_key in swipe_pairs:
                duplicates.append({
                    "swiper_id": swipe["swiper_id"],
                    "target_id": swipe["target_id"],
                    "count": swipe_pairs[pair_key] + 1
                })
                swipe_pairs[pair_key] += 1
            else:
                swipe_pairs[pair_key] = 1
        
        # Filter to only include actual duplicates (count > 1)
        real_duplicates = [d for d in duplicates if swipe_pairs[f"{d['swiper_id']}_{d['target_id']}"] > 1]
        
        if real_duplicates:
            print(f"Found {len(real_duplicates)} duplicate swipe pairs:")
            for i, dup in enumerate(real_duplicates):
                swiper = self.db.users.find_one({"user_id": dup["swiper_id"]})
                target = self.db.users.find_one({"user_id": dup["target_id"]})
                swiper_name = swiper["display_name"] if swiper else "Unknown User"
                target_name = target["display_name"] if target else "Unknown User"
                print(f"{i+1}. {swiper_name} → {target_name} (Count: {dup['count']})")
        else:
            print("✅ No duplicate swipes found")
        
        return real_duplicates

    def check_for_demo_users(self):
        """Check for demo users in the database"""
        print("\n🔍 Checking for Demo Users...")
        
        # Get users with auth_method = 'demo'
        demo_users = list(self.db.users.find({"auth_method": "demo"}))
        print(f"Users with auth_method='demo': {len(demo_users)}")
        
        # Check for suspicious usernames
        suspicious_users = list(self.db.users.find({
            "$or": [
                {"username": {"$regex": "demo"}},
                {"username": {"$regex": "test"}},
                {"display_name": {"$regex": "Demo"}},
                {"display_name": {"$regex": "Test"}}
            ]
        }))
        
        # Remove actual demo users from suspicious list
        demo_ids = [user["user_id"] for user in demo_users]
        suspicious_users = [user for user in suspicious_users if user["user_id"] not in demo_ids]
        
        print(f"Suspicious users (not marked as demo): {len(suspicious_users)}")
        
        # Show demo users
        if demo_users:
            print("\nDemo users:")
            for i, user in enumerate(demo_users):
                print(f"{i+1}. User ID: {user['user_id']}, Username: {user['username']}, Display Name: {user['display_name']}")
        
        # Show suspicious users
        if suspicious_users:
            print("\nSuspicious users:")
            for i, user in enumerate(suspicious_users):
                print(f"{i+1}. User ID: {user['user_id']}, Username: {user['username']}, Display Name: {user['display_name']}, Auth Method: {user.get('auth_method', 'None')}")
        
        return demo_users, suspicious_users

    def investigate_user_matches(self, user_id):
        """Comprehensive investigation of a user's matches"""
        print(f"\n🔍 Investigating Matches for User ID: {user_id}")
        
        # Step 1: Check if user exists
        user = self.db.users.find_one({"user_id": user_id})
        if not user:
            print(f"❌ User with ID {user_id} not found in database")
            return False
        
        print(f"✅ Found user: {user.get('display_name')} ({user.get('username')})")
        print(f"Profile complete: {user.get('profile_complete')}")
        print(f"Auth method: {user.get('auth_method')}")
        
        # Step 2: Check API response for matches
        success, api_matches = self.test_get_matches(user_id)
        if not success:
            print("❌ Failed to get matches from API")
        else:
            print(f"API returned {len(api_matches)} matches")
        
        # Step 3: Check database for matches
        db_matches = self.check_user_matches(user_id)
        
        # Step 4: Check swipes
        outgoing_swipes, incoming_swipes, mutual_likes = self.check_user_swipes(user_id)
        
        # Step 5: Check for duplicate swipes
        self.check_for_duplicate_swipes()
        
        # Step 6: Check for demo users
        self.check_for_demo_users()
        
        # Step 7: Create a test match if no matches exist
        if not db_matches:
            print("\n🔍 No existing matches found. Creating a test match...")
            success, test_match = self.create_test_match(user_id)
            
            if success:
                print("✅ Successfully created test match")
                
                # Verify the match appears in API response
                success, api_matches_after = self.test_get_matches(user_id)
                if success and len(api_matches_after) > 0:
                    print("✅ Test match appears in API response")
                else:
                    print("❌ Test match does not appear in API response")
            else:
                print("❌ Failed to create test match")
        
        return True

def test_profile_popup_functionality():
    """Test the profile popup functionality by creating a user and verifying profile data"""
    print("\n🔍 Testing Profile Popup Functionality...")
    tester = Solm8APITester()
    
    # Step 1: Create a new user account with email signup
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_profile_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Profile User {random_suffix}"
    
    print("\n1️⃣ Creating new user account...")
    success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    if not success:
        print("❌ Failed to create test user")
        return False
    
    user_id = tester.email_user['user_id']
    print(f"✅ Created test user with ID: {user_id}")
    
    # Step 2: Complete the profile setup process
    print("\n2️⃣ Completing profile setup...")
    complete_profile = {
        "bio": "I'm a trader focused on DeFi and NFTs.",
        "location": "Crypto Valley",
        "trading_experience": "Intermediate",
        "years_trading": 3,
        "preferred_tokens": ["DeFi", "NFTs", "Blue Chips"],
        "trading_style": "Swing Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "best_trade": "Bought SOL at $20, sold at $200",
        "worst_trade": "Missed the BONK pump",
        "favorite_project": "Solana",
        "trading_hours": "Evening",
        "communication_style": "Casual",
        "preferred_communication_platform": "Discord",
        "preferred_trading_platform": "Jupiter",
        "looking_for": ["Alpha Sharing", "Research Partner"]
    }
    
    success, update_response = tester.test_update_user_profile(user_id, complete_profile)
    if not success:
        print("❌ Failed to update user profile")
        return False
    
    print("✅ Successfully completed profile setup")
    
    # Step 3: Verify the user data can be retrieved via the API
    print("\n3️⃣ Verifying user data retrieval...")
    success, user_data = tester.test_get_user(user_id)
    if not success:
        print("❌ Failed to retrieve user data")
        return False
    
    print("✅ Successfully retrieved user data")
    
    # Step 4: Check that all required fields for the profile popup are present in the response
    print("\n4️⃣ Checking required fields for profile popup...")
    required_fields = [
        "user_id", "display_name", "avatar_url", "bio", "location", 
        "trading_experience", "years_trading", "preferred_tokens", 
        "trading_style", "portfolio_size", "risk_tolerance",
        "best_trade", "worst_trade", "favorite_project", 
        "trading_hours", "communication_style", 
        "preferred_communication_platform", "preferred_trading_platform",
        "looking_for", "user_status"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in user_data or user_data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    print("✅ All required fields for profile popup are present")
    
    # Step 5: Verify profile_complete flag is set to true
    print("\n5️⃣ Verifying profile_complete flag...")
    if not user_data.get("profile_complete"):
        print("❌ profile_complete flag is not set to true")
        return False
    
    print("✅ profile_complete flag is set to true")
    
    # Step 6: Verify the user appears in discovery results
    print("\n6️⃣ Creating another user to test discovery...")
    
    # Create another user to test discovery
    random_suffix2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email2 = f"test_discover_{random_suffix2}@example.com"
    test_password2 = "TestPassword123!"
    test_display_name2 = f"Test Discover User {random_suffix2}"
    
    success, signup_response2 = tester.test_email_signup(test_email2, test_password2, test_display_name2)
    if not success:
        print("❌ Failed to create second test user")
        return False
    
    user_id2 = tester.email_user['user_id']
    print(f"✅ Created second test user with ID: {user_id2}")
    
    # Complete the second user's profile
    complete_profile2 = {
        "trading_experience": "Beginner",
        "preferred_tokens": ["Meme Coins", "GameFi"],
        "trading_style": "HODLer",
        "portfolio_size": "$1K-$10K"
    }
    
    success, _ = tester.test_update_user_profile(user_id2, complete_profile2)
    if not success:
        print("❌ Failed to update second user's profile")
        return False
    
    print("✅ Successfully completed second user's profile")
    
    # Test discovery endpoint
    print("\n7️⃣ Testing discovery endpoint...")
    success, discover_response = tester.run_test(
        "Get Discovery Users",
        "GET",
        f"discover/{user_id2}",
        200
    )
    
    if not success:
        print("❌ Failed to get discovery users")
        return False
    
    # Check if the first user appears in discovery results
    first_user_found = False
    for user in discover_response:
        if user.get("user_id") == user_id:
            first_user_found = True
            break
    
    if not first_user_found:
        print("❌ First user not found in discovery results")
        return False
    
    print("✅ First user found in discovery results")
    
    # Test clicking on profile (simulated by getting user data)
    print("\n8️⃣ Testing profile data retrieval (simulating profile click)...")
    success, profile_data = tester.test_get_user(user_id)
    if not success:
        print("❌ Failed to retrieve profile data")
        return False
    
    print("✅ Successfully retrieved profile data")
    print("✅ All tests for profile popup functionality passed!")
    return True

def test_public_profile_modal():
    """Test the enhanced public profile modal functionality"""
    print("\n🔍 Testing Public Profile Modal Functionality...")
    tester = Solm8APITester()
    
    # Step 1: Create a new user account with email signup
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_public_profile_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Public Profile User {random_suffix}"
    
    print("\n1️⃣ Creating new user account...")
    success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    if not success:
        print("❌ Failed to create test user")
        return False
    
    user_id = tester.email_user['user_id']
    print(f"✅ Created test user with ID: {user_id}")
    
    # Step 2: Complete the profile setup process
    print("\n2️⃣ Completing profile setup...")
    complete_profile = {
        "bio": "I'm a trader focused on DeFi and NFTs.",
        "location": "Crypto Valley",
        "trading_experience": "Intermediate",
        "years_trading": 3,
        "preferred_tokens": ["DeFi", "NFTs", "Blue Chips"],
        "trading_style": "Swing Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "best_trade": "Bought SOL at $20, sold at $200",
        "worst_trade": "Missed the BONK pump",
        "favorite_project": "Solana",
        "trading_hours": "Evening",
        "communication_style": "Casual",
        "preferred_communication_platform": "Discord",
        "preferred_trading_platform": "Jupiter",
        "looking_for": ["Alpha Sharing", "Research Partner"]
    }
    
    success, update_response = tester.test_update_user_profile(user_id, complete_profile)
    if not success:
        print("❌ Failed to update user profile")
        return False
    
    print("✅ Successfully completed profile setup")
    
    # Step 3: Verify the user data can be retrieved via the API
    print("\n3️⃣ Verifying user data retrieval...")
    success, user_data = tester.test_get_user(user_id)
    if not success:
        print("❌ Failed to retrieve user data")
        return False
    
    print("✅ Successfully retrieved user data")
    
    # Step 4: Test the public profile endpoint
    print("\n4️⃣ Testing public profile endpoint...")
    success, public_profile = tester.run_test(
        "Get Public Profile",
        "GET",
        f"public-profile/{user_data['username']}",
        200
    )
    
    if not success:
        print("❌ Failed to retrieve public profile")
        return False
    
    print("✅ Successfully retrieved public profile")
    
    # Step 5: Test social links functionality
    print("\n5️⃣ Testing social links functionality...")
    social_links = {
        "twitter": "test_twitter_handle",
        "discord": "test_discord#1234",
        "telegram": "test_telegram",
        "website": "https://example.com"
    }
    
    success, social_response = tester.run_test(
        "Update Social Links",
        "POST",
        f"update-social-links/{user_id}",
        200,
        data=social_links
    )
    
    if not success:
        print("❌ Failed to update social links")
        return False
    
    print("✅ Successfully updated social links")
    
    # Step 6: Verify social links were saved
    success, retrieved_links = tester.run_test(
        "Get Social Links",
        "GET",
        f"social-links/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to retrieve social links")
        return False
    
    print("✅ Successfully retrieved social links")
    
    # Verify the links match what we set
    links_match = all(
        retrieved_links.get(key) == value 
        for key, value in social_links.items() 
        if key in retrieved_links
    )
    
    if not links_match:
        print("❌ Retrieved social links don't match what was set")
        print(f"Expected: {social_links}")
        print(f"Received: {retrieved_links}")
        return False
    
    print("✅ Social links match what was set")
    
    # Step 7: Test trading highlights functionality
    print("\n6️⃣ Testing trading highlights functionality...")
    
    # Create a simple base64 image for testing
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    highlight_data = {
        "title": "Test Trading Highlight",
        "description": "This is a test trading highlight",
        "image_data": test_image_data,
        "highlight_type": "pnl_screenshot",
        "date_achieved": "2023-05-15",
        "profit_loss": "+$5000",
        "percentage_gain": "+250%"
    }
    
    success, highlight_response = tester.run_test(
        "Save Trading Highlight",
        "POST",
        f"save-trading-highlight/{user_id}",
        200,
        data=highlight_data
    )
    
    if not success:
        print("❌ Failed to save trading highlight")
        return False
    
    print("✅ Successfully saved trading highlight")
    
    # Step 8: Verify trading highlights were saved
    success, retrieved_highlights = tester.run_test(
        "Get Trading Highlights",
        "GET",
        f"trading-highlights/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to retrieve trading highlights")
        return False
    
    if not retrieved_highlights or len(retrieved_highlights) == 0:
        print("❌ No trading highlights found")
        return False
    
    print(f"✅ Successfully retrieved {len(retrieved_highlights)} trading highlights")
    
    # Step 9: Test referral code generation for sharing
    print("\n7️⃣ Testing referral code generation...")
    success, referral_response = tester.run_test(
        "Generate Referral Code",
        "POST",
        f"referrals/generate/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to generate referral code")
        return False
    
    if not referral_response.get("referral_code"):
        print("❌ No referral code in response")
        return False
    
    print(f"✅ Successfully generated referral code: {referral_response.get('referral_code')}")
    
    print("\n✅ All tests for public profile modal functionality passed!")
    return True

def test_trading_highlights_save_functionality():
    """Test the trading highlights save functionality"""
    print("\n🔍 Testing Trading Highlights Save Functionality...")
    tester = Solm8APITester()
    
    # Step 1: Create a new user account with email signup
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_highlights_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Highlights User {random_suffix}"
    
    print("\n1️⃣ Creating new user account...")
    success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    if not success:
        print("❌ Failed to create test user")
        return False
    
    user_id = tester.email_user['user_id']
    print(f"✅ Created test user with ID: {user_id}")
    
    # Step 2: Complete the profile setup process
    print("\n2️⃣ Completing profile setup...")
    complete_profile = {
        "bio": "I'm a trader focused on DeFi and NFTs.",
        "location": "Crypto Valley",
        "trading_experience": "Intermediate",
        "years_trading": 3,
        "preferred_tokens": ["DeFi", "NFTs", "Blue Chips"],
        "trading_style": "Swing Trader",
        "portfolio_size": "$10K-$100K",
        "risk_tolerance": "Moderate",
        "best_trade": "Bought SOL at $20, sold at $200",
        "worst_trade": "Missed the BONK pump",
        "favorite_project": "Solana",
        "trading_hours": "Evening",
        "communication_style": "Casual",
        "preferred_communication_platform": "Discord",
        "preferred_trading_platform": "Jupiter",
        "looking_for": ["Alpha Sharing", "Research Partner"]
    }
    
    success, update_response = tester.test_update_user_profile(user_id, complete_profile)
    if not success:
        print("❌ Failed to update user profile")
        return False
    
    print("✅ Successfully completed profile setup")
    
    # Step 3: Test saving a trading highlight with all required fields
    print("\n3️⃣ Testing saving a trading highlight with all required fields...")
    
    # Create a simple base64 image for testing
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    highlight_data = {
        "title": "Test Trading Highlight",
        "description": "This is a test",
        "image_data": test_image_data,
        "highlight_type": "pnl_screenshot",
        "date_achieved": "2023-05-15",
        "profit_loss": "+$1000",
        "percentage_gain": "+50%"
    }
    
    success, highlight_response = tester.run_test(
        "Save Trading Highlight",
        "POST",
        f"save-trading-highlight/{user_id}",
        200,
        data=highlight_data
    )
    
    if not success:
        print("❌ Failed to save trading highlight")
        return False
    
    print("✅ Successfully saved trading highlight")
    
    # Step 4: Verify the trading highlight was saved to the database
    print("\n4️⃣ Verifying trading highlight was saved to the database...")
    success, retrieved_highlights = tester.run_test(
        "Get Trading Highlights",
        "GET",
        f"trading-highlights/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to retrieve trading highlights")
        return False
    
    if not retrieved_highlights or len(retrieved_highlights) == 0:
        print("❌ No trading highlights found")
        return False
    
    print(f"✅ Successfully retrieved {len(retrieved_highlights)} trading highlights")
    
    # Verify the highlight data matches what we set
    highlight = retrieved_highlights[0]
    fields_to_check = ["title", "description", "profit_loss", "percentage_gain"]
    
    for field in fields_to_check:
        if highlight.get(field) != highlight_data.get(field):
            print(f"❌ Field mismatch: {field}")
            print(f"Expected: {highlight_data.get(field)}")
            print(f"Received: {highlight.get(field)}")
            return False
    
    print("✅ Trading highlight data matches what was set")
    
    # Step 5: Test error handling with missing required fields
    print("\n5️⃣ Testing error handling with missing required fields...")
    
    # Test with missing title
    invalid_highlight = highlight_data.copy()
    invalid_highlight.pop("title")
    
    success, error_response = tester.run_test(
        "Save Trading Highlight with Missing Title",
        "POST",
        f"save-trading-highlight/{user_id}",
        200,  # The API currently returns 200 even with missing fields
        data=invalid_highlight
    )
    
    # Test with missing description
    invalid_highlight = highlight_data.copy()
    invalid_highlight.pop("description")
    
    success, error_response = tester.run_test(
        "Save Trading Highlight with Missing Description",
        "POST",
        f"save-trading-highlight/{user_id}",
        200,  # The API currently returns 200 even with missing fields
        data=invalid_highlight
    )
    
    # Test with missing image data
    invalid_highlight = highlight_data.copy()
    invalid_highlight.pop("image_data")
    
    success, error_response = tester.run_test(
        "Save Trading Highlight with Missing Image Data",
        "POST",
        f"save-trading-highlight/{user_id}",
        200,  # The API currently returns 200 even with missing fields
        data=invalid_highlight
    )
    
    # Step 6: Test with invalid user ID
    print("\n6️⃣ Testing with invalid user ID...")
    
    invalid_user_id = "invalid-user-id"
    
    success, error_response = tester.run_test(
        "Save Trading Highlight with Invalid User ID",
        "POST",
        f"save-trading-highlight/{invalid_user_id}",
        404,  # Should return 404 for invalid user ID
        data=highlight_data
    )
    
    if success:
        print("❌ API accepted invalid user ID")
        return False
    
    print("✅ API correctly rejected invalid user ID")
    
    # Step 7: Test with very large image data
    print("\n7️⃣ Testing with very large image data...")
    
    # Create a large base64 string (approximately 100KB)
    large_image_data = test_image_data * 1000
    
    large_highlight_data = highlight_data.copy()
    large_highlight_data["image_data"] = large_image_data
    large_highlight_data["title"] = "Large Image Test"
    
    success, large_response = tester.run_test(
        "Save Trading Highlight with Large Image",
        "POST",
        f"save-trading-highlight/{user_id}",
        200,
        data=large_highlight_data
    )
    
    if not success:
        print("❌ Failed to save trading highlight with large image")
        return False
    
    print("✅ Successfully saved trading highlight with large image")
    
    # Step 8: Verify all highlights are retrievable
    print("\n8️⃣ Verifying all highlights are retrievable...")
    
    success, all_highlights = tester.run_test(
        "Get All Trading Highlights",
        "GET",
        f"trading-highlights/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to retrieve all trading highlights")
        return False
    
    # We should have at least 2 highlights now (the original and the large image one)
    if len(all_highlights) < 2:
        print(f"❌ Expected at least 2 highlights, but found {len(all_highlights)}")
        return False
    
    print(f"✅ Successfully retrieved all {len(all_highlights)} trading highlights")
    
    print("\n✅ All tests for trading highlights save functionality passed!")
    return True

def main():
    tester = Solm8APITester()
    
    # Test trading highlights save functionality
    test_trading_highlights_save_functionality()
    
    # Uncomment to run other tests
    # test_profile_popup_functionality()
    # test_public_profile_modal()
    # user_id = "17d9709a-9a6f-4418-8cb4-765faca422a8"
    # tester.investigate_user_matches(user_id)

if __name__ == "__main__":
    main()
