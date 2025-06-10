import requests
import unittest
import uuid
import os
import tempfile
import time
from datetime import datetime

class Solm8APITester:
    def __init__(self, base_url="https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_user = None
        self.uploaded_image_id = None
        self.token_launch_profile = None

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
        
        # Create demo user
        success, user = self.test_create_demo_user()
        if not success or not user:
            print("❌ Demo user creation failed, stopping tests")
            return False
        
        user_id = user['user_id']
        
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