import requests
import unittest
import uuid
import os
import tempfile
import time
import json
import random
import string
from datetime import datetime
from pymongo import MongoClient

class Solm8APITester:
    def __init__(self, base_url="https://ad8c686b-31d6-433d-aa09-b025124c7c61.preview.emergentagent.com"):
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

    def test_health_check(self):
        """Test the health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )

    def test_create_demo_user(self):
        """Test creating a demo user"""
        success, response = self.run_test(
            "Create Demo User",
            "POST",
            "create-demo-user",
            200
        )
        if success:
            self.demo_user = response
            print(f"Created demo user: {self.demo_user['username']}")
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

    def check_actual_users_in_database(self):
        """Check actual users in the database"""
        print("\n🔍 Checking Actual Users in Database...")
        
        # Get all users
        users = list(self.db.users.find())
        total_users = len(users)
        
        # Count users by auth method
        auth_methods = {}
        for user in users:
            auth_method = user.get('auth_method', 'none')
            auth_methods[auth_method] = auth_methods.get(auth_method, 0) + 1
        
        # Count users with complete profiles
        complete_profiles = sum(1 for user in users if user.get('profile_complete', False))
        
        print(f"Total users in database: {total_users}")
        print(f"Users by auth method: {auth_methods}")
        print(f"Users with complete profiles: {complete_profiles}")
        
        # Get email users (non-demo)
        email_users = [user for user in users if user.get('auth_method') == 'email']
        wallet_users = [user for user in users if user.get('auth_method') == 'wallet']
        
        print(f"\nEmail users (non-demo): {len(email_users)}")
        print(f"Wallet users: {len(wallet_users)}")
        
        # Show profile completion status for email users
        print("\nProfile completion status for email users:")
        for user in email_users:
            print(f"User ID: {user.get('user_id')}, Email: {user.get('email')}, Profile Complete: {user.get('profile_complete')}")
            print(f"  Trading Experience: '{user.get('trading_experience')}'")
            print(f"  Preferred Tokens: {user.get('preferred_tokens')}")
            print(f"  Trading Style: '{user.get('trading_style')}'")
            print(f"  Portfolio Size: '{user.get('portfolio_size')}'")
            print()
        
        # Return user IDs of users with complete profiles
        return [user.get('user_id') for user in users if user.get('profile_complete', False)]

    def test_discovery_with_real_users(self, user_ids=None, limit=5):
        """Test discovery with real user IDs from the database"""
        print("\n🔍 Testing Discovery with Real User IDs...")
        
        if not user_ids:
            # Get users with complete profiles
            user_ids = [user.get('user_id') for user in self.db.users.find({"profile_complete": True}).limit(limit)]
        
        if not user_ids:
            print("❌ No users with complete profiles found in the database")
            return False
        
        results = []
        
        for user_id in user_ids[:limit]:  # Limit to 5 users for testing
            print(f"\nTesting discovery for user ID: {user_id}")
            
            # Get user details
            success, user_data = self.test_get_user(user_id)
            if not success:
                print(f"❌ Failed to get user data for ID: {user_id}")
                continue
            
            print(f"User: {user_data.get('username')}, Profile Complete: {user_data.get('profile_complete')}")
            
            # Test regular discovery
            success, discover_results = self.test_discover_users(user_id)
            if not success:
                print(f"❌ Failed to get discovery results for user ID: {user_id}")
                continue
            
            print(f"Discovery returned {len(discover_results)} potential matches")
            
            # Show the first 3 matches
            if discover_results and len(discover_results) > 0:
                print("\nSample of discovery results:")
                for i, match in enumerate(discover_results[:3]):
                    print(f"{i+1}. User ID: {match.get('user_id')}, Username: {match.get('username')}")
                    print(f"   Profile Complete: {match.get('profile_complete')}")
                    print(f"   Trading Experience: '{match.get('trading_experience')}'")
                    print(f"   Last Activity: {match.get('last_activity')}")
            
            # Test AI recommendations
            try:
                success, ai_results = self.test_ai_recommendations(user_id)
                if not success:
                    print(f"❌ Failed to get AI recommendations for user ID: {user_id}")
                    ai_count = 0
                else:
                    ai_count = len(ai_results)
                    print(f"AI recommendations returned {ai_count} potential matches")
                    
                    # Show the first 3 AI recommendations
                    if ai_results and len(ai_results) > 0:
                        print("\nSample of AI recommendations:")
                        for i, match in enumerate(ai_results[:3]):
                            print(f"{i+1}. User ID: {match.get('user_id')}, Username: {match.get('username')}")
                            print(f"   Compatibility: {match.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                            print(f"   Profile Complete: {match.get('profile_complete')}")
            except Exception as e:
                print(f"❌ Error getting AI recommendations: {str(e)}")
                ai_count = 0
            
            results.append({
                "user_id": user_id,
                "username": user_data.get('username'),
                "profile_complete": user_data.get('profile_complete'),
                "discover_count": len(discover_results),
                "ai_recommendations_count": ai_count
            })
        
        print("\nDiscovery Test Results Summary:")
        for result in results:
            print(f"User: {result['username']}, Profile Complete: {result['profile_complete']}, Discovery: {result['discover_count']}, AI Recommendations: {result['ai_recommendations_count']}")
        
        return results

    def test_profile_update_process(self, user_id=None):
        """Test if the profile update endpoint is setting profile_complete correctly"""
        print("\n🔍 Testing Profile Update Process...")
        
        if not user_id:
            # Create a new test user
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            test_email = f"test_{random_suffix}@example.com"
            test_password = "TestPassword123!"
            test_display_name = f"Test User {random_suffix}"
            
            success, signup_response = self.test_email_signup(test_email, test_password, test_display_name)
            if not success:
                print("❌ Email signup failed, stopping test")
                return False
            
            user_id = self.email_user['user_id']
        
        # Get initial user profile
        success, initial_profile = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get initial user profile")
            return False
        
        print(f"Initial profile_complete: {initial_profile.get('profile_complete')}")
        
        # Test Case 1: Update with incomplete profile (missing trading_experience)
        incomplete_profile = {
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_id, incomplete_profile)
        if not success:
            print("❌ Failed to update user profile with incomplete data")
            return False
        
        success, updated_profile = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get updated user profile")
            return False
        
        print(f"After incomplete update, profile_complete: {updated_profile.get('profile_complete')}")
        
        # Test Case 2: Update with complete profile
        complete_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_id, complete_profile)
        if not success:
            print("❌ Failed to update user profile with complete data")
            return False
        
        success, updated_profile = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get updated user profile")
            return False
        
        print(f"After complete update, profile_complete: {updated_profile.get('profile_complete')}")
        
        # Test Case 3: Update with empty preferred_tokens
        empty_tokens_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": [],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_id, empty_tokens_profile)
        if not success:
            print("❌ Failed to update user profile with empty tokens")
            return False
        
        success, updated_profile = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get updated user profile")
            return False
        
        print(f"After empty tokens update, profile_complete: {updated_profile.get('profile_complete')}")
        
        # Test Case 4: Update with empty string for trading_style
        empty_style_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_id, empty_style_profile)
        if not success:
            print("❌ Failed to update user profile with empty trading style")
            return False
        
        success, updated_profile = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get updated user profile")
            return False
        
        print(f"After empty style update, profile_complete: {updated_profile.get('profile_complete')}")
        
        # Test Case 5: Update back to complete profile
        success, _ = self.test_update_user_profile(user_id, complete_profile)
        if not success:
            print("❌ Failed to update user profile back to complete")
            return False
        
        success, final_profile = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get final user profile")
            return False
        
        print(f"Final profile_complete: {final_profile.get('profile_complete')}")
        
        # Verify profile completion logic is working correctly
        if not final_profile.get('profile_complete'):
            print("❌ Profile completion logic failed - profile should be marked as complete")
            return False
        else:
            print("✅ Profile completion logic is working correctly")
        
        return True

    def test_discovery_filters(self):
        """Test discovery filters to ensure no hidden filters are blocking users"""
        print("\n🔍 Testing Discovery Filters...")
        
        # Create two test users with complete profiles
        print("Creating two test users with complete profiles...")
        
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
        
        user_b_id = self.email_user['user_id']
        
        print(f"Created User A (ID: {user_a_id}) and User B (ID: {user_b_id})")
        
        # Complete profiles for both users
        complete_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_a_id, complete_profile)
        if not success:
            print("❌ Failed to update User A's profile")
            return False
        
        success, _ = self.test_update_user_profile(user_b_id, complete_profile)
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
        
        # Test if User A can discover User B
        print("\nTesting if User A can discover User B...")
        success, discover_results_a = self.test_discover_users(user_a_id)
        if not success:
            print("❌ Failed to get discovery results for User A")
            return False
        
        user_b_found = False
        for user in discover_results_a:
            if user.get('user_id') == user_b_id:
                user_b_found = True
                break
        
        if user_b_found:
            print("✅ User A can discover User B")
        else:
            print("❌ User A cannot discover User B")
            print(f"Discovery returned {len(discover_results_a)} users, but User B was not among them")
        
        # Test if User B can discover User A
        print("\nTesting if User B can discover User A...")
        success, discover_results_b = self.test_discover_users(user_b_id)
        if not success:
            print("❌ Failed to get discovery results for User B")
            return False
        
        user_a_found = False
        for user in discover_results_b:
            if user.get('user_id') == user_a_id:
                user_a_found = True
                break
        
        if user_a_found:
            print("✅ User B can discover User A")
        else:
            print("❌ User B cannot discover User A")
            print(f"Discovery returned {len(discover_results_b)} users, but User A was not among them")
        
        # Test swipe history filtering
        if user_b_found:
            print("\nTesting swipe history filtering...")
            
            # User A swipes on User B
            success, _ = self.run_test(
                "User A swipes on User B",
                "POST",
                "swipe",
                200,
                data={
                    "swiper_id": user_a_id,
                    "target_id": user_b_id,
                    "action": "like"
                }
            )
            
            if not success:
                print("❌ Failed when User A swiped on User B")
                return False
            
            # Check if User A can still see User B in discovery
            success, discover_results_a_after = self.test_discover_users(user_a_id)
            if not success:
                print("❌ Failed to get discovery results for User A after swiping")
                return False
            
            user_b_found_after = False
            for user in discover_results_a_after:
                if user.get('user_id') == user_b_id:
                    user_b_found_after = True
                    break
            
            if not user_b_found_after:
                print("✅ User A cannot discover User B after swiping (as expected)")
            else:
                print("❌ User A can still discover User B after swiping (unexpected)")
        
        # Test sorting by last_activity
        print("\nTesting sorting by last_activity...")
        
        # Update User B's last_activity to be more recent
        success, _ = self.run_test(
            "Update User B's activity",
            "POST",
            f"user/{user_b_id}/update-activity",
            200
        )
        
        if not success:
            print("❌ Failed to update User B's activity")
            return False
        
        # Create a third user who will have the most recent activity
        random_suffix_c = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_c = f"test_c_{random_suffix_c}@example.com"
        display_name_c = f"Test User C {random_suffix_c}"
        
        success, signup_response_c = self.test_email_signup(email_c, "TestPassword123!", display_name_c)
        if not success:
            print("❌ Failed to create User C")
            return False
        
        user_c_id = self.email_user['user_id']
        
        # Complete profile for User C
        success, _ = self.test_update_user_profile(user_c_id, complete_profile)
        if not success:
            print("❌ Failed to update User C's profile")
            return False
        
        # Update User C's activity to be the most recent
        time.sleep(1)  # Ensure timestamp difference
        success, _ = self.run_test(
            "Update User C's activity",
            "POST",
            f"user/{user_c_id}/update-activity",
            200
        )
        
        if not success:
            print("❌ Failed to update User C's activity")
            return False
        
        # Check discovery results for a new user to see the order
        random_suffix_d = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_d = f"test_d_{random_suffix_d}@example.com"
        display_name_d = f"Test User D {random_suffix_d}"
        
        success, signup_response_d = self.test_email_signup(email_d, "TestPassword123!", display_name_d)
        if not success:
            print("❌ Failed to create User D")
            return False
        
        user_d_id = self.email_user['user_id']
        
        # Complete profile for User D
        success, _ = self.test_update_user_profile(user_d_id, complete_profile)
        if not success:
            print("❌ Failed to update User D's profile")
            return False
        
        # Get discovery results for User D
        success, discover_results_d = self.test_discover_users(user_d_id)
        if not success:
            print("❌ Failed to get discovery results for User D")
            return False
        
        print("\nDiscovery results for User D (should be sorted by last_activity):")
        for i, user in enumerate(discover_results_d[:5]):  # Show first 5 results
            print(f"{i+1}. User ID: {user.get('user_id')}, Username: {user.get('username')}, Last Activity: {user.get('last_activity')}")
        
        # Check if User C appears before User B and User A in the results
        user_positions = {}
        for i, user in enumerate(discover_results_d):
            if user.get('user_id') == user_a_id:
                user_positions['A'] = i
            elif user.get('user_id') == user_b_id:
                user_positions['B'] = i
            elif user.get('user_id') == user_c_id:
                user_positions['C'] = i
        
        if 'C' in user_positions and 'B' in user_positions and user_positions['C'] < user_positions['B']:
            print("✅ User C appears before User B in discovery results (correct sorting)")
        elif 'C' in user_positions and 'B' in user_positions:
            print("❌ User C appears after User B in discovery results (incorrect sorting)")
        else:
            print("⚠️ Could not verify sorting - one or both users not found in results")
        
        return True

    def live_debug_session(self):
        """Run a live debug session with test users"""
        print("\n🔍 Running Live Debug Session...")
        
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
        
        user_b_id = self.email_user['user_id']
        
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
        
        # Step 3: Test immediate discovery
        print("\n3️⃣ Testing immediate discovery...")
        
        # Test if User A can discover User B
        print("Testing if User A can discover User B...")
        success, discover_results_a = self.test_discover_users(user_a_id)
        if not success:
            print("❌ Failed to get discovery results for User A")
            return False
        
        user_b_found = False
        for user in discover_results_a:
            if user.get('user_id') == user_b_id:
                user_b_found = True
                break
        
        if user_b_found:
            print("✅ User A can discover User B immediately after profile completion")
        else:
            print("❌ User A cannot discover User B")
            print(f"Discovery returned {len(discover_results_a)} users, but User B was not among them")
        
        # Test if User B can discover User A
        print("\nTesting if User B can discover User A...")
        success, discover_results_b = self.test_discover_users(user_b_id)
        if not success:
            print("❌ Failed to get discovery results for User B")
            return False
        
        user_a_found = False
        for user in discover_results_b:
            if user.get('user_id') == user_a_id:
                user_a_found = True
                break
        
        if user_a_found:
            print("✅ User B can discover User A immediately after profile completion")
        else:
            print("❌ User B cannot discover User A")
            print(f"Discovery returned {len(discover_results_b)} users, but User A was not among them")
        
        # Step 4: Compare with real user data
        print("\n4️⃣ Comparing with real user data...")
        
        # Get real users with complete profiles
        real_users = list(self.db.users.find({
            "auth_method": {"$in": ["email", "wallet"]},
            "profile_complete": True
        }).limit(5))
        
        if not real_users:
            print("No real users with complete profiles found for comparison")
            return True
        
        print(f"Found {len(real_users)} real users with complete profiles for comparison")
        
        # Check if test users can discover real users
        print("\nChecking if test users can discover real users...")
        
        real_user_ids = [user.get('user_id') for user in real_users]
        
        success, discover_results_a = self.test_discover_users(user_a_id)
        if not success:
            print("❌ Failed to get discovery results for User A")
            return False
        
        real_users_found_by_a = []
        for user in discover_results_a:
            if user.get('user_id') in real_user_ids:
                real_users_found_by_a.append(user.get('user_id'))
        
        print(f"User A found {len(real_users_found_by_a)} real users in discovery")
        
        # Check if real users can discover test users
        if real_users:
            print("\nChecking if real users can discover test users...")
            
            real_user_id = real_users[0].get('user_id')
            
            success, discover_results_real = self.test_discover_users(real_user_id)
            if not success:
                print(f"❌ Failed to get discovery results for real user {real_user_id}")
                return False
            
            test_users_found = []
            for user in discover_results_real:
                if user.get('user_id') in [user_a_id, user_b_id]:
                    test_users_found.append(user.get('user_id'))
            
            print(f"Real user found {len(test_users_found)} test users in discovery")
            if test_users_found:
                print(f"Test users found: {', '.join(test_users_found)}")
        
        return True

    def run_discovery_debug_tests(self):
        """Run all tests related to debugging discovery issues"""
        print("🚀 Starting Solm8 Discovery Debug Tests")
        
        # Step 1: Check actual users in database
        print("\n===== STEP 1: CHECK ACTUAL USERS IN DATABASE =====")
        complete_user_ids = self.check_actual_users_in_database()
        
        # Step 2: Test discovery with real user IDs
        print("\n===== STEP 2: TEST DISCOVERY WITH REAL USER IDS =====")
        if complete_user_ids:
            self.test_discovery_with_real_users(complete_user_ids)
        
        # Step 3: Debug profile update process
        print("\n===== STEP 3: DEBUG PROFILE UPDATE PROCESS =====")
        self.test_profile_update_process()
        
        # Step 4: Test discovery filters
        print("\n===== STEP 4: TEST DISCOVERY FILTERS =====")
        self.test_discovery_filters()
        
        # Step 5: Live debug session
        print("\n===== STEP 5: LIVE DEBUG SESSION =====")
        self.live_debug_session()
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = Solm8APITester()
    tester.run_discovery_debug_tests()
