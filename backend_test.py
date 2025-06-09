import requests
import unittest
import uuid
from datetime import datetime

class SolMatchAPITester:
    def __init__(self, base_url="https://b455855f-f3ef-4faa-b146-fcff2737404b.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_user = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
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

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting SolMatch API Tests")
        
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
        
        # Test updating user profile
        profile_data = {
            "bio": "Test bio for API testing",
            "location": "Test Location",
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
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = SolMatchAPITester()
    tester.run_all_tests()
