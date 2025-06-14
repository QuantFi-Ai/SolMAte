import requests
import random
import string
from datetime import datetime
from pymongo import MongoClient

class MatchCreator:
    def __init__(self, base_url="https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"):
        self.base_url = base_url
        self.mongo_client = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client.solm8_db

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

    def create_test_user(self):
        """Create a new test user"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"test_match_{random_suffix}@example.com"
        password = "TestPassword123!"
        display_name = f"Test Match User {random_suffix}"
        
        data = {
            "email": email,
            "password": password,
            "display_name": display_name
        }
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "auth/email/signup",
            200,
            data=data
        )
        
        if success:
            user = response.get("user")
            print(f"Created test user: {user['display_name']} ({user['user_id']})")
            return user
        
        return None

    def update_user_profile(self, user_id):
        """Update user profile to complete it"""
        complete_profile = {
            "trading_experience": "Intermediate",
            "preferred_tokens": ["Meme Coins", "DeFi"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, _ = self.run_test(
            "Update User Profile",
            "PUT",
            f"user/{user_id}",
            200,
            data=complete_profile
        )
        
        return success

    def create_mutual_swipes(self, user1_id, user2_id):
        """Create mutual swipes between two users"""
        # User 1 swipes on User 2
        success1, _ = self.run_test(
            f"User 1 swipes on User 2",
            "POST",
            "swipe",
            200,
            data={
                "swiper_id": user1_id,
                "target_id": user2_id,
                "action": "like"
            }
        )
        
        # User 2 swipes on User 1
        success2, _ = self.run_test(
            f"User 2 swipes on User 1",
            "POST",
            "swipe",
            200,
            data={
                "swiper_id": user2_id,
                "target_id": user1_id,
                "action": "like"
            }
        )
        
        return success1 and success2

    def check_match_created(self, user1_id, user2_id):
        """Check if a match was created between the two users"""
        match = self.db.matches.find_one({
            "$or": [
                {"user1_id": user1_id, "user2_id": user2_id},
                {"user1_id": user2_id, "user2_id": user1_id}
            ]
        })
        
        if match:
            print(f"✅ Match created with ID: {match['match_id']}")
            return match
        else:
            print("❌ No match found in database")
            return None

    def send_test_message(self, match_id, sender_id, receiver_id):
        """Send a test message in the match"""
        message_data = {
            "match_id": match_id,
            "sender_id": sender_id,
            "content": f"Hello! This is a test message sent at {datetime.utcnow()}"
        }
        
        success, response = self.run_test(
            "Send Test Message",
            "POST",
            "messages",
            200,
            data=message_data
        )
        
        return success, response

    def get_user_matches(self, user_id):
        """Get matches for a user"""
        success, matches = self.run_test(
            "Get User Matches",
            "GET",
            f"matches/{user_id}",
            200
        )
        
        if success:
            print(f"User has {len(matches)} matches")
            for i, match in enumerate(matches):
                other_user = match.get("other_user", {})
                print(f"{i+1}. Match with: {other_user.get('display_name')} ({other_user.get('user_id')})")
        
        return success, matches

    def create_test_match_for_user(self, target_user_id):
        """Create a complete test match for the target user"""
        print(f"\n🔍 Creating Test Match for User ID: {target_user_id}")
        
        # Step 1: Create a new test user
        test_user = self.create_test_user()
        if not test_user:
            print("❌ Failed to create test user")
            return False
        
        test_user_id = test_user["user_id"]
        
        # Step 2: Complete the test user's profile
        if not self.update_user_profile(test_user_id):
            print("❌ Failed to update test user's profile")
            return False
        
        # Step 3: Create mutual swipes
        if not self.create_mutual_swipes(target_user_id, test_user_id):
            print("❌ Failed to create mutual swipes")
            return False
        
        # Step 4: Check if match was created
        match = self.check_match_created(target_user_id, test_user_id)
        if not match:
            print("❌ Failed to create match")
            return False
        
        # Step 5: Send a test message
        success, _ = self.send_test_message(match["match_id"], test_user_id, target_user_id)
        if not success:
            print("❌ Failed to send test message")
            # Continue anyway, this is not critical
        
        # Step 6: Verify the match appears in the user's matches
        success, matches = self.get_user_matches(target_user_id)
        if not success:
            print("❌ Failed to get user matches")
            return False
        
        # Check if the new match is in the list
        match_found = False
        for m in matches:
            if m.get("match_id") == match["match_id"]:
                match_found = True
                break
        
        if match_found:
            print("✅ New match appears in user's matches list")
        else:
            print("❌ New match does not appear in user's matches list")
            return False
        
        print("\n✅ Successfully created test match for user")
        return True

def main():
    creator = MatchCreator()
    
    # Create a test match for the specified user
    target_user_id = "17d9709a-9a6f-4418-8cb4-765faca422a8"
    creator.create_test_match_for_user(target_user_id)

if __name__ == "__main__":
    main()
