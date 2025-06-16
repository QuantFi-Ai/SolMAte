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

class DiscoveryDebugger:
    def __init__(self, base_url="https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com"):
        self.base_url = base_url
        self.mongo_client = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client.solm8_db
        self.test_users = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        default_headers = {'Content-Type': 'application/json'} if not files else {}
        if headers:
            default_headers.update(headers)
        
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

    def check_database_users(self):
        """Check users in the database"""
        print("\n🔍 Checking Users in Database...")
        
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
        
        # Check last_activity and user_status
        active_users = sum(1 for user in users if user.get('user_status') == 'active')
        
        print(f"Users with 'active' status: {active_users}")
        
        # Show some sample users with complete profiles
        complete_users = [user for user in users if user.get('profile_complete', False)]
        if complete_users:
            print("\nSample users with complete profiles:")
            for i, user in enumerate(complete_users[:5]):  # Show first 5 users
                print(f"{i+1}. User ID: {user.get('user_id')}")
                print(f"   Username: {user.get('username')}")
                print(f"   Auth Method: {user.get('auth_method')}")
                print(f"   User Status: {user.get('user_status')}")
                print(f"   Last Activity: {user.get('last_activity')}")
                print(f"   Trading Experience: {user.get('trading_experience')}")
                print(f"   Preferred Tokens: {user.get('preferred_tokens')}")
                print(f"   Trading Style: {user.get('trading_style')}")
                print(f"   Portfolio Size: {user.get('portfolio_size')}")
                print()
        else:
            print("No users with complete profiles found.")
        
        return users, complete_users

    def create_test_user(self, index=0):
        """Create a test user with a complete profile"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"test_discovery_{index}_{random_suffix}@example.com"
        password = "TestPassword123!"
        display_name = f"Test Discovery User {index} {random_suffix}"
        
        # Create user
        data = {
            "email": email,
            "password": password,
            "display_name": display_name
        }
        
        success, response = self.run_test(
            f"Create Test User {index}",
            "POST",
            "auth/email/signup",
            200,
            data=data
        )
        
        if not success:
            print(f"❌ Failed to create test user {index}")
            return None
        
        user = response.get("user")
        print(f"Created test user: {user['username']} (ID: {user['user_id']})")
        
        # Complete profile with different trading preferences
        trading_experiences = ["Beginner", "Intermediate", "Advanced", "Expert"]
        trading_styles = ["Day Trader", "Swing Trader", "HODLer", "Scalper"]
        portfolio_sizes = ["Under $1K", "$1K-$10K", "$10K-$100K", "$100K+"]
        token_options = [
            ["Meme Coins", "DeFi"], 
            ["NFTs", "GameFi"], 
            ["Blue Chips", "DeFi"], 
            ["Meme Coins", "NFTs", "GameFi"]
        ]
        
        profile_data = {
            "trading_experience": trading_experiences[index % len(trading_experiences)],
            "preferred_tokens": token_options[index % len(token_options)],
            "trading_style": trading_styles[index % len(trading_styles)],
            "portfolio_size": portfolio_sizes[index % len(portfolio_sizes)],
            "bio": f"Test user for discovery debugging {index}",
            "location": "Crypto Land",
            "timezone": "UTC"
        }
        
        success, _ = self.run_test(
            f"Complete Profile for User {index}",
            "PUT",
            f"user/{user['user_id']}",
            200,
            data=profile_data
        )
        
        if not success:
            print(f"❌ Failed to complete profile for test user {index}")
            return None
        
        # Set user as active with recent last_activity
        success, _ = self.run_test(
            f"Update Activity for User {index}",
            "POST",
            f"user/{user['user_id']}/update-activity",
            200
        )
        
        if not success:
            print(f"❌ Failed to update activity for test user {index}")
        
        # Set user status to active or offline
        status = "active" if index % 2 == 0 else "offline"
        success, _ = self.run_test(
            f"Set Status for User {index}",
            "POST",
            f"user-status/{user['user_id']}",
            200,
            data={"user_status": status}
        )
        
        if not success:
            print(f"❌ Failed to set status for test user {index}")
        
        # Verify profile is complete
        success, updated_user = self.run_test(
            f"Verify Profile Completion for User {index}",
            "GET",
            f"user/{user['user_id']}",
            200
        )
        
        if success:
            if updated_user.get('profile_complete'):
                print(f"✅ User {index} profile is complete")
            else:
                print(f"❌ User {index} profile is NOT marked as complete")
                print(f"Profile data: {profile_data}")
                return None
        else:
            print(f"❌ Failed to verify profile completion for user {index}")
            return None
        
        return user

    def create_test_users(self, count=5):
        """Create multiple test users with complete profiles"""
        print(f"\n🔍 Creating {count} Test Users...")
        
        self.test_users = []
        for i in range(count):
            user = self.create_test_user(i)
            if user:
                self.test_users.append(user)
        
        print(f"\nCreated {len(self.test_users)} test users successfully")
        return self.test_users

    def test_discovery(self, user_id):
        """Test the discovery endpoint for a user"""
        print(f"\n🔍 Testing Discovery for User ID: {user_id}")
        
        success, discover_results = self.run_test(
            "Discovery Endpoint",
            "GET",
            f"discover/{user_id}",
            200
        )
        
        if success:
            print(f"Discovery returned {len(discover_results)} potential matches")
            
            if discover_results:
                print("\nSample discovery results:")
                for i, match in enumerate(discover_results[:3]):  # Show first 3 matches
                    print(f"{i+1}. User ID: {match.get('user_id')}")
                    print(f"   Username: {match.get('username')}")
                    print(f"   Profile Complete: {match.get('profile_complete')}")
                    print(f"   Trading Experience: {match.get('trading_experience')}")
                    print(f"   Last Activity: {match.get('last_activity')}")
            else:
                print("No discovery results found.")
        
        return success, discover_results

    def test_ai_recommendations(self, user_id):
        """Test the AI recommendations endpoint for a user"""
        print(f"\n🔍 Testing AI Recommendations for User ID: {user_id}")
        
        success, ai_results = self.run_test(
            "AI Recommendations Endpoint",
            "GET",
            f"ai-recommendations/{user_id}",
            200
        )
        
        if success:
            print(f"AI recommendations returned {len(ai_results)} potential matches")
            
            if ai_results:
                print("\nSample AI recommendations:")
                for i, match in enumerate(ai_results[:3]):  # Show first 3 matches
                    print(f"{i+1}. User ID: {match.get('user_id')}")
                    print(f"   Username: {match.get('username')}")
                    print(f"   Compatibility: {match.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                    print(f"   Profile Complete: {match.get('profile_complete')}")
            else:
                print("No AI recommendations found.")
        
        return success, ai_results

    def test_discovery_for_all_users(self):
        """Test discovery for all test users"""
        print("\n🔍 Testing Discovery for All Test Users...")
        
        results = []
        for user in self.test_users:
            user_id = user['user_id']
            print(f"\nTesting discovery for user: {user['username']} (ID: {user_id})")
            
            # Test regular discovery
            success, discover_results = self.test_discovery(user_id)
            
            # Test AI recommendations
            success, ai_results = self.test_ai_recommendations(user_id)
            
            results.append({
                "user_id": user_id,
                "username": user['username'],
                "discover_count": len(discover_results) if success else 0,
                "ai_recommendations_count": len(ai_results) if success else 0
            })
        
        print("\nDiscovery Test Results Summary:")
        for result in results:
            print(f"User: {result['username']}, Discovery: {result['discover_count']}, AI Recommendations: {result['ai_recommendations_count']}")
        
        return results

    def test_discovery_for_real_user(self, user_id):
        """Test discovery for a specific real user ID"""
        print(f"\n🔍 Testing Discovery for Real User ID: {user_id}")
        
        # Get user details
        success, user_data = self.run_test(
            "Get User Details",
            "GET",
            f"user/{user_id}",
            200
        )
        
        if not success:
            print(f"❌ Failed to get user data for ID: {user_id}")
            return False
        
        print(f"User: {user_data.get('username')}")
        print(f"Profile Complete: {user_data.get('profile_complete')}")
        print(f"User Status: {user_data.get('user_status')}")
        print(f"Last Activity: {user_data.get('last_activity')}")
        
        # Test regular discovery
        success, discover_results = self.test_discovery(user_id)
        
        # Test AI recommendations
        success, ai_results = self.test_ai_recommendations(user_id)
        
        return {
            "user_id": user_id,
            "username": user_data.get('username'),
            "profile_complete": user_data.get('profile_complete'),
            "discover_count": len(discover_results) if success else 0,
            "ai_recommendations_count": len(ai_results) if success else 0
        }

    def run_discovery_debug(self, real_user_id=None):
        """Run the complete discovery debug process"""
        print("🚀 Starting Solm8 Discovery Debug")
        
        # Step 1: Check existing users in the database
        print("\n===== STEP 1: CHECK EXISTING USERS =====")
        users, complete_users = self.check_database_users()
        
        # Step 2: Create test users with complete profiles
        print("\n===== STEP 2: CREATE TEST USERS =====")
        self.create_test_users(5)
        
        # Step 3: Test discovery for all test users
        print("\n===== STEP 3: TEST DISCOVERY FOR TEST USERS =====")
        self.test_discovery_for_all_users()
        
        # Step 4: Test discovery for the real user ID if provided
        if real_user_id:
            print(f"\n===== STEP 4: TEST DISCOVERY FOR REAL USER {real_user_id} =====")
            real_user_result = self.test_discovery_for_real_user(real_user_id)
            
            print("\nReal User Discovery Test Result:")
            print(f"User: {real_user_result['username']}")
            print(f"Profile Complete: {real_user_result['profile_complete']}")
            print(f"Discovery Results: {real_user_result['discover_count']}")
            print(f"AI Recommendations: {real_user_result['ai_recommendations_count']}")
        
        print("\n🏁 Discovery Debug Complete")

if __name__ == "__main__":
    debugger = DiscoveryDebugger()
    # Use the real user ID from the review request
    real_user_id = "17d9709a-9a6f-4418-8cb4-765faca422a8"
    debugger.run_discovery_debug(real_user_id)
