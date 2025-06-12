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
    def __init__(self, base_url="https://8134b81b-ad13-497e-ba8a-ecdf0793b0b4.preview.emergentagent.com"):
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

    def test_session_validation(self):
        """Test session validation by creating a user and verifying the session persists"""
        print("\n🔍 Testing Session Validation...")
        
        # Step 1: Create a new test user
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_session_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Test Session User {random_suffix}"
        
        success, signup_response = self.test_email_signup(test_email, test_password, test_display_name)
        if not success:
            print("❌ Email signup failed, stopping test")
            return False
        
        user_id = self.email_user['user_id']
        print(f"Created test user with ID: {user_id}")
        
        # Step 2: Verify user exists via /api/user/{user_id} endpoint
        success, user_data = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get user data - session validation failed")
            return False
        
        print(f"✅ Successfully retrieved user data for ID: {user_id}")
        print(f"Username: {user_data.get('username')}")
        print(f"Email: {user_data.get('email')}")
        
        # Step 3: Simulate a page refresh by making another request to get user data
        print("\nSimulating page refresh...")
        success, refreshed_user_data = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get user data after simulated refresh - session validation failed")
            return False
        
        print(f"✅ Successfully retrieved user data after simulated refresh")
        
        # Step 4: Verify the data is consistent
        if user_data.get('user_id') == refreshed_user_data.get('user_id') and \
           user_data.get('email') == refreshed_user_data.get('email'):
            print("✅ User session data is consistent after refresh")
        else:
            print("❌ User session data is inconsistent after refresh")
            return False
        
        # Step 5: Test updating user activity
        success, _ = self.run_test(
            "Update User Activity",
            "POST",
            f"user/{user_id}/update-activity",
            200
        )
        
        if not success:
            print("❌ Failed to update user activity")
            return False
        
        print("✅ Successfully updated user activity")
        
        # Step 6: Verify user data again after activity update
        success, updated_user_data = self.test_get_user(user_id)
        if not success:
            print("❌ Failed to get user data after activity update")
            return False
        
        print("✅ Successfully retrieved user data after activity update")
        
        return True

    def test_discovery_api_format(self):
        """Test that the discovery API returns the correct format (not nested in potential_matches)"""
        print("\n🔍 Testing Discovery API Format...")
        
        # Step 1: Create a new test user
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_disc_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Test Discovery User {random_suffix}"
        
        success, signup_response = self.test_email_signup(test_email, test_password, test_display_name)
        if not success:
            print("❌ Email signup failed, stopping test")
            return False
        
        user_id = self.email_user['user_id']
        print(f"Created test user with ID: {user_id}")
        
        # Step 2: Complete the user profile
        complete_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_id, complete_profile)
        if not success:
            print("❌ Failed to update user profile")
            return False
        
        # Step 3: Test the discover endpoint
        success, discover_results = self.test_discover_users(user_id)
        if not success:
            print("❌ Failed to get discovery results")
            return False
        
        # Step 4: Verify the format of the response
        if isinstance(discover_results, list):
            print(f"✅ Discovery API returns an array format with {len(discover_results)} items")
            
            # Check the first item if available
            if discover_results and len(discover_results) > 0:
                first_item = discover_results[0]
                print(f"Sample discovery result: User ID: {first_item.get('user_id')}, Username: {first_item.get('username')}")
        else:
            print("❌ Discovery API does not return an array format")
            print(f"Returned type: {type(discover_results)}")
            return False
        
        # Step 5: Test the AI recommendations endpoint
        success, ai_results = self.test_ai_recommendations(user_id)
        if not success:
            print("❌ Failed to get AI recommendations")
            return False
        
        # Step 6: Verify the format of the AI recommendations response
        if isinstance(ai_results, list):
            print(f"✅ AI Recommendations API returns an array format with {len(ai_results)} items")
            
            # Check the first item if available
            if ai_results and len(ai_results) > 0:
                first_item = ai_results[0]
                print(f"Sample AI recommendation: User ID: {first_item.get('user_id')}, Username: {first_item.get('username')}")
                print(f"Compatibility: {first_item.get('ai_compatibility', {}).get('compatibility_percentage')}%")
        else:
            print("❌ AI Recommendations API does not return an array format")
            print(f"Returned type: {type(ai_results)}")
            return False
        
        return True

    def test_profile_completion_and_discovery(self):
        """Test that users with complete profiles are marked correctly and appear in discovery"""
        print("\n🔍 Testing Profile Completion and Discovery...")
        
        # Step 1: Create two test users
        random_suffix_a = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_a = f"test_prof_a_{random_suffix_a}@example.com"
        display_name_a = f"Test Profile User A {random_suffix_a}"
        
        success, signup_response_a = self.test_email_signup(email_a, "TestPassword123!", display_name_a)
        if not success:
            print("❌ Failed to create User A")
            return False
        
        user_a_id = self.email_user['user_id']
        
        random_suffix_b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_b = f"test_prof_b_{random_suffix_b}@example.com"
        display_name_b = f"Test Profile User B {random_suffix_b}"
        
        success, signup_response_b = self.test_email_signup(email_b, "TestPassword123!", display_name_b)
        if not success:
            print("❌ Failed to create User B")
            return False
        
        user_b_id = self.email_user['user_id']
        
        print(f"Created User A (ID: {user_a_id}) and User B (ID: {user_b_id})")
        
        # Step 2: Verify both users have profile_complete = false initially
        success, user_a_initial = self.test_get_user(user_a_id)
        success, user_b_initial = self.test_get_user(user_b_id)
        
        if user_a_initial.get('profile_complete') or user_b_initial.get('profile_complete'):
            print("❌ One or both users have profile_complete = true initially (unexpected)")
            return False
        
        print("✅ Both users have profile_complete = false initially (as expected)")
        
        # Step 3: Update User A with incomplete profile
        incomplete_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins"],
            # Missing trading_style
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_a_id, incomplete_profile)
        if not success:
            print("❌ Failed to update User A with incomplete profile")
            return False
        
        # Step 4: Verify User A still has profile_complete = false
        success, user_a_updated = self.test_get_user(user_a_id)
        if user_a_updated.get('profile_complete'):
            print("❌ User A has profile_complete = true with incomplete profile (unexpected)")
            return False
        
        print("✅ User A has profile_complete = false with incomplete profile (as expected)")
        
        # Step 5: Update User A with complete profile
        complete_profile_a = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_a_id, complete_profile_a)
        if not success:
            print("❌ Failed to update User A with complete profile")
            return False
        
        # Step 6: Verify User A now has profile_complete = true
        success, user_a_complete = self.test_get_user(user_a_id)
        if not user_a_complete.get('profile_complete'):
            print("❌ User A has profile_complete = false with complete profile (unexpected)")
            return False
        
        print("✅ User A has profile_complete = true with complete profile (as expected)")
        
        # Step 7: Update User B with complete profile
        complete_profile_b = {
            "trading_experience": "Advanced",
            "preferred_tokens": ["NFTs", "GameFi"],
            "trading_style": "Swing Trader",
            "portfolio_size": "$100K+"
        }
        
        success, _ = self.test_update_user_profile(user_b_id, complete_profile_b)
        if not success:
            print("❌ Failed to update User B with complete profile")
            return False
        
        # Step 8: Verify User B now has profile_complete = true
        success, user_b_complete = self.test_get_user(user_b_id)
        if not user_b_complete.get('profile_complete'):
            print("❌ User B has profile_complete = false with complete profile (unexpected)")
            return False
        
        print("✅ User B has profile_complete = true with complete profile (as expected)")
        
        # Step 9: Test if User A can discover User B
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
            print("✅ User A can discover User B (as expected)")
        else:
            print("❌ User A cannot discover User B (unexpected)")
            print(f"Discovery returned {len(discover_results_a)} users, but User B was not among them")
            return False
        
        # Step 10: Test if User B can discover User A
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
            print("✅ User B can discover User A (as expected)")
        else:
            print("❌ User B cannot discover User A (unexpected)")
            print(f"Discovery returned {len(discover_results_b)} users, but User A was not among them")
            return False
        
        # Step 11: Update User A with incomplete profile (empty preferred_tokens)
        incomplete_profile_2 = {
            "trading_experience": "Intermediate",
            "preferred_tokens": [],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.test_update_user_profile(user_a_id, incomplete_profile_2)
        if not success:
            print("❌ Failed to update User A with incomplete profile (empty tokens)")
            return False
        
        # Step 12: Verify User A now has profile_complete = false
        success, user_a_incomplete = self.test_get_user(user_a_id)
        if user_a_incomplete.get('profile_complete'):
            print("❌ User A has profile_complete = true with empty tokens (unexpected)")
            return False
        
        print("✅ User A has profile_complete = false with empty tokens (as expected)")
        
        # Step 13: Test if User B can still discover User A (should not be able to)
        print("\nTesting if User B can discover User A with incomplete profile...")
        success, discover_results_b_2 = self.test_discover_users(user_b_id)
        if not success:
            print("❌ Failed to get discovery results for User B")
            return False
        
        user_a_found_2 = False
        for user in discover_results_b_2:
            if user.get('user_id') == user_a_id:
                user_a_found_2 = True
                break
        
        if not user_a_found_2:
            print("✅ User B cannot discover User A with incomplete profile (as expected)")
        else:
            print("❌ User B can discover User A with incomplete profile (unexpected)")
            return False
        
        return True

    def test_referral_code_generation(self, user_id=None):
        """Test generating a referral code for a user"""
        if not user_id:
            # Create a new test user if user_id not provided
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            test_email = f"test_ref_{random_suffix}@example.com"
            test_password = "TestPassword123!"
            test_display_name = f"Test Referral User {random_suffix}"
            
            success, signup_response = self.test_email_signup(test_email, test_password, test_display_name)
            if not success:
                print("❌ Email signup failed, stopping test")
                return False, None
            
            user_id = self.email_user['user_id']
            print(f"Created test user with ID: {user_id}")
        
        print(f"\n🔍 Testing Referral Code Generation for user ID: {user_id}")
        
        success, response = self.run_test(
            "Generate Referral Code",
            "POST",
            f"referrals/generate/{user_id}",
            200
        )
        
        if success:
            print(f"✅ Successfully generated referral code: {response.get('referral_code')}")
            print(f"Created at: {response.get('created_at')}")
            print(f"Message: {response.get('message')}")
        
        return success, response
    
    def test_referral_code_validation(self, referral_code):
        """Test validating a referral code"""
        print(f"\n🔍 Testing Referral Code Validation for code: {referral_code}")
        
        success, response = self.run_test(
            "Validate Referral Code",
            "GET",
            f"referrals/validate/{referral_code}",
            200
        )
        
        if success:
            if response.get('valid'):
                print(f"✅ Referral code is valid")
                print(f"Referrer: {response.get('referrer', {}).get('display_name')}")
            else:
                print(f"❌ Referral code is invalid: {response.get('message')}")
        
        return success, response
    
    def test_referral_stats(self, user_id):
        """Test getting referral statistics for a user"""
        print(f"\n🔍 Testing Referral Statistics for user ID: {user_id}")
        
        success, response = self.run_test(
            "Get Referral Stats",
            "GET",
            f"referrals/stats/{user_id}",
            200
        )
        
        if success:
            print(f"✅ Successfully retrieved referral statistics")
            print(f"Referral code: {response.get('referral_code')}")
            print(f"Total referrals: {response.get('total_referrals')}")
            print(f"Successful signups: {response.get('successful_signups')}")
            print(f"Pending signups: {response.get('pending_signups')}")
            print(f"Referral link: {response.get('referral_link')}")
            
            if response.get('referred_users'):
                print(f"Referred users: {len(response.get('referred_users'))}")
                for i, user in enumerate(response.get('referred_users')):
                    print(f"  {i+1}. {user.get('display_name')} (Profile complete: {user.get('profile_complete')})")
        
        return success, response
    
    def test_signup_with_referral(self, referral_code):
        """Test signing up with a referral code"""
        print(f"\n🔍 Testing Signup with Referral Code: {referral_code}")
        
        # Generate random user data
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_referred_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Referred User {random_suffix}"
        
        data = {
            "email": test_email,
            "password": test_password,
            "display_name": test_display_name,
            "referral_code": referral_code
        }
        
        success, response = self.run_test(
            "Email Signup with Referral",
            "POST",
            "auth/email/signup",
            200,
            data=data
        )
        
        if success:
            self.email_user = response.get("user")
            print(f"✅ Successfully created user with referral code")
            print(f"User ID: {self.email_user.get('user_id')}")
            print(f"Username: {self.email_user.get('username')}")
            print(f"Referral applied: {response.get('referral_applied', False)}")
            print(f"Message: {response.get('message')}")
        
        return success, response
    
    def test_invalid_referral_signup(self):
        """Test signing up with an invalid referral code"""
        print(f"\n🔍 Testing Signup with Invalid Referral Code")
        
        # Generate random user data
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_invalid_ref_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Invalid Ref User {random_suffix}"
        
        # Generate an invalid referral code
        invalid_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        data = {
            "email": test_email,
            "password": test_password,
            "display_name": test_display_name,
            "referral_code": invalid_code
        }
        
        # We expect this to fail with a 400 status code
        success, response = self.run_test(
            "Email Signup with Invalid Referral",
            "POST",
            "auth/email/signup",
            400,
            data=data
        )
        
        if success:
            print(f"✅ Correctly rejected invalid referral code")
        
        return success, response
    
    def test_referral_flow(self):
        """Test the complete referral flow from generation to signup"""
        print("\n🔍 Testing Complete Referral Flow")
        
        # Step 1: Create a referrer user
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        referrer_email = f"referrer_{random_suffix}@example.com"
        referrer_password = "TestPassword123!"
        referrer_display_name = f"Referrer {random_suffix}"
        
        success, signup_response = self.test_email_signup(referrer_email, referrer_password, referrer_display_name)
        if not success:
            print("❌ Failed to create referrer user")
            return False
        
        referrer_id = self.email_user['user_id']
        print(f"Created referrer user with ID: {referrer_id}")
        
        # Step 2: Generate a referral code for the referrer
        success, gen_response = self.test_referral_code_generation(referrer_id)
        if not success:
            print("❌ Failed to generate referral code")
            return False
        
        referral_code = gen_response.get('referral_code')
        print(f"Generated referral code: {referral_code}")
        
        # Step 3: Validate the referral code
        success, validate_response = self.test_referral_code_validation(referral_code)
        if not success or not validate_response.get('valid'):
            print("❌ Failed to validate referral code")
            return False
        
        print(f"Validated referral code successfully")
        
        # Step 4: Sign up a new user with the referral code
        success, signup_response = self.test_signup_with_referral(referral_code)
        if not success:
            print("❌ Failed to sign up with referral code")
            return False
        
        referred_id = self.email_user['user_id']
        print(f"Created referred user with ID: {referred_id}")
        
        # Step 5: Check referral stats for the referrer
        success, stats_response = self.test_referral_stats(referrer_id)
        if not success:
            print("❌ Failed to get referral stats")
            return False
        
        # Verify that the referral was recorded
        if stats_response.get('total_referrals') > 0:
            print(f"✅ Referral was successfully recorded")
            
            # Check if the referred user is in the list
            referred_users = stats_response.get('referred_users', [])
            referred_user_found = False
            for user in referred_users:
                if user.get('user_id') == referred_id:
                    referred_user_found = True
                    break
            
            if referred_user_found:
                print(f"✅ Referred user appears in referrer's stats")
            else:
                print(f"❌ Referred user not found in referrer's stats")
                return False
        else:
            print(f"❌ Referral was not recorded in stats")
            return False
        
        # Step 6: Try to generate another referral code for the same user
        # This should return the existing code
        success, gen_response2 = self.test_referral_code_generation(referrer_id)
        if not success:
            print("❌ Failed to retrieve existing referral code")
            return False
        
        if gen_response2.get('referral_code') == referral_code:
            print(f"✅ Successfully retrieved existing referral code")
        else:
            print(f"❌ Generated a different referral code instead of returning the existing one")
            return False
        
        # Step 7: Try to sign up with an invalid referral code
        success, invalid_response = self.test_invalid_referral_signup()
        if not success:
            print("❌ Test for invalid referral code failed")
            return False
        
        print(f"✅ Complete referral flow tested successfully")
        return True
    
    def test_database_referrals(self):
        """Check the referrals collection in the database"""
        print("\n🔍 Checking Referrals in Database...")
        
        # Get all referrals
        referrals = list(self.db.referrals.find())
        total_referrals = len(referrals)
        
        # Count referrals by status
        status_counts = {}
        for referral in referrals:
            status = referral.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"Total referrals in database: {total_referrals}")
        print(f"Referrals by status: {status_counts}")
        
        # Count completed referrals
        completed_referrals = sum(1 for referral in referrals if referral.get('status') == 'completed')
        
        print(f"Completed referrals: {completed_referrals}")
        
        # Show some sample referrals
        if referrals:
            print("\nSample referrals:")
            for i, referral in enumerate(referrals[:5]):  # Show first 5 referrals
                print(f"{i+1}. Referral ID: {referral.get('referral_id')}")
                print(f"   Referrer User ID: {referral.get('referrer_user_id')}")
                print(f"   Referral Code: {referral.get('referral_code')}")
                print(f"   Status: {referral.get('status')}")
                print(f"   Created At: {referral.get('created_at')}")
                if referral.get('referred_user_id'):
                    print(f"   Referred User ID: {referral.get('referred_user_id')}")
                    print(f"   Used At: {referral.get('used_at')}")
                print()
        
        return referrals
    
    def run_auth_discovery_tests(self):
        """Run all tests related to authentication and discovery issues"""
        print("🚀 Starting Solm8 Authentication and Discovery Tests")
        
        # Step 1: Test session validation
        print("\n===== STEP 1: TEST SESSION VALIDATION =====")
        session_valid = self.test_session_validation()
        
        # Step 2: Test discovery API format
        print("\n===== STEP 2: TEST DISCOVERY API FORMAT =====")
        discovery_format_valid = self.test_discovery_api_format()
        
        # Step 3: Test profile completion and discovery
        print("\n===== STEP 3: TEST PROFILE COMPLETION AND DISCOVERY =====")
        profile_completion_valid = self.test_profile_completion_and_discovery()
        
        # Print results
        print("\n📊 Test Results Summary:")
        print(f"Session Validation: {'✅ PASSED' if session_valid else '❌ FAILED'}")
        print(f"Discovery API Format: {'✅ PASSED' if discovery_format_valid else '❌ FAILED'}")
        print(f"Profile Completion and Discovery: {'✅ PASSED' if profile_completion_valid else '❌ FAILED'}")
        
        overall_success = session_valid and discovery_format_valid and profile_completion_valid
        print(f"\nOverall Test Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        return overall_success
    
    def run_referral_tests(self):
        """Run all tests related to the referral system"""
        print("🚀 Starting Solm8 Referral System Tests")
        
        # Step 1: Test referral code generation
        print("\n===== STEP 1: TEST REFERRAL CODE GENERATION =====")
        success, gen_response = self.test_referral_code_generation()
        if not success:
            print("❌ Referral code generation test failed")
            return False
        
        referral_code = gen_response.get('referral_code')
        user_id = self.email_user['user_id']
        
        # Step 2: Test referral code validation
        print("\n===== STEP 2: TEST REFERRAL CODE VALIDATION =====")
        success, _ = self.test_referral_code_validation(referral_code)
        if not success:
            print("❌ Referral code validation test failed")
            return False
        
        # Step 3: Test referral stats
        print("\n===== STEP 3: TEST REFERRAL STATS =====")
        success, _ = self.test_referral_stats(user_id)
        if not success:
            print("❌ Referral stats test failed")
            return False
        
        # Step 4: Test signup with referral
        print("\n===== STEP 4: TEST SIGNUP WITH REFERRAL =====")
        success, _ = self.test_signup_with_referral(referral_code)
        if not success:
            print("❌ Signup with referral test failed")
            return False
        
        # Step 5: Test complete referral flow
        print("\n===== STEP 5: TEST COMPLETE REFERRAL FLOW =====")
        success = self.test_referral_flow()
        if not success:
            print("❌ Complete referral flow test failed")
            return False
        
        # Step 6: Check database referrals
        print("\n===== STEP 6: CHECK DATABASE REFERRALS =====")
        self.test_database_referrals()
        
        print("\n📊 Referral System Tests Summary:")
        print("✅ All referral system tests passed successfully")
        
        return True

if __name__ == "__main__":
    tester = Solm8APITester()
    # tester.run_auth_discovery_tests()
    tester.run_referral_tests()
