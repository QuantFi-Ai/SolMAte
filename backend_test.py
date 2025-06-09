import requests
import json
import sys
import uuid
from datetime import datetime

class SolMatchAPITester:
    def __init__(self, base_url="https://b455855f-f3ef-4faa-b146-fcff2737404b.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_id = None
        self.test_match_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        if success:
            print(f"Health check response: {response}")
        return success

    def test_twitter_login_redirect(self):
        """Test the Twitter login redirect"""
        print("\n🔍 Testing Twitter Login Redirect...")
        url = f"{self.base_url}/api/login/twitter"
        
        try:
            response = requests.get(url, allow_redirects=False)
            # We expect a redirect (302, 303, or 307)
            if response.status_code in [302, 303, 307]:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Redirect URL: {response.headers.get('Location')}")
                return True
            else:
                print(f"❌ Failed - Expected redirect status, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for further testing"""
        print("\n🔍 Creating test user for API testing...")
        
        # Generate a unique user ID
        user_id = str(uuid.uuid4())
        twitter_id = f"test_twitter_{int(datetime.now().timestamp())}"
        
        # Create user data with enhanced profile fields
        user_data = {
            "user_id": user_id,
            "twitter_id": twitter_id,
            "username": f"test_user_{int(datetime.now().timestamp())}",
            "display_name": "Test User",
            "avatar_url": "https://images.pexels.com/photos/31610834/pexels-photo-31610834.jpeg",
            "bio": "This is a test user for API testing",
            "location": "San Francisco, CA",
            "trading_experience": "Intermediate",
            "years_trading": 3,
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$1K-$10K",
            "risk_tolerance": "Moderate",
            "best_trade": "Bought SOL at $20, sold at $200",
            "worst_trade": "Lost 50% on a meme coin rugpull",
            "favorite_project": "Jupiter - best DEX aggregator",
            "trading_hours": "Evening",
            "communication_style": "Technical",
            "looking_for": ["Alpha Sharing", "Research Partner"],
            "profile_complete": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat()
        }
        
        # Try to insert directly into MongoDB
        try:
            import pymongo
            import os
            
            # Connect to MongoDB
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = pymongo.MongoClient(mongo_url)
            db = client.solmatch_db
            users_collection = db.users
            
            # Insert the test user
            users_collection.insert_one(user_data)
            print(f"✅ Created test user with ID: {user_id}")
            self.test_user_id = user_id
            return user_id
            
        except Exception as e:
            print(f"❌ Failed to create test user: {str(e)}")
            return None

    def test_get_user(self):
        """Test getting a user profile"""
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            f"user/{self.test_user_id}",
            200
        )
        if success:
            print(f"User profile: {json.dumps(response, indent=2)}")
        return success

    def test_update_user(self):
        """Test updating a user profile"""
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        update_data = {
            "bio": "Updated bio for testing",
            "location": "New York, NY",
            "trading_experience": "Expert",
            "years_trading": 5,
            "preferred_tokens": ["Blue Chips", "NFTs", "AI Tokens"],
            "trading_style": "HODLer",
            "portfolio_size": "$100K+",
            "risk_tolerance": "Aggressive",
            "best_trade": "Updated best trade story",
            "worst_trade": "Updated worst trade story",
            "favorite_project": "Magic Eden - best NFT marketplace",
            "trading_hours": "Night Owl",
            "communication_style": "Professional",
            "looking_for": ["Teaching", "Risk Management"]
        }
        
        success, response = self.run_test(
            "Update User Profile",
            "PUT",
            f"user/{self.test_user_id}",
            200,
            data=update_data
        )
        
        if success:
            # Verify the update by getting the user again
            verify_success, user_data = self.run_test(
                "Verify User Update",
                "GET",
                f"user/{self.test_user_id}",
                200
            )
            
            if verify_success:
                # Check if the update was applied
                update_successful = True
                for key, value in update_data.items():
                    if user_data.get(key) != value:
                        update_successful = False
                        print(f"❌ Update verification failed for {key}: expected {value}, got {user_data.get(key)}")
                
                if update_successful:
                    print("✅ User update verified successfully")
                    return True
                else:
                    return False
        
        return success

    def test_discover_users(self):
        """Test discovering potential matches"""
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        success, response = self.run_test(
            "Discover Users",
            "GET",
            f"discover/{self.test_user_id}",
            200
        )
        
        if success:
            print(f"Found {len(response)} potential matches")
            if len(response) > 0:
                print(f"First match: {json.dumps(response[0], indent=2)}")
        
        return success

    def create_test_match(self):
        """Create a test match for further testing"""
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        print("\n🔍 Creating test match for API testing...")
        
        try:
            import pymongo
            import os
            
            # Connect to MongoDB
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = pymongo.MongoClient(mongo_url)
            db = client.solmatch_db
            users_collection = db.users
            matches_collection = db.matches
            
            # Create another test user with enhanced profile
            other_user_id = str(uuid.uuid4())
            twitter_id = f"test_twitter_{int(datetime.now().timestamp())}"
            
            other_user_data = {
                "user_id": other_user_id,
                "twitter_id": twitter_id,
                "username": f"test_match_{int(datetime.now().timestamp())}",
                "display_name": "Test Match",
                "avatar_url": "https://images.pexels.com/photos/31630004/pexels-photo-31630004.jpeg",
                "bio": "This is a test match for API testing",
                "location": "Austin, TX",
                "trading_experience": "Advanced",
                "years_trading": 4,
                "preferred_tokens": ["GameFi", "AI Tokens"],
                "trading_style": "Swing Trader",
                "portfolio_size": "$10K-$100K",
                "risk_tolerance": "YOLO",
                "best_trade": "Made 20x on a GameFi token",
                "worst_trade": "Bought the top of a bull market",
                "favorite_project": "Tensor - best NFT trading platform",
                "trading_hours": "24/7",
                "communication_style": "Casual",
                "looking_for": ["Learning", "Networking"],
                "profile_complete": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow().isoformat()
            }
            
            # Insert the other test user
            users_collection.insert_one(other_user_data)
            
            # Create a match between the two users
            match_id = str(uuid.uuid4())
            match_data = {
                "match_id": match_id,
                "user1_id": self.test_user_id,
                "user2_id": other_user_id,
                "created_at": datetime.utcnow(),
                "last_message_at": datetime.utcnow()
            }
            
            matches_collection.insert_one(match_data)
            print(f"✅ Created test match with ID: {match_id}")
            self.test_match_id = match_id
            return match_id
            
        except Exception as e:
            print(f"❌ Failed to create test match: {str(e)}")
            return None

    def test_get_matches(self):
        """Test getting user matches"""
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        success, response = self.run_test(
            "Get User Matches",
            "GET",
            f"matches/{self.test_user_id}",
            200
        )
        
        if success:
            print(f"Found {len(response)} matches")
            if len(response) > 0:
                print(f"First match: {json.dumps(response[0], indent=2)}")
        
        return success

    def test_get_messages(self):
        """Test getting match messages"""
        if not self.test_match_id:
            print("❌ No test match ID available")
            return False
            
        success, response = self.run_test(
            "Get Match Messages",
            "GET",
            f"messages/{self.test_match_id}",
            200
        )
        
        if success:
            print(f"Found {len(response)} messages")
        
        return success

    def test_profile_completion_validation(self):
        """Test that profile completion validation works correctly"""
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        # First, update the profile to be incomplete
        incomplete_data = {
            "trading_experience": "",
            "preferred_tokens": [],
            "trading_style": "",
            "portfolio_size": ""
        }
        
        success, _ = self.run_test(
            "Set Incomplete Profile",
            "PUT",
            f"user/{self.test_user_id}",
            200,
            data=incomplete_data
        )
        
        if not success:
            return False
            
        # Verify profile is marked as incomplete
        verify_success, user_data = self.run_test(
            "Verify Incomplete Profile",
            "GET",
            f"user/{self.test_user_id}",
            200
        )
        
        if not verify_success:
            return False
            
        if user_data.get("profile_complete") == True:
            print("❌ Profile incorrectly marked as complete when it should be incomplete")
            return False
            
        # Now update to complete the profile
        complete_data = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$1K-$10K"
        }
        
        success, _ = self.run_test(
            "Set Complete Profile",
            "PUT",
            f"user/{self.test_user_id}",
            200,
            data=complete_data
        )
        
        if not success:
            return False
            
        # Verify profile is marked as complete
        verify_success, user_data = self.run_test(
            "Verify Complete Profile",
            "GET",
            f"user/{self.test_user_id}",
            200
        )
        
        if not verify_success:
            return False
            
        if user_data.get("profile_complete") != True:
            print("❌ Profile incorrectly marked as incomplete when it should be complete")
            return False
            
        print("✅ Profile completion validation works correctly")
        return True

def main():
    tester = SolMatchAPITester()
    
    # Test health check
    health_check_success = tester.test_health_check()
    
    # Test Twitter login redirect
    twitter_login_success = tester.test_twitter_login_redirect()
    
    # Test demo user creation
    success, response = tester.run_test(
        "Create Demo User",
        "POST",
        "create-demo-user",
        200
    )
    
    if success and "user_id" in response:
        print(f"Created demo user with ID: {response['user_id']}")
    
    # Create a test user for further testing
    tester.create_test_user()
    
    # Test user endpoints
    if tester.test_user_id:
        tester.test_get_user()
        tester.test_update_user()
        tester.test_discover_users()
        tester.test_swipe_action()
        
        # Create a test match
        tester.create_test_match()
        
        # Test match endpoints
        if tester.test_match_id:
            tester.test_get_matches()
            tester.test_get_messages()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
