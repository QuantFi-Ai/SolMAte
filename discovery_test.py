import requests
import json
import random
import string
from datetime import datetime

class DiscoveryTester:
    def __init__(self, base_url="https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_users = []
        
    def print_separator(self):
        print("\n" + "="*80 + "\n")
        
    def create_test_user(self, profile_complete=True):
        """Create a test user with optional complete profile"""
        print(f"Creating test user (profile_complete={profile_complete})...")
        
        response = requests.post(f"{self.base_url}/api/create-demo-user")
        if response.status_code != 200:
            print(f"❌ Failed to create test user: {response.status_code}")
            return None
            
        user = response.json()
        user_id = user['user_id']
        
        if profile_complete:
            # Update profile to make it complete
            profile_data = {
                "bio": f"Test bio for user {user_id[:6]}",
                "location": "Test Location",
                "trading_experience": "Intermediate",
                "years_trading": 3,
                "preferred_tokens": ["Meme Coins", "DeFi", "NFTs"],
                "trading_style": "Day Trader",
                "portfolio_size": "$10K-$100K",
                "risk_tolerance": "Moderate",
                "looking_for": ["Alpha Sharing", "Research Partner"]
            }
            
            response = requests.put(
                f"{self.base_url}/api/user/{user_id}",
                json=profile_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to update user profile: {response.status_code}")
                return None
                
            # Verify profile was updated and is complete
            response = requests.get(f"{self.base_url}/api/user/{user_id}")
            if response.status_code != 200:
                print(f"❌ Failed to get updated user: {response.status_code}")
                return None
                
            updated_user = response.json()
            if not updated_user.get('profile_complete'):
                print(f"❌ Profile not marked as complete after update")
                return None
                
            print(f"✅ Created user with complete profile: {user['username']}")
        else:
            print(f"✅ Created user with incomplete profile: {user['username']}")
            
        self.test_users.append(user)
        return user
        
    def test_discover_endpoint(self, user_id):
        """Test the discover endpoint"""
        print(f"\nTesting /api/discover/{user_id}...")
        
        response = requests.get(f"{self.base_url}/api/discover/{user_id}")
        if response.status_code != 200:
            print(f"❌ Discover endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
        discover_results = response.json()
        print(f"✅ Discover endpoint returned {len(discover_results)} users")
        
        # Print details about discovered users
        if discover_results:
            print(f"\nDiscovered users:")
            for i, user in enumerate(discover_results[:3]):  # Show first 3 users
                print(f"  {i+1}. {user.get('display_name')} (@{user.get('username')})")
                print(f"     - Profile complete: {user.get('profile_complete')}")
                print(f"     - User status: {user.get('user_status')}")
                
        return True, discover_results
        
    def test_ai_recommendations_endpoint(self, user_id):
        """Test the AI recommendations endpoint"""
        print(f"\nTesting /api/ai-recommendations/{user_id}...")
        
        response = requests.get(f"{self.base_url}/api/ai-recommendations/{user_id}")
        if response.status_code != 200:
            print(f"❌ AI recommendations endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
        recommendations = response.json()
        print(f"✅ AI recommendations endpoint returned {len(recommendations)} users")
        
        # Print details about recommended users
        if recommendations:
            print(f"\nRecommended users:")
            for i, user in enumerate(recommendations[:3]):  # Show first 3 users
                print(f"  {i+1}. {user.get('display_name')} (@{user.get('username')})")
                print(f"     - Compatibility: {user.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                print(f"     - Profile complete: {user.get('profile_complete')}")
                print(f"     - User status: {user.get('user_status')}")
                
        return True, recommendations
        
    def check_database_users(self):
        """Check how many users are in the database and their status"""
        print("\nChecking database users...")
        
        response = requests.get(f"{self.base_url}/api/health")
        if response.status_code != 200:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Get active users
        response = requests.get(f"{self.base_url}/api/users/active")
        if response.status_code != 200:
            print(f"❌ Failed to get active users: {response.status_code}")
            return False
            
        active_users = response.json().get('active_users', [])
        print(f"✅ Found {len(active_users)} active users in the database")
        
        # Get token launchers (as another way to count users)
        response = requests.get(f"{self.base_url}/api/users/token-launchers")
        if response.status_code != 200:
            print(f"❌ Failed to get token launchers: {response.status_code}")
            return False
            
        token_launchers = response.json().get('token_launchers', [])
        print(f"✅ Found {len(token_launchers)} token launchers in the database")
        
        return True
        
    def test_discovery_with_incomplete_profile(self):
        """Test discovery with an incomplete profile"""
        print("\nTesting discovery with incomplete profile...")
        
        # Create user with incomplete profile
        user = self.create_test_user(profile_complete=False)
        if not user:
            return False
            
        # Try to get AI recommendations (should fail)
        response = requests.get(f"{self.base_url}/api/ai-recommendations/{user['user_id']}")
        if response.status_code == 400:
            print(f"✅ AI recommendations correctly rejected incomplete profile with 400 status")
            print(f"   Error: {response.json().get('detail')}")
        else:
            print(f"❌ AI recommendations should reject incomplete profile with 400 status, got {response.status_code}")
            return False
            
        # Try regular discovery (should work but might return empty results)
        success, discover_results = self.test_discover_endpoint(user['user_id'])
        if not success:
            return False
            
        return True
        
    def test_discovery_between_users(self):
        """Test if two users can discover each other"""
        print("\nTesting discovery between two users...")
        
        # Create two users with complete profiles
        user1 = self.create_test_user(profile_complete=True)
        user2 = self.create_test_user(profile_complete=True)
        
        if not user1 or not user2:
            return False
            
        # Check if user1 can discover user2
        success1, discover_results1 = self.test_discover_endpoint(user1['user_id'])
        if not success1:
            return False
            
        user2_found = False
        for user in discover_results1:
            if user.get('user_id') == user2['user_id']:
                user2_found = True
                break
                
        if user2_found:
            print(f"✅ User1 can discover User2")
        else:
            print(f"❌ User1 cannot discover User2")
            
        # Check if user2 can discover user1
        success2, discover_results2 = self.test_discover_endpoint(user2['user_id'])
        if not success2:
            return False
            
        user1_found = False
        for user in discover_results2:
            if user.get('user_id') == user1['user_id']:
                user1_found = True
                break
                
        if user1_found:
            print(f"✅ User2 can discover User1")
        else:
            print(f"❌ User2 cannot discover User1")
            
        return user1_found and user2_found
        
    def test_profile_completion_requirements(self):
        """Test profile completion requirements for discovery"""
        print("\nTesting profile completion requirements...")
        
        # Create a user
        user = self.create_test_user(profile_complete=False)
        if not user:
            return False
            
        # Get the user to check initial profile_complete status
        response = requests.get(f"{self.base_url}/api/user/{user['user_id']}")
        if response.status_code != 200:
            print(f"❌ Failed to get user: {response.status_code}")
            return False
            
        initial_user = response.json()
        print(f"Initial profile_complete status: {initial_user.get('profile_complete')}")
        
        # Test with minimal required fields
        minimal_profile = {
            "trading_experience": "Beginner",
            "preferred_tokens": ["Meme Coins"],
            "trading_style": "HODLer",
            "portfolio_size": "Under $1K"
        }
        
        response = requests.put(
            f"{self.base_url}/api/user/{user['user_id']}",
            json=minimal_profile,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to update minimal profile: {response.status_code}")
            return False
            
        # Check if profile is now complete
        response = requests.get(f"{self.base_url}/api/user/{user['user_id']}")
        if response.status_code != 200:
            print(f"❌ Failed to get updated user: {response.status_code}")
            return False
            
        updated_user = response.json()
        if updated_user.get('profile_complete'):
            print(f"✅ Profile marked as complete with minimal required fields")
        else:
            print(f"❌ Profile not marked as complete with minimal required fields")
            return False
            
        # Now test discovery with the complete profile
        success, discover_results = self.test_discover_endpoint(user['user_id'])
        if not success:
            return False
            
        return True
        
    def run_all_tests(self):
        """Run all discovery tests"""
        print("🚀 Starting SolM8 Discovery System Tests")
        self.print_separator()
        
        # Check database users
        if not self.check_database_users():
            print("❌ Database check failed, stopping tests")
            return False
        self.print_separator()
        
        # Test discovery with incomplete profile
        if not self.test_discovery_with_incomplete_profile():
            print("❌ Incomplete profile test failed, stopping tests")
            return False
        self.print_separator()
        
        # Test profile completion requirements
        if not self.test_profile_completion_requirements():
            print("❌ Profile completion requirements test failed, stopping tests")
            return False
        self.print_separator()
        
        # Test discovery between users
        if not self.test_discovery_between_users():
            print("❌ Discovery between users test failed")
            # Don't stop tests on this failure
        self.print_separator()
        
        # Create a user for AI recommendations test
        user = self.create_test_user(profile_complete=True)
        if not user:
            print("❌ Failed to create user for AI recommendations test, stopping tests")
            return False
            
        # Test AI recommendations
        success, recommendations = self.test_ai_recommendations_endpoint(user['user_id'])
        if not success:
            print("❌ AI recommendations test failed")
            # Don't stop tests on this failure
        self.print_separator()
        
        print("✅ Discovery system tests completed!")
        return True

if __name__ == "__main__":
    tester = DiscoveryTester()
    tester.run_all_tests()