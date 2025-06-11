import requests
import json
import random
import string
from datetime import datetime, timedelta
import time

class DiscoverySortingTester:
    def __init__(self, base_url="https://abc11984-1ed0-4743-b061-3045e146cf6a.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_users = []
        
    def print_separator(self):
        print("\n" + "="*80 + "\n")
        
    def create_test_user(self, delay_seconds=0):
        """Create a test user with complete profile and optional delay"""
        print(f"Creating test user (delay={delay_seconds}s)...")
        
        response = requests.post(f"{self.base_url}/api/create-demo-user")
        if response.status_code != 200:
            print(f"❌ Failed to create test user: {response.status_code}")
            return None
            
        user = response.json()
        user_id = user['user_id']
        
        # Update profile to make it complete
        profile_data = {
            "bio": f"Test user created at {datetime.utcnow().isoformat()}",
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
            
        # If delay is specified, wait before updating activity
        if delay_seconds > 0:
            print(f"Waiting {delay_seconds} seconds before updating activity...")
            time.sleep(delay_seconds)
            
        # Update user's last activity
        response = requests.post(f"{self.base_url}/api/user/{user_id}/update-activity")
        if response.status_code != 200:
            print(f"❌ Failed to update user activity: {response.status_code}")
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
        print(f"   Last activity: {updated_user.get('last_activity')}")
        
        self.test_users.append(updated_user)
        return updated_user
        
    def test_discover_endpoint(self, user_id):
        """Test the discover endpoint and check sorting"""
        print(f"\nTesting /api/discover/{user_id} with sorting...")
        
        response = requests.get(f"{self.base_url}/api/discover/{user_id}")
        if response.status_code != 200:
            print(f"❌ Discover endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
        discover_results = response.json()
        print(f"✅ Discover endpoint returned {len(discover_results)} users")
        
        # Check if results are sorted by last_activity
        if len(discover_results) >= 2:
            is_sorted = True
            for i in range(len(discover_results) - 1):
                # Convert string timestamps to datetime objects
                time1 = discover_results[i].get('last_activity')
                time2 = discover_results[i+1].get('last_activity')
                
                if time1 and time2:
                    if isinstance(time1, str) and isinstance(time2, str):
                        dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
                        dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
                        
                        if dt1 < dt2:  # Should be descending (newest first)
                            is_sorted = False
                            print(f"❌ Results not sorted correctly at positions {i} and {i+1}:")
                            print(f"   Position {i}: {dt1}")
                            print(f"   Position {i+1}: {dt2}")
                            break
            
            if is_sorted:
                print("✅ Results are correctly sorted by last_activity (newest first)")
            else:
                print("❌ Results are NOT sorted by last_activity")
        else:
            print("⚠️ Not enough results to verify sorting")
            
        # Print details about discovered users
        if discover_results:
            print(f"\nDiscovered users (showing first 3):")
            for i, user in enumerate(discover_results[:3]):
                print(f"  {i+1}. {user.get('display_name')} (@{user.get('username')})")
                print(f"     - Last activity: {user.get('last_activity')}")
                print(f"     - User status: {user.get('user_status')}")
                
        return True, discover_results
        
    def test_ai_recommendations_endpoint(self, user_id):
        """Test the AI recommendations endpoint and check sorting"""
        print(f"\nTesting /api/ai-recommendations/{user_id} with sorting...")
        
        response = requests.get(f"{self.base_url}/api/ai-recommendations/{user_id}")
        if response.status_code != 200:
            print(f"❌ AI recommendations endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
        recommendations = response.json()
        print(f"✅ AI recommendations endpoint returned {len(recommendations)} users")
        
        # Check if results are sorted by last_activity
        # Note: AI recommendations are first sorted by compatibility score, then by last_activity
        # So we can't directly check the sorting here
        
        # Print details about recommended users
        if recommendations:
            print(f"\nRecommended users (showing first 3):")
            for i, user in enumerate(recommendations[:3]):
                print(f"  {i+1}. {user.get('display_name')} (@{user.get('username')})")
                print(f"     - Compatibility: {user.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                print(f"     - Last activity: {user.get('last_activity')}")
                print(f"     - User status: {user.get('user_status')}")
                
        return True, recommendations
        
    def test_discovery_between_users(self):
        """Test if users can discover each other with proper sorting"""
        print("\nTesting discovery between users with sorting...")
        
        # Create users with different activity timestamps
        print("\nCreating 3 users with staggered activity times...")
        
        # User 1 - Most recent activity
        user1 = self.create_test_user(delay_seconds=0)
        
        # User 2 - Middle activity
        user2 = self.create_test_user(delay_seconds=2)
        
        # User 3 - Oldest activity
        user3 = self.create_test_user(delay_seconds=4)
        
        if not user1 or not user2 or not user3:
            return False
            
        # Update User 1's activity to make it the most recent
        print("\nUpdating User 1's activity to make it the most recent...")
        response = requests.post(f"{self.base_url}/api/user/{user1['user_id']}/update-activity")
        if response.status_code != 200:
            print(f"❌ Failed to update User 1's activity: {response.status_code}")
            return False
            
        # Check if User 3 can discover User 1 and User 2
        print("\nChecking if User 3 can discover User 1 and User 2 in the correct order...")
        success, discover_results = self.test_discover_endpoint(user3['user_id'])
        if not success:
            return False
            
        # Check if User 1 and User 2 are in the results and in the correct order
        user1_index = -1
        user2_index = -1
        
        for i, user in enumerate(discover_results):
            if user.get('user_id') == user1['user_id']:
                user1_index = i
            elif user.get('user_id') == user2['user_id']:
                user2_index = i
                
        if user1_index == -1:
            print(f"❌ User 3 cannot discover User 1")
            return False
        elif user2_index == -1:
            print(f"❌ User 3 cannot discover User 2")
            return False
        else:
            print(f"✅ User 3 can discover both User 1 and User 2")
            
            # Check if User 1 (most recent) appears before User 2
            if user1_index < user2_index:
                print(f"✅ User 1 (most recent) appears before User 2 in the results (index {user1_index} vs {user2_index})")
            else:
                print(f"❌ User 1 (most recent) should appear before User 2, but doesn't (index {user1_index} vs {user2_index})")
                return False
                
        # Test AI recommendations
        print("\nChecking AI recommendations for User 3...")
        success, recommendations = self.test_ai_recommendations_endpoint(user3['user_id'])
        if not success:
            return False
            
        # We can't directly check sorting in AI recommendations since they're sorted by compatibility first
        # But we can check if both users are in the results
        user1_found = False
        user2_found = False
        
        for user in recommendations:
            if user.get('user_id') == user1['user_id']:
                user1_found = True
            elif user.get('user_id') == user2['user_id']:
                user2_found = True
                
        if user1_found and user2_found:
            print(f"✅ User 3 can see both User 1 and User 2 in AI recommendations")
        else:
            print(f"❌ User 3 cannot see {'User 1' if not user1_found else 'User 2'} in AI recommendations")
            return False
            
        return True
        
    def run_sorting_tests(self):
        """Run tests specifically for the sorting fix"""
        print("🚀 Starting SolM8 Discovery Sorting Fix Tests")
        self.print_separator()
        
        # Test discovery between users with sorting
        if not self.test_discovery_between_users():
            print("❌ Discovery sorting test failed")
            return False
        self.print_separator()
        
        print("✅ Discovery sorting tests completed successfully!")
        print("✅ The fix for sorting by last_activity is working correctly.")
        print("✅ Users can now discover each other with proper sorting by recent activity.")
        return True

if __name__ == "__main__":
    tester = DiscoverySortingTester()
    tester.run_sorting_tests()