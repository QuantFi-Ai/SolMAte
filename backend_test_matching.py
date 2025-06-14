import requests
import unittest
import uuid
import os
import time
import json
import random
import string
from datetime import datetime
from pymongo import MongoClient

class Solm8MatchingTester:
    def __init__(self, base_url="https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.email_user = None
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

    def test_swipe(self, swiper_id, target_id, action="like"):
        """Test swiping on a user"""
        data = {
            "swiper_id": swiper_id,
            "target_id": target_id,
            "action": action
        }
        
        return self.run_test(
            f"User {swiper_id} swipes {action} on User {target_id}",
            "POST",
            "swipe",
            200,
            data=data
        )

    def test_get_matches(self, user_id):
        """Test getting matches for a user"""
        return self.run_test(
            f"Get matches for User {user_id}",
            "GET",
            f"matches/{user_id}",
            200
        )

    def test_send_message(self, match_id, sender_id, content):
        """Test sending a message in a match"""
        data = {
            "match_id": match_id,
            "sender_id": sender_id,
            "content": content
        }
        
        return self.run_test(
            f"Send message in match {match_id}",
            "POST",
            "messages",
            200,
            data=data
        )

    def test_get_messages(self, match_id):
        """Test getting messages for a match"""
        return self.run_test(
            f"Get messages for match {match_id}",
            "GET",
            f"messages/{match_id}",
            200
        )

    def check_demo_users_in_database(self):
        """Check for demo users in the database"""
        print("\n🔍 Checking for Demo Users in Database...")
        
        # Get all users
        users = list(self.db.users.find())
        total_users = len(users)
        
        # Count users by auth method
        auth_methods = {}
        for user in users:
            auth_method = user.get('auth_method', 'none')
            auth_methods[auth_method] = auth_methods.get(auth_method, 0) + 1
        
        # Look for demo users
        demo_users = [user for user in users if user.get('auth_method') == 'demo']
        suspicious_usernames = []
        
        for user in users:
            username = user.get('username', '')
            if (username.startswith('demo_') or 
                username.startswith('crypto_whale_') or 
                username.startswith('sol_degen_') or
                'demo' in username.lower() or
                'test' in username.lower()):
                suspicious_usernames.append({
                    'user_id': user.get('user_id'),
                    'username': username,
                    'auth_method': user.get('auth_method'),
                    'profile_complete': user.get('profile_complete', False)
                })
        
        print(f"Total users in database: {total_users}")
        print(f"Users by auth method: {auth_methods}")
        print(f"Demo users count: {len(demo_users)}")
        print(f"Suspicious usernames count: {len(suspicious_usernames)}")
        
        if suspicious_usernames:
            print("\nSuspicious usernames found:")
            for user in suspicious_usernames[:10]:  # Show first 10
                print(f"  User ID: {user['user_id']}, Username: {user['username']}, Auth Method: {user['auth_method']}")
            
            if len(suspicious_usernames) > 10:
                print(f"  ... and {len(suspicious_usernames) - 10} more")
        
        return demo_users, suspicious_usernames

    def check_swipes_collection(self):
        """Check the swipes collection for inconsistencies"""
        print("\n🔍 Checking Swipes Collection...")
        
        swipes = list(self.db.swipes.find())
        print(f"Total swipes in database: {len(swipes)}")
        
        # Count swipes by action
        actions = {}
        for swipe in swipes:
            action = swipe.get('action', 'unknown')
            actions[action] = actions.get(action, 0) + 1
        
        print(f"Swipes by action: {actions}")
        
        # Check for duplicate swipes (same swiper_id and target_id)
        swiper_target_pairs = {}
        duplicates = []
        
        for swipe in swipes:
            swiper_id = swipe.get('swiper_id')
            target_id = swipe.get('target_id')
            pair_key = f"{swiper_id}_{target_id}"
            
            if pair_key in swiper_target_pairs:
                duplicates.append({
                    'swiper_id': swiper_id,
                    'target_id': target_id,
                    'count': swiper_target_pairs[pair_key] + 1
                })
                swiper_target_pairs[pair_key] += 1
            else:
                swiper_target_pairs[pair_key] = 1
        
        if duplicates:
            print("\nDuplicate swipes found:")
            for dup in duplicates[:10]:  # Show first 10
                print(f"  Swiper: {dup['swiper_id']}, Target: {dup['target_id']}, Count: {dup['count']}")
            
            if len(duplicates) > 10:
                print(f"  ... and {len(duplicates) - 10} more")
        else:
            print("No duplicate swipes found")
        
        return swipes, duplicates

    def check_matches_collection(self):
        """Check the matches collection for inconsistencies"""
        print("\n🔍 Checking Matches Collection...")
        
        matches = list(self.db.matches.find())
        print(f"Total matches in database: {len(matches)}")
        
        # Check for orphaned matches (where one or both users don't exist)
        orphaned_matches = []
        for match in matches:
            user1_id = match.get('user1_id')
            user2_id = match.get('user2_id')
            
            user1 = self.db.users.find_one({"user_id": user1_id})
            user2 = self.db.users.find_one({"user_id": user2_id})
            
            if not user1 or not user2:
                orphaned_matches.append({
                    'match_id': match.get('match_id'),
                    'user1_exists': bool(user1),
                    'user2_exists': bool(user2)
                })
        
        if orphaned_matches:
            print("\nOrphaned matches found:")
            for match in orphaned_matches[:10]:  # Show first 10
                print(f"  Match ID: {match['match_id']}, User1 Exists: {match['user1_exists']}, User2 Exists: {match['user2_exists']}")
            
            if len(orphaned_matches) > 10:
                print(f"  ... and {len(orphaned_matches) - 10} more")
        else:
            print("No orphaned matches found")
        
        # Check for matches without corresponding mutual likes in swipes
        inconsistent_matches = []
        for match in matches:
            user1_id = match.get('user1_id')
            user2_id = match.get('user2_id')
            
            # Check if both users liked each other
            user1_liked_user2 = self.db.swipes.find_one({
                "swiper_id": user1_id,
                "target_id": user2_id,
                "action": "like"
            })
            
            user2_liked_user1 = self.db.swipes.find_one({
                "swiper_id": user2_id,
                "target_id": user1_id,
                "action": "like"
            })
            
            if not user1_liked_user2 or not user2_liked_user1:
                inconsistent_matches.append({
                    'match_id': match.get('match_id'),
                    'user1_liked_user2': bool(user1_liked_user2),
                    'user2_liked_user1': bool(user2_liked_user1)
                })
        
        if inconsistent_matches:
            print("\nInconsistent matches found (missing mutual likes):")
            for match in inconsistent_matches[:10]:  # Show first 10
                print(f"  Match ID: {match['match_id']}, User1 liked User2: {match['user1_liked_user2']}, User2 liked User1: {match['user2_liked_user1']}")
            
            if len(inconsistent_matches) > 10:
                print(f"  ... and {len(inconsistent_matches) - 10} more")
        else:
            print("No inconsistent matches found")
        
        return matches, orphaned_matches, inconsistent_matches

    def test_matching_system(self):
        """Test the complete matching system"""
        print("\n===== TESTING MATCHING SYSTEM =====")
        
        # Step 1: Create two test users
        print("\n1️⃣ Creating two test users...")
        
        # User A
        random_suffix_a = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_a = f"test_match_a_{random_suffix_a}@example.com"
        display_name_a = f"Test Match User A {random_suffix_a}"
        
        success, signup_response_a = self.test_email_signup(email_a, "TestPassword123!", display_name_a)
        if not success:
            print("❌ Failed to create User A")
            return False
        
        user_a_id = self.email_user['user_id']
        
        # User B
        random_suffix_b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email_b = f"test_match_b_{random_suffix_b}@example.com"
        display_name_b = f"Test Match User B {random_suffix_b}"
        
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
        
        # Step 3: User A swipes right on User B
        print("\n3️⃣ User A swipes right on User B...")
        success, swipe_response_a = self.test_swipe(user_a_id, user_b_id, "like")
        if not success:
            print("❌ Failed when User A swiped on User B")
            return False
        
        print(f"Swipe response: {swipe_response_a}")
        
        # Step 4: Check if a match was created (should not be yet)
        print("\n4️⃣ Checking if a match was created (should not be yet)...")
        success, matches_a = self.test_get_matches(user_a_id)
        if not success:
            print("❌ Failed to get matches for User A")
            return False
        
        if matches_a and len(matches_a) > 0:
            print("❌ User A has matches before User B swiped (unexpected)")
            print(f"Matches: {matches_a}")
            return False
        
        print("✅ User A has no matches yet (as expected)")
        
        # Step 5: User B swipes right on User A
        print("\n5️⃣ User B swipes right on User A...")
        success, swipe_response_b = self.test_swipe(user_b_id, user_a_id, "like")
        if not success:
            print("❌ Failed when User B swiped on User A")
            return False
        
        print(f"Swipe response: {swipe_response_b}")
        
        # Step 6: Check if a match was created for User A
        print("\n6️⃣ Checking if a match was created for User A...")
        success, matches_a = self.test_get_matches(user_a_id)
        if not success:
            print("❌ Failed to get matches for User A")
            return False
        
        if not matches_a or len(matches_a) == 0:
            print("❌ User A has no matches after mutual likes (unexpected)")
            return False
        
        print(f"✅ User A has {len(matches_a)} match(es)")
        
        # Step 7: Check if a match was created for User B
        print("\n7️⃣ Checking if a match was created for User B...")
        success, matches_b = self.test_get_matches(user_b_id)
        if not success:
            print("❌ Failed to get matches for User B")
            return False
        
        if not matches_b or len(matches_b) == 0:
            print("❌ User B has no matches after mutual likes (unexpected)")
            return False
        
        print(f"✅ User B has {len(matches_b)} match(es)")
        
        # Step 8: Verify the match is the same for both users
        print("\n8️⃣ Verifying the match is the same for both users...")
        
        match_a = matches_a[0] if matches_a else None
        match_b = matches_b[0] if matches_b else None
        
        if not match_a or not match_b:
            print("❌ One or both users have no matches")
            return False
        
        if match_a.get('match_id') == match_b.get('match_id'):
            print(f"✅ Both users have the same match ID: {match_a.get('match_id')}")
        else:
            print("❌ Users have different match IDs")
            print(f"User A match ID: {match_a.get('match_id')}")
            print(f"User B match ID: {match_b.get('match_id')}")
            return False
        
        # Step 9: Verify User A can see User B in their matches
        print("\n9️⃣ Verifying User A can see User B in their matches...")
        
        other_user_a = match_a.get('other_user', {})
        if other_user_a.get('user_id') == user_b_id:
            print(f"✅ User A can see User B in their matches")
        else:
            print("❌ User A cannot see User B in their matches")
            print(f"Expected User B ID: {user_b_id}")
            print(f"Actual other user ID: {other_user_a.get('user_id')}")
            return False
        
        # Step 10: Verify User B can see User A in their matches
        print("\n🔟 Verifying User B can see User A in their matches...")
        
        other_user_b = match_b.get('other_user', {})
        if other_user_b.get('user_id') == user_a_id:
            print(f"✅ User B can see User A in their matches")
        else:
            print("❌ User B cannot see User A in their matches")
            print(f"Expected User A ID: {user_a_id}")
            print(f"Actual other user ID: {other_user_b.get('user_id')}")
            return False
        
        # Step 11: Test sending a message from User A to User B
        print("\n1️⃣1️⃣ Testing sending a message from User A to User B...")
        
        match_id = match_a.get('match_id')
        message_content = f"Hello from User A! {random.randint(1000, 9999)}"
        
        success, message_response = self.test_send_message(match_id, user_a_id, message_content)
        if not success:
            print("❌ Failed to send message from User A to User B")
            return False
        
        print(f"✅ Message sent successfully: {message_response.get('content')}")
        
        # Step 12: Test getting messages for the match
        print("\n1️⃣2️⃣ Testing getting messages for the match...")
        
        success, messages = self.test_get_messages(match_id)
        if not success:
            print("❌ Failed to get messages for the match")
            return False
        
        if not messages or len(messages) == 0:
            print("❌ No messages found for the match")
            return False
        
        print(f"✅ Found {len(messages)} message(s) for the match")
        
        # Verify the message content
        last_message = messages[-1] if messages else None
        if last_message and last_message.get('content') == message_content:
            print(f"✅ Message content matches: {last_message.get('content')}")
        else:
            print("❌ Message content does not match")
            print(f"Expected: {message_content}")
            print(f"Actual: {last_message.get('content') if last_message else 'No message'}")
            return False
        
        # Step 13: Test sending a message from User B to User A
        print("\n1️⃣3️⃣ Testing sending a message from User B to User A...")
        
        message_content_b = f"Hello from User B! {random.randint(1000, 9999)}"
        
        success, message_response_b = self.test_send_message(match_id, user_b_id, message_content_b)
        if not success:
            print("❌ Failed to send message from User B to User A")
            return False
        
        print(f"✅ Message sent successfully: {message_response_b.get('content')}")
        
        # Step 14: Test getting messages again to verify both messages
        print("\n1️⃣4️⃣ Testing getting messages again to verify both messages...")
        
        success, messages_updated = self.test_get_messages(match_id)
        if not success:
            print("❌ Failed to get updated messages for the match")
            return False
        
        if not messages_updated or len(messages_updated) < 2:
            print("❌ Expected at least 2 messages, but found fewer")
            return False
        
        print(f"✅ Found {len(messages_updated)} message(s) for the match")
        
        # Verify the second message content
        last_message_updated = messages_updated[-1] if messages_updated else None
        if last_message_updated and last_message_updated.get('content') == message_content_b:
            print(f"✅ Second message content matches: {last_message_updated.get('content')}")
        else:
            print("❌ Second message content does not match")
            print(f"Expected: {message_content_b}")
            print(f"Actual: {last_message_updated.get('content') if last_message_updated else 'No message'}")
            return False
        
        print("\n✅ MATCHING SYSTEM TEST COMPLETED SUCCESSFULLY")
        return True

    def test_asymmetric_matching(self):
        """Test for asymmetric matching issues"""
        print("\n===== TESTING FOR ASYMMETRIC MATCHING ISSUES =====")
        
        # Step 1: Check the database for existing matches
        print("\n1️⃣ Checking database for existing matches...")
        
        matches = list(self.db.matches.find())
        print(f"Found {len(matches)} existing matches in the database")
        
        # Step 2: For each match, check if both users can see each other
        print("\n2️⃣ Checking if both users in each match can see each other...")
        
        asymmetric_matches = []
        
        for i, match in enumerate(matches[:10]):  # Check first 10 matches
            match_id = match.get('match_id')
            user1_id = match.get('user1_id')
            user2_id = match.get('user2_id')
            
            print(f"\nChecking match {i+1}/{min(10, len(matches))}: {match_id}")
            print(f"User1: {user1_id}, User2: {user2_id}")
            
            # Check if User1 can see User2 in their matches
            success, matches_user1 = self.test_get_matches(user1_id)
            if not success:
                print(f"❌ Failed to get matches for User1 {user1_id}")
                continue
            
            user2_found_in_user1_matches = False
            for user1_match in matches_user1:
                other_user = user1_match.get('other_user', {})
                if other_user.get('user_id') == user2_id:
                    user2_found_in_user1_matches = True
                    break
            
            # Check if User2 can see User1 in their matches
            success, matches_user2 = self.test_get_matches(user2_id)
            if not success:
                print(f"❌ Failed to get matches for User2 {user2_id}")
                continue
            
            user1_found_in_user2_matches = False
            for user2_match in matches_user2:
                other_user = user2_match.get('other_user', {})
                if other_user.get('user_id') == user1_id:
                    user1_found_in_user2_matches = True
                    break
            
            # Report results
            if user2_found_in_user1_matches and user1_found_in_user2_matches:
                print(f"✅ Match is symmetric - both users can see each other")
            else:
                print(f"❌ Match is asymmetric:")
                print(f"  User1 can see User2: {user2_found_in_user1_matches}")
                print(f"  User2 can see User1: {user1_found_in_user2_matches}")
                
                asymmetric_matches.append({
                    'match_id': match_id,
                    'user1_id': user1_id,
                    'user2_id': user2_id,
                    'user1_can_see_user2': user2_found_in_user1_matches,
                    'user2_can_see_user1': user1_found_in_user2_matches
                })
        
        # Step 3: Report findings
        print("\n3️⃣ Asymmetric matching test results:")
        
        if asymmetric_matches:
            print(f"❌ Found {len(asymmetric_matches)} asymmetric matches")
            for i, match in enumerate(asymmetric_matches):
                print(f"\nAsymmetric Match {i+1}:")
                print(f"  Match ID: {match['match_id']}")
                print(f"  User1 ID: {match['user1_id']}")
                print(f"  User2 ID: {match['user2_id']}")
                print(f"  User1 can see User2: {match['user1_can_see_user2']}")
                print(f"  User2 can see User1: {match['user2_can_see_user1']}")
        else:
            print(f"✅ No asymmetric matches found in the sample")
        
        return asymmetric_matches

    def run_matching_system_tests(self):
        """Run all tests related to the matching system"""
        print("🚀 Starting Solm8 Matching System Tests")
        
        # Step 1: Check for demo users in the database
        print("\n===== STEP 1: CHECK FOR DEMO USERS =====")
        demo_users, suspicious_usernames = self.check_demo_users_in_database()
        
        # Step 2: Check swipes collection for inconsistencies
        print("\n===== STEP 2: CHECK SWIPES COLLECTION =====")
        swipes, duplicate_swipes = self.check_swipes_collection()
        
        # Step 3: Check matches collection for inconsistencies
        print("\n===== STEP 3: CHECK MATCHES COLLECTION =====")
        matches, orphaned_matches, inconsistent_matches = self.check_matches_collection()
        
        # Step 4: Test for asymmetric matching issues
        print("\n===== STEP 4: TEST FOR ASYMMETRIC MATCHING =====")
        asymmetric_matches = self.test_asymmetric_matching()
        
        # Step 5: Test the complete matching system
        print("\n===== STEP 5: TEST COMPLETE MATCHING SYSTEM =====")
        matching_system_works = self.test_matching_system()
        
        # Print summary
        print("\n📊 MATCHING SYSTEM TEST SUMMARY:")
        print(f"Demo Users Found: {len(demo_users)}")
        print(f"Suspicious Usernames Found: {len(suspicious_usernames)}")
        print(f"Duplicate Swipes Found: {len(duplicate_swipes)}")
        print(f"Orphaned Matches Found: {len(orphaned_matches)}")
        print(f"Inconsistent Matches Found: {len(inconsistent_matches)}")
        print(f"Asymmetric Matches Found: {len(asymmetric_matches)}")
        print(f"Complete Matching System Test: {'✅ PASSED' if matching_system_works else '❌ FAILED'}")
        
        # Overall assessment
        issues_found = (
            len(demo_users) > 0 or
            len(suspicious_usernames) > 0 or
            len(duplicate_swipes) > 0 or
            len(orphaned_matches) > 0 or
            len(inconsistent_matches) > 0 or
            len(asymmetric_matches) > 0 or
            not matching_system_works
        )
        
        if issues_found:
            print("\n❌ ISSUES FOUND IN THE MATCHING SYSTEM")
            
            if len(demo_users) > 0 or len(suspicious_usernames) > 0:
                print("- Demo/test users found in the database that may be affecting matching")
            
            if len(duplicate_swipes) > 0:
                print("- Duplicate swipes found that may cause inconsistent matching")
            
            if len(orphaned_matches) > 0:
                print("- Orphaned matches found (matches where one or both users don't exist)")
            
            if len(inconsistent_matches) > 0:
                print("- Inconsistent matches found (matches without corresponding mutual likes)")
            
            if len(asymmetric_matches) > 0:
                print("- Asymmetric matches found (one user can see the match but the other can't)")
            
            if not matching_system_works:
                print("- The matching system test failed - new matches may not be working correctly")
        else:
            print("\n✅ NO ISSUES FOUND IN THE MATCHING SYSTEM")
        
        return not issues_found

if __name__ == "__main__":
    tester = Solm8MatchingTester()
    tester.run_matching_system_tests()
