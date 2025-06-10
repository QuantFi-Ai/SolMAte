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

class Solm8APITester:
    def __init__(self, base_url="https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_user = None
        self.uploaded_image_id = None
        self.token_launch_profile = None
        self.email_user = None
        self.wallet_user = None
        self.wallet_message = None

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

    def test_update_twitter_settings(self, user_id, show_twitter, twitter_username):
        """Test updating Twitter settings"""
        profile_data = {
            "show_twitter": show_twitter,
            "twitter_username": twitter_username
        }
        return self.run_test(
            "Update Twitter Settings",
            "PUT",
            f"user/{user_id}",
            200,
            data=profile_data
        )

    def test_upload_profile_image(self, user_id, image_path):
        """Test uploading a profile image"""
        with open(image_path, 'rb') as img:
            files = {'file': ('test_image.jpg', img, 'image/jpeg')}
            success, response = self.run_test(
                "Upload Profile Image",
                "POST",
                f"upload-profile-image/{user_id}",
                200,
                files=files
            )
            if success and 'image_id' in response:
                self.uploaded_image_id = response['image_id']
            return success, response

    def test_get_profile_image(self, image_id):
        """Test getting a profile image"""
        return self.run_test(
            "Get Profile Image",
            "GET",
            f"profile-image/{image_id}",
            200
        )

    def test_discover_users(self, user_id):
        """Test discovering potential matches"""
        return self.run_test(
            "Discover Users",
            "GET",
            f"discover/{user_id}",
            200
        )

    def test_swipe_action(self, swiper_id, target_id, action):
        """Test swiping on a user"""
        return self.run_test(
            f"Swipe {action.capitalize()}",
            "POST",
            "swipe",
            200,
            data={
                "swiper_id": swiper_id,
                "target_id": target_id,
                "action": action
            }
        )

    def test_get_matches(self, user_id):
        """Test getting user matches"""
        return self.run_test(
            "Get Matches",
            "GET",
            f"matches/{user_id}",
            200
        )

    def test_get_messages(self, match_id):
        """Test getting match messages"""
        return self.run_test(
            "Get Messages",
            "GET",
            f"messages/{match_id}",
            200
        )
        
    # User Status Management Tests
    
    def test_update_user_status(self, user_id, status):
        """Test updating user status (active/offline)"""
        return self.run_test(
            f"Update User Status to {status}",
            "POST",
            f"user-status/{user_id}",
            200,
            data={"user_status": status}
        )
    
    def test_get_user_status(self, user_id):
        """Test getting user status"""
        return self.run_test(
            "Get User Status",
            "GET",
            f"user-status/{user_id}",
            200
        )
    
    def test_get_active_users(self):
        """Test getting list of active users"""
        return self.run_test(
            "Get Active Users",
            "GET",
            "users/active",
            200
        )
    
    def test_update_user_activity(self, user_id):
        """Test updating user's last activity timestamp"""
        return self.run_test(
            "Update User Activity",
            "POST",
            f"user/{user_id}/update-activity",
            200
        )
    
    # Token Launch Profile Tests
    
    def test_update_token_launch_profile(self, user_id, token_profile_data):
        """Test updating token launch profile"""
        # Add user_id to the token profile data
        token_profile_data["user_id"] = user_id
        return self.run_test(
            "Update Token Launch Profile",
            "POST",
            f"token-launch-profile/{user_id}",
            200,
            data=token_profile_data
        )
    
    def test_get_token_launch_profile(self, user_id):
        """Test getting token launch profile"""
        return self.run_test(
            "Get Token Launch Profile",
            "GET",
            f"token-launch-profile/{user_id}",
            200
        )
    
    def test_get_token_launchers(self):
        """Test getting users interested in token launches"""
        return self.run_test(
            "Get Token Launchers",
            "GET",
            "users/token-launchers",
            200
        )
    
    def test_get_public_profile(self, username):
        """Test getting public profile with new fields"""
        return self.run_test(
            "Get Public Profile",
            "GET",
            f"public-profile/{username}",
            200
        )
        
    # Authentication Tests
    
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
    
    def test_email_signup_duplicate(self, email, password="TestPassword123!", display_name="Duplicate Test User"):
        """Test email signup with duplicate email (should fail)"""
        data = {
            "email": email,
            "password": password,
            "display_name": display_name
        }
        
        # This should fail with 400 status code
        return self.run_test(
            "Email Signup (Duplicate)",
            "POST",
            "auth/email/signup",
            400,
            data=data
        )
    
    def test_email_signup_missing_fields(self):
        """Test email signup with missing fields (should fail)"""
        # Missing password
        data = {
            "email": "missing_fields@example.com",
            "display_name": "Missing Fields User"
        }
        
        # This should fail with 422 status code (validation error)
        return self.run_test(
            "Email Signup (Missing Fields)",
            "POST",
            "auth/email/signup",
            422,
            data=data
        )
    
    def test_email_login(self, email, password="TestPassword123!"):
        """Test email login"""
        data = {
            "email": email,
            "password": password
        }
        
        return self.run_test(
            "Email Login",
            "POST",
            "auth/email/login",
            200,
            data=data
        )
    
    def test_email_login_invalid(self, email, wrong_password="WrongPassword123!"):
        """Test email login with invalid credentials (should fail)"""
        data = {
            "email": email,
            "password": wrong_password
        }
        
        # This should fail with 401 status code
        return self.run_test(
            "Email Login (Invalid Credentials)",
            "POST",
            "auth/email/login",
            401,
            data=data
        )
    
    def test_email_login_nonexistent(self):
        """Test email login with non-existent email (should fail)"""
        data = {
            "email": "nonexistent_user@example.com",
            "password": "SomePassword123!"
        }
        
        # This should fail with 401 status code
        return self.run_test(
            "Email Login (Non-existent User)",
            "POST",
            "auth/email/login",
            401,
            data=data
        )
    
    def test_get_wallet_message(self):
        """Test getting message for wallet signature"""
        success, response = self.run_test(
            "Get Wallet Message",
            "GET",
            "auth/wallet/message",
            200
        )
        
        if success:
            self.wallet_message = response.get("message")
            print(f"Got wallet message: {self.wallet_message}")
            
        return success, response
    
    def test_wallet_connect(self, wallet_address=None, signature=None, message=None):
        """Test connecting with Solana wallet"""
        if not wallet_address:
            # Generate random wallet address
            wallet_address = ''.join(random.choices(string.ascii_lowercase + string.digits, k=44))
            
        if not signature:
            # Generate random signature
            signature = ''.join(random.choices(string.ascii_lowercase + string.digits, k=88))
            
        if not message:
            message = self.wallet_message or f"Sign this message to authenticate with Solm8: {int(time.time())}"
            
        data = {
            "wallet_address": wallet_address,
            "signature": signature,
            "message": message
        }
        
        success, response = self.run_test(
            "Wallet Connect",
            "POST",
            "auth/wallet/connect",
            200,
            data=data
        )
        
        if success:
            self.wallet_user = response.get("user")
            print(f"Connected wallet user: {self.wallet_user['username']}")
            
        return success, response
    
    def test_wallet_connect_duplicate(self, wallet_address, signature=None, message=None):
        """Test connecting with the same wallet address again"""
        if not signature:
            # Generate random signature
            signature = ''.join(random.choices(string.ascii_lowercase + string.digits, k=88))
            
        if not message:
            message = self.wallet_message or f"Sign this message to authenticate with Solm8: {int(time.time())}"
            
        data = {
            "wallet_address": wallet_address,
            "signature": signature,
            "message": message
        }
        
        # This should succeed with 200 status code (existing user login)
        return self.run_test(
            "Wallet Connect (Duplicate)",
            "POST",
            "auth/wallet/connect",
            200,
            data=data
        )
    
    def test_wallet_connect_invalid(self):
        """Test connecting with invalid wallet address (should fail)"""
        data = {
            "wallet_address": "invalid",  # Too short
            "signature": "some_signature",
            "message": "some_message"
        }
        
        # This should fail with 400 status code
        return self.run_test(
            "Wallet Connect (Invalid)",
            "POST",
            "auth/wallet/connect",
            400,
            data=data
        )

    def create_test_image(self):
        """Create a temporary test image for upload testing"""
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.jpg')
        os.close(fd)
        
        # Create a simple image file (1x1 pixel black image)
        with open(path, 'wb') as f:
            # Simple JPEG header and data for a 1x1 black pixel
            f.write(b'\xff\xd8\xff\xe0\x10JFIF\x01\x01\x01HH\xff\xdbC\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdbC\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x11\x08\x01\x01\x03\x01"\x02\x11\x01\x03\x11\x01\xff\xc4\x1f\x01\x05\x01\x01\x01\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\xb5\x10\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x01}\x01\x02\x03\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x1f\x01\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\xb5\x11\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x01\x02w\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x0c\x03\x01\x02\x11\x03\x11?\xfe\xfe(\xa2\x8a\xff\xd9')
        
        print(f"Created test image at {path}")
        return path

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Solm8 API Tests")
        
        # Test health check
        self.test_health_check()
        
        # Test Authentication Endpoints
        print("\n🔍 Testing Authentication Endpoints...")
        
        # Email Authentication Tests
        print("\n🔑 Testing Email Authentication...")
        
        # Test email signup
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Test User {random_suffix}"
        
        success, signup_response = self.test_email_signup(test_email, test_password, test_display_name)
        if not success:
            print("❌ Email signup failed, stopping authentication tests")
            return False
            
        # Verify user was created with correct auth_method
        if self.email_user.get('auth_method') != "email":
            print("❌ Email user auth_method verification failed - expected 'email'")
            self.tests_run += 1
            return False
        else:
            print("✅ Email user auth_method verification passed")
            self.tests_passed += 1
            self.tests_run += 1
            
        # Test duplicate email signup (should fail)
        success, _ = self.test_email_signup_duplicate(test_email)
        if not success:
            print("❌ Duplicate email test failed - should return 400")
            return False
            
        # Test missing fields (should fail)
        success, _ = self.test_email_signup_missing_fields()
        if not success:
            print("❌ Missing fields test failed - should return 422")
            return False
            
        # Test valid login
        success, login_response = self.test_email_login(test_email, test_password)
        if not success:
            print("❌ Email login failed")
            return False
            
        # Test invalid password
        success, _ = self.test_email_login_invalid(test_email)
        if not success:
            print("❌ Invalid password test failed - should return 401")
            return False
            
        # Test non-existent user
        success, _ = self.test_email_login_nonexistent()
        if not success:
            print("❌ Non-existent user test failed - should return 401")
            return False
            
        # Wallet Authentication Tests
        print("\n💼 Testing Wallet Authentication...")
        
        # Test getting wallet message
        success, message_response = self.test_get_wallet_message()
        if not success:
            print("❌ Get wallet message failed")
            return False
            
        # Verify message format
        if not self.wallet_message or "Sign this message to authenticate with Solm8" not in self.wallet_message:
            print("❌ Wallet message verification failed - unexpected format")
            self.tests_run += 1
            return False
        else:
            print("✅ Wallet message verification passed")
            self.tests_passed += 1
            self.tests_run += 1
            
        # Test wallet connect
        wallet_address = ''.join(random.choices(string.ascii_lowercase + string.digits, k=44))
        success, connect_response = self.test_wallet_connect(wallet_address)
        if not success:
            print("❌ Wallet connect failed")
            return False
            
        # Verify user was created with correct auth_method
        if self.wallet_user.get('auth_method') != "wallet":
            print("❌ Wallet user auth_method verification failed - expected 'wallet'")
            self.tests_run += 1
            return False
        else:
            print("✅ Wallet user auth_method verification passed")
            self.tests_passed += 1
            self.tests_run += 1
            
        # Test connecting with same wallet again (should succeed as login)
        success, reconnect_response = self.test_wallet_connect_duplicate(wallet_address)
        if not success:
            print("❌ Wallet reconnect test failed - should return 200")
            return False
            
        # Test invalid wallet address
        success, _ = self.test_wallet_connect_invalid()
        if not success:
            print("❌ Invalid wallet test failed - should return 400")
            return False
            
        # Verify password is not stored in plain text
        # Get the user from the database directly via API
        success, user_response = self.test_get_user(self.email_user['user_id'])
        if not success:
            print("❌ Get user for password verification failed")
            return False
            
        # Check that password is not returned in the user object
        if 'password' in user_response or 'password_hash' in user_response:
            print("❌ Password security verification failed - password/hash exposed in API response")
            self.tests_run += 1
            return False
        else:
            print("✅ Password security verification passed - not exposed in API response")
            self.tests_passed += 1
            self.tests_run += 1
            
        # Create demo user
        success, user = self.test_create_demo_user()
        if not success or not user:
            print("❌ Demo user creation failed, stopping tests")
            return False
        
        user_id = user['user_id']
        username = user['username']
        
        # Test getting user profile
        success, _ = self.test_get_user(user_id)
        if not success:
            print("❌ Get user profile failed, stopping tests")
            return False
        
        # Test uploading profile image
        test_image_path = self.create_test_image()
        success, upload_response = self.test_upload_profile_image(user_id, test_image_path)
        if not success:
            print("❌ Profile image upload failed, stopping tests")
            os.remove(test_image_path)  # Clean up
            return False
        
        # Test getting profile image
        if self.uploaded_image_id:
            success, _ = self.test_get_profile_image(self.uploaded_image_id)
            if not success:
                print("❌ Get profile image failed, stopping tests")
                os.remove(test_image_path)  # Clean up
                return False
        
        # Clean up test image
        os.remove(test_image_path)
        
        # Test updating Twitter settings
        twitter_settings = {
            "show_twitter": True,
            "twitter_username": "test_trader"
        }
        success, _ = self.test_update_user_profile(user_id, twitter_settings)
        if not success:
            print("❌ Update Twitter settings failed, stopping tests")
            return False
        
        # Test updating user profile with all fields
        profile_data = {
            "bio": "Test bio for API testing",
            "location": "Test Location",
            "show_twitter": True,
            "twitter_username": "test_trader",
            "trading_experience": "Intermediate",
            "years_trading": 3,
            "preferred_tokens": ["Meme Coins", "DeFi", "NFTs"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K",
            "risk_tolerance": "Moderate",
            "best_trade": "Test best trade",
            "worst_trade": "Test worst trade",
            "favorite_project": "Jupiter",
            "trading_hours": "Morning",
            "communication_style": "Technical",
            "preferred_communication_platform": "Discord",
            "preferred_trading_platform": "Axiom",
            "looking_for": ["Alpha Sharing", "Research Partner"]
        }
        
        success, _ = self.test_update_user_profile(user_id, profile_data)
        if not success:
            print("❌ Update user profile failed, stopping tests")
            return False
        
        # Verify profile was updated correctly
        success, updated_user = self.test_get_user(user_id)
        if not success:
            print("❌ Get updated user profile failed, stopping tests")
            return False
        
        # Verify Twitter settings were saved
        if not updated_user.get('show_twitter') or updated_user.get('twitter_username') != "test_trader":
            print("❌ Twitter settings verification failed")
            self.tests_run += 1
            return False
        else:
            print("✅ Twitter settings verification passed")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Test User Status Management
        print("\n🔍 Testing User Status Management...")
        
        # Test updating user status to active
        success, _ = self.test_update_user_status(user_id, "active")
        if not success:
            print("❌ Update user status to active failed")
            return False
        
        # Test getting user status
        success, status_response = self.test_get_user_status(user_id)
        if not success:
            print("❌ Get user status failed")
            return False
        
        # Verify status was set to active
        if status_response.get('user_status') != "active":
            print("❌ User status verification failed - expected 'active'")
            self.tests_run += 1
            return False
        else:
            print("✅ User status verification passed - status is 'active'")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Test getting active users
        success, active_users_response = self.test_get_active_users()
        if not success:
            print("❌ Get active users failed")
            return False
        
        # Verify our user is in the active users list
        user_found = False
        for active_user in active_users_response.get('active_users', []):
            if active_user.get('user_id') == user_id:
                user_found = True
                break
        
        if not user_found:
            print("❌ Active users verification failed - user not found in active list")
            self.tests_run += 1
            return False
        else:
            print("✅ Active users verification passed - user found in active list")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Test updating user activity
        success, _ = self.test_update_user_activity(user_id)
        if not success:
            print("❌ Update user activity failed")
            return False
        
        # Test updating user status to offline
        success, _ = self.test_update_user_status(user_id, "offline")
        if not success:
            print("❌ Update user status to offline failed")
            return False
        
        # Test getting user status again
        success, status_response = self.test_get_user_status(user_id)
        if not success:
            print("❌ Get user status after offline update failed")
            return False
        
        # Verify status was set to offline
        if status_response.get('user_status') != "offline":
            print("❌ User status verification failed - expected 'offline'")
            self.tests_run += 1
            return False
        else:
            print("✅ User status verification passed - status is 'offline'")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Test Token Launch Profile
        print("\n🔍 Testing Token Launch Profile...")
        
        # Create token launch profile
        token_profile_data = {
            "interested_in_token_launch": True,
            "token_launch_experience": "Experienced",
            "launch_timeline": "3-6 months",
            "launch_budget": "$50K-$100K",
            "project_type": "DeFi Protocol",
            "looking_for_help_with": ["Technical Development", "Marketing", "Community Building"]
        }
        
        success, _ = self.test_update_token_launch_profile(user_id, token_profile_data)
        if not success:
            print("❌ Update token launch profile failed")
            return False
        
        # Test getting token launch profile
        success, token_profile_response = self.test_get_token_launch_profile(user_id)
        if not success:
            print("❌ Get token launch profile failed")
            return False
        
        # Verify token launch profile was created correctly
        if not token_profile_response.get('interested_in_token_launch') or token_profile_response.get('token_launch_experience') != "Experienced":
            print("❌ Token launch profile verification failed")
            self.tests_run += 1
            return False
        else:
            print("✅ Token launch profile verification passed")
            self.tests_passed += 1
            self.tests_run += 1
            self.token_launch_profile = token_profile_response
        
        # Test getting token launchers
        success, token_launchers_response = self.test_get_token_launchers()
        if not success:
            print("❌ Get token launchers failed")
            return False
        
        # Verify our user is in the token launchers list
        user_found = False
        for launcher in token_launchers_response.get('token_launchers', []):
            if launcher.get('user_id') == user_id:
                user_found = True
                break
        
        if not user_found:
            print("❌ Token launchers verification failed - user not found in launchers list")
            self.tests_run += 1
            return False
        else:
            print("✅ Token launchers verification passed - user found in launchers list")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Test Enhanced Public Profile
        print("\n🔍 Testing Enhanced Public Profile...")
        
        # Test getting public profile
        success, public_profile = self.test_get_public_profile(username)
        if not success:
            print("❌ Get public profile failed")
            return False
        
        # Verify public profile includes new fields
        if 'timezone' not in public_profile or 'user_status' not in public_profile or 'interested_in_token_launch' not in public_profile:
            print("❌ Public profile verification failed - missing new fields")
            self.tests_run += 1
            return False
        else:
            print("✅ Public profile verification passed - includes new fields")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Test discovering users
        success, discover_response = self.test_discover_users(user_id)
        if not success:
            print("❌ Discover users failed, stopping tests")
            return False
        
        # Test swiping if there are users to discover
        if discover_response and len(discover_response) > 0:
            target_id = discover_response[0]['user_id']
            success, swipe_response = self.test_swipe_action(user_id, target_id, "like")
            if not success:
                print("❌ Swipe action failed, stopping tests")
                return False
            
            # Test getting matches
            success, matches_response = self.test_get_matches(user_id)
            if not success:
                print("❌ Get matches failed, stopping tests")
                return False
            
            # Test getting messages if there are matches
            if matches_response and len(matches_response) > 0:
                match_id = matches_response[0]['match_id']
                success, _ = self.test_get_messages(match_id)
                if not success:
                    print("❌ Get messages failed, stopping tests")
                    return False
                
                # Verify Twitter info is displayed in matches
                if matches_response[0]['other_user'].get('show_twitter'):
                    if 'twitter_username' not in matches_response[0]['other_user']:
                        print("❌ Twitter username not displayed in match data")
                        self.tests_run += 1
                        return False
                    else:
                        print("✅ Twitter username correctly displayed in match data")
                        self.tests_passed += 1
                        self.tests_run += 1
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = Solm8APITester()
    tester.run_all_tests()