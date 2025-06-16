import requests
import unittest
import uuid
import os
import tempfile
import time
import json
import random
import string
from datetime import datetime, timedelta
from pymongo import MongoClient

class Solm8APITester:
    def __init__(self, base_url="https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com"):
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

    def test_get_user(self, user_id):
        """Test getting a user profile"""
        return self.run_test(
            "Get User Profile",
            "GET",
            f"user/{user_id}",
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
        return self.run_test(
            f"Swipe {action} on User",
            "POST",
            "swipe",
            200,
            data={
                "swiper_id": swiper_id,
                "target_id": target_id,
                "action": action
            }
        )

def test_pro_trader_features():
    """Test the Pro Trader premium features"""
    print("\n🔍 Testing Pro Trader Premium Features...")
    tester = Solm8APITester()
    
    # Step 1: Create a new user account with email signup
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_pro_trader_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Pro Trader {random_suffix}"
    
    print("\n1️⃣ Creating new user account...")
    success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    if not success:
        print("❌ Failed to create test user")
        return False
    
    user_id = tester.email_user['user_id']
    print(f"✅ Created test user with ID: {user_id}")
    
    # Step 2: Complete the profile setup process
    print("\n2️⃣ Completing profile setup...")
    complete_profile = {
        "bio": "I'm a professional crypto trader.",
        "location": "Crypto Valley",
        "trading_experience": "Expert",
        "years_trading": 5,
        "preferred_tokens": ["DeFi", "NFTs", "Blue Chips"],
        "trading_style": "Day Trader",
        "portfolio_size": "$100K+",
        "risk_tolerance": "Aggressive",
        "best_trade": "Bought SOL at $1, sold at $250",
        "worst_trade": "Missed the BONK pump",
        "favorite_project": "Solana",
        "trading_hours": "24/7",
        "communication_style": "Professional",
        "preferred_communication_platform": "Discord",
        "preferred_trading_platform": "Jupiter",
        "looking_for": ["Alpha Sharing", "Research Partner"]
    }
    
    success, update_response = tester.test_update_user_profile(user_id, complete_profile)
    if not success:
        print("❌ Failed to update user profile")
        return False
    
    print("✅ Successfully completed profile setup")
    
    # Step 3: Upgrade user to Pro Trader plan
    print("\n3️⃣ Upgrading user to Pro Trader plan...")
    success, upgrade_response = tester.run_test(
        "Upgrade to Pro Trader",
        "POST",
        f"subscription/upgrade/{user_id}",
        200,
        data={"plan_type": "pro_trader"}
    )
    
    if not success:
        print("❌ Failed to upgrade to Pro Trader")
        return False
    
    print("✅ Successfully upgraded to Pro Trader")
    print(f"Features unlocked: {upgrade_response.get('features_unlocked', [])}")
    
    # Step 4: Test portfolio connection (Pro Trader feature)
    print("\n4️⃣ Testing portfolio connection...")
    wallet_address = "8ZU6Pah9XUzRrHZsJ8mBav7xbT7VmCgaJiUy8xpqRNAB"
    
    success, portfolio_response = tester.run_test(
        "Connect Portfolio",
        "POST",
        f"portfolio/connect/{user_id}",
        200,
        data={"wallet_address": wallet_address, "exchange_name": "Phantom"}
    )
    
    if not success:
        print("❌ Failed to connect portfolio")
        return False
    
    print("✅ Successfully connected portfolio")
    
    # Step 5: Verify portfolio connection
    print("\n5️⃣ Verifying portfolio connection...")
    success, portfolio_info = tester.run_test(
        "Get Portfolio Info",
        "GET",
        f"portfolio/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to get portfolio info")
        return False
    
    if portfolio_info.get("wallet_address") != wallet_address:
        print(f"❌ Portfolio wallet address mismatch. Expected: {wallet_address}, Got: {portfolio_info.get('wallet_address')}")
        return False
    
    print("✅ Portfolio connection verified")
    
    # Step 6: Create a second user to test trading signals and groups
    print("\n6️⃣ Creating a second user for testing signals and groups...")
    random_suffix2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email2 = f"test_trader2_{random_suffix2}@example.com"
    test_password2 = "TestPassword123!"
    test_display_name2 = f"Test Trader 2 {random_suffix2}"
    
    success, signup_response2 = tester.test_email_signup(test_email2, test_password2, test_display_name2)
    if not success:
        print("❌ Failed to create second test user")
        return False
    
    user_id2 = tester.email_user['user_id']
    print(f"✅ Created second test user with ID: {user_id2}")
    
    # Complete the second user's profile
    complete_profile2 = {
        "trading_experience": "Intermediate",
        "preferred_tokens": ["Meme Coins", "GameFi"],
        "trading_style": "Swing Trader",
        "portfolio_size": "$10K-$100K"
    }
    
    success, _ = tester.test_update_user_profile(user_id2, complete_profile2)
    if not success:
        print("❌ Failed to update second user's profile")
        return False
    
    # Create a match between the two users
    success, _ = tester.test_swipe(user_id, user_id2, "like")
    success, _ = tester.test_swipe(user_id2, user_id, "like")
    
    # Step 7: Test sending trading signals
    print("\n7️⃣ Testing trading signal sending...")
    signal_data = {
        "sender_id": user_id,
        "recipient_ids": [user_id2],
        "signal_type": "entry",
        "token_symbol": "SOL",
        "price_target": 150.0,
        "stop_loss": 120.0,
        "risk_level": "medium",
        "message": "SOL looking bullish, entry at current price with target of $150"
    }
    
    success, signal_response = tester.run_test(
        "Send Trading Signal",
        "POST",
        "trading-signal/send",
        200,
        data=signal_data
    )
    
    if not success:
        print("❌ Failed to send trading signal")
        return False
    
    print("✅ Successfully sent trading signal")
    
    # Step 8: Verify trading signals
    print("\n8️⃣ Verifying trading signals...")
    success, sent_signals = tester.run_test(
        "Get Sent Trading Signals",
        "GET",
        f"trading-signals/{user_id}?signal_type=sent",
        200
    )
    
    if not success:
        print("❌ Failed to get sent trading signals")
        return False
    
    if len(sent_signals["signals"]) == 0:
        print("❌ No sent trading signals found")
        return False
    
    success, received_signals = tester.run_test(
        "Get Received Trading Signals",
        "GET",
        f"trading-signals/{user_id2}",
        200
    )
    
    if not success:
        print("❌ Failed to get received trading signals")
        return False
    
    if len(received_signals["signals"]) == 0:
        print("❌ No received trading signals found")
        return False
    
    print("✅ Trading signals verified")
    
    # Step 9: Test creating trading group
    print("\n9️⃣ Testing trading group creation...")
    group_data = {
        "creator_id": user_id,
        "name": "SOL Traders Elite",
        "description": "A group for serious SOL traders to share alpha",
        "is_private": False
    }
    
    success, group_response = tester.run_test(
        "Create Trading Group",
        "POST",
        "trading-group/create",
        200,
        data=group_data
    )
    
    if not success:
        print("❌ Failed to create trading group")
        return False
    
    group_id = group_response["group"]["group_id"]
    print(f"✅ Successfully created trading group with ID: {group_id}")
    
    # Step 10: Test joining trading group
    print("\n🔟 Testing joining trading group...")
    join_data = {
        "user_id": user_id2
    }
    
    success, join_response = tester.run_test(
        "Join Trading Group",
        "POST",
        f"trading-group/{group_id}/join",
        200,
        data=join_data
    )
    
    if not success:
        print("❌ Failed to join trading group")
        return False
    
    print("✅ Successfully joined trading group")
    
    # Step 11: Verify trading groups
    print("\n1️⃣1️⃣ Verifying trading groups...")
    success, groups_response = tester.run_test(
        "Get User Trading Groups",
        "GET",
        f"trading-groups/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to get user trading groups")
        return False
    
    if len(groups_response["groups"]) == 0:
        print("❌ No trading groups found")
        return False
    
    success, groups_response2 = tester.run_test(
        "Get Second User Trading Groups",
        "GET",
        f"trading-groups/{user_id2}",
        200
    )
    
    if not success:
        print("❌ Failed to get second user trading groups")
        return False
    
    if len(groups_response2["groups"]) == 0:
        print("❌ No trading groups found for second user")
        return False
    
    print("✅ Trading groups verified")
    
    # Step 12: Test scheduling trading event
    print("\n1️⃣2️⃣ Testing trading event scheduling...")
    event_data = {
        "creator_id": user_id,
        "title": "SOL Technical Analysis Session",
        "description": "Let's analyze SOL price action and set up a trading plan",
        "event_type": "trading_session",
        "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "duration_minutes": 60
    }
    
    success, event_response = tester.run_test(
        "Schedule Trading Event",
        "POST",
        "trading-event/schedule",
        200,
        data=event_data
    )
    
    if not success:
        print("❌ Failed to schedule trading event")
        return False
    
    print("✅ Successfully scheduled trading event")
    
    # Step 13: Verify trading events
    print("\n1️⃣3️⃣ Verifying trading events...")
    success, events_response = tester.run_test(
        "Get User Trading Events",
        "GET",
        f"trading-events/{user_id}",
        200
    )
    
    if not success:
        print("❌ Failed to get user trading events")
        return False
    
    if len(events_response["events"]) == 0:
        print("❌ No trading events found")
        return False
    
    print("✅ Trading events verified")
    
    # Step 14: Test Pro Trader features on free user (should return upgrade prompts)
    print("\n1️⃣4️⃣ Testing Pro Trader features on free user (should return upgrade prompts)...")
    
    # Test portfolio connection on free user
    success, free_portfolio_response = tester.run_test(
        "Connect Portfolio (Free User)",
        "POST",
        f"portfolio/connect/{user_id2}",
        200,
        data={"wallet_address": "FreeUserWallet123", "exchange_name": "Phantom"}
    )
    
    if not success:
        print("❌ Failed to get response from portfolio connection endpoint for free user")
        return False
    
    if not free_portfolio_response.get("pro_trader_required"):
        print("❌ Portfolio connection should require Pro Trader for free user")
        return False
    
    # Test sending trading signal on free user
    free_signal_data = {
        "sender_id": user_id2,
        "recipient_ids": [user_id],
        "signal_type": "entry",
        "token_symbol": "SOL",
        "message": "Test signal from free user"
    }
    
    success, free_signal_response = tester.run_test(
        "Send Trading Signal (Free User)",
        "POST",
        "trading-signal/send",
        200,
        data=free_signal_data
    )
    
    if not success:
        print("❌ Failed to get response from trading signal endpoint for free user")
        return False
    
    if not free_signal_response.get("pro_trader_required"):
        print("❌ Sending trading signals should require Pro Trader for free user")
        return False
    
    # Test creating trading group on free user
    free_group_data = {
        "creator_id": user_id2,
        "name": "Free User Group",
        "description": "Test group from free user"
    }
    
    success, free_group_response = tester.run_test(
        "Create Trading Group (Free User)",
        "POST",
        "trading-group/create",
        200,
        data=free_group_data
    )
    
    if not success:
        print("❌ Failed to get response from trading group creation endpoint for free user")
        return False
    
    if not free_group_response.get("pro_trader_required"):
        print("❌ Creating trading groups should require Pro Trader for free user")
        return False
    
    print("✅ All Pro Trader features correctly require upgrade for free users")
    
    print("\n✅ All tests for Pro Trader premium features passed!")
    return True

if __name__ == "__main__":
    test_pro_trader_features()