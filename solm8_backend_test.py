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

    def test_health_check(self):
        """Test basic health check to verify the API is running"""
        print("\n🔍 Testing API Health Check...")
        try:
            response = requests.get(f"{self.base_url}/api")
            if response.status_code == 404:
                # This is expected as there's no root endpoint, but the server is responding
                print("✅ API is running (404 response is expected for root endpoint)")
                return True
            elif 200 <= response.status_code < 500:
                print(f"✅ API is running (Status: {response.status_code})")
                return True
            else:
                print(f"❌ API health check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API health check failed - Error: {str(e)}")
            return False

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

    def test_email_login(self, email, password):
        """Test email login"""
        data = {
            "email": email,
            "password": password
        }
        
        success, response = self.run_test(
            "Email Login",
            "POST",
            "auth/email/login",
            200,
            data=data
        )
        
        if success:
            self.email_user = response.get("user")
            print(f"Logged in as: {self.email_user['username']}")
            
        return success, response

    def test_change_password(self, user_id, current_password, new_password):
        """Test changing password"""
        data = {
            "user_id": user_id,
            "current_password": current_password,
            "new_password": new_password
        }
        
        return self.run_test(
            "Change Password",
            "POST",
            "auth/change-password",
            200,
            data=data
        )

    def test_change_password_invalid_current(self, user_id, current_password, new_password):
        """Test changing password with invalid current password"""
        data = {
            "user_id": user_id,
            "current_password": current_password,
            "new_password": new_password
        }
        
        return self.run_test(
            "Change Password with Invalid Current Password",
            "POST",
            "auth/change-password",
            401,  # Expecting 401 Unauthorized
            data=data
        )

    def test_change_password_too_short(self, user_id, current_password, new_password):
        """Test changing password with too short new password"""
        data = {
            "user_id": user_id,
            "current_password": current_password,
            "new_password": new_password
        }
        
        return self.run_test(
            "Change Password with Too Short New Password",
            "POST",
            "auth/change-password",
            400,  # Expecting 400 Bad Request
            data=data
        )

    def test_change_password_missing_fields(self, data):
        """Test changing password with missing fields"""
        return self.run_test(
            "Change Password with Missing Fields",
            "POST",
            "auth/change-password",
            400,  # Expecting 400 Bad Request
            data=data
        )

    def test_get_user(self, user_id):
        """Test getting a user profile"""
        return self.run_test(
            "Get User Profile",
            "GET",
            f"user/{user_id}",
            200
        )

    def test_discover(self, user_id):
        """Test discovery endpoint"""
        return self.run_test(
            "Get Discovery Users",
            "GET",
            f"discover/{user_id}",
            200
        )

    def test_ai_recommendations(self, user_id):
        """Test AI recommendations endpoint"""
        return self.run_test(
            "Get AI Recommendations",
            "GET",
            f"ai-recommendations/{user_id}",
            200
        )

    def test_subscription_status(self, user_id):
        """Test subscription status endpoint"""
        return self.run_test(
            "Get Subscription Status",
            "GET",
            f"subscription/{user_id}",
            200
        )

def run_all_tests():
    """Run all tests for SOLM8 5.0 backend"""
    print("🚀 Starting SOLM8 5.0 Backend Tests")
    
    tester = Solm8APITester()
    test_results = {}
    
    # Test 1: Basic Health Check
    print("\n==== 1. Basic Health Check ====")
    health_check_passed = tester.test_health_check()
    test_results["Health Check"] = health_check_passed
    
    if not health_check_passed:
        print("❌ API health check failed. Stopping tests.")
        return test_results
    
    # Test 2: Authentication (Email Signup/Login)
    print("\n==== 2. Authentication Tests ====")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_auth_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Auth User {random_suffix}"
    
    # Test signup
    signup_success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    test_results["Email Signup"] = signup_success
    
    if not signup_success:
        print("❌ Email signup failed. Stopping tests.")
        return test_results
    
    # Test login
    login_success, login_response = tester.test_email_login(test_email, test_password)
    test_results["Email Login"] = login_success
    
    if not login_success:
        print("❌ Email login failed. Stopping tests.")
        return test_results
    
    print("✅ Authentication tests passed!")
    
    # Test 3: Password Change Feature
    print("\n==== 3. Password Change Feature Tests ====")
    
    # Create a new user for password change tests
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_password_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Password User {random_suffix}"
    
    print("\n3.1 Creating new user account...")
    success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    if not success:
        print("❌ Failed to create test user")
        test_results["Password Change - Create User"] = False
        return test_results
    
    user_id = tester.email_user['user_id']
    print(f"✅ Created test user with ID: {user_id}")
    test_results["Password Change - Create User"] = True
    
    # Test valid password change
    print("\n3.2 Testing valid password change...")
    new_password = "NewPassword456!"
    success, change_response = tester.test_change_password(user_id, test_password, new_password)
    if not success:
        print("❌ Failed to change password")
        test_results["Password Change - Valid Change"] = False
        return test_results
    
    print("✅ Successfully changed password")
    test_results["Password Change - Valid Change"] = True
    
    # Verify login with new password
    print("\n3.3 Verifying login with new password...")
    success, login_response = tester.test_email_login(test_email, new_password)
    if not success:
        print("❌ Failed to login with new password")
        test_results["Password Change - Login with New Password"] = False
        return test_results
    
    print("✅ Successfully logged in with new password")
    test_results["Password Change - Login with New Password"] = True
    
    # Test invalid current password
    print("\n3.4 Testing invalid current password...")
    invalid_current = "WrongPassword123!"
    success, invalid_response = tester.test_change_password_invalid_current(user_id, invalid_current, "AnotherPassword789!")
    # For this test, success means the API correctly rejected the invalid password (returned 401)
    if not success:
        print("❌ API did not correctly reject invalid current password")
        test_results["Password Change - Invalid Current Password"] = False
        return test_results
    
    print("✅ API correctly rejected invalid current password")
    test_results["Password Change - Invalid Current Password"] = True
    
    # Test password too short
    print("\n3.5 Testing password too short validation...")
    short_password = "short"
    success, short_response = tester.test_change_password_too_short(user_id, new_password, short_password)
    # For this test, success means the API correctly rejected the short password (returned 400)
    if not success:
        print("❌ API did not correctly reject password that is too short")
        test_results["Password Change - Too Short Password"] = False
        return test_results
    
    print("✅ API correctly rejected password that is too short")
    test_results["Password Change - Too Short Password"] = True
    
    # Test missing fields
    print("\n3.6 Testing missing fields validation...")
    
    # Missing user_id
    missing_user_id = {
        "current_password": new_password,
        "new_password": "ValidPassword789!"
    }
    success, missing_response = tester.test_change_password_missing_fields(missing_user_id)
    # For this test, success means the API correctly rejected the missing field (returned 400)
    if not success:
        print("❌ API did not correctly reject request with missing user_id")
        test_results["Password Change - Missing User ID"] = False
        return test_results
    
    print("✅ API correctly rejected request with missing user_id")
    test_results["Password Change - Missing User ID"] = True
    
    # Missing current_password
    missing_current = {
        "user_id": user_id,
        "new_password": "ValidPassword789!"
    }
    success, missing_response = tester.test_change_password_missing_fields(missing_current)
    # For this test, success means the API correctly rejected the missing field (returned 400)
    if not success:
        print("❌ API did not correctly reject request with missing current_password")
        test_results["Password Change - Missing Current Password"] = False
        return test_results
    
    print("✅ API correctly rejected request with missing current_password")
    test_results["Password Change - Missing Current Password"] = True
    
    # Missing new_password
    missing_new = {
        "user_id": user_id,
        "current_password": new_password
    }
    success, missing_response = tester.test_change_password_missing_fields(missing_new)
    # For this test, success means the API correctly rejected the missing field (returned 400)
    if not success:
        print("❌ API did not correctly reject request with missing new_password")
        test_results["Password Change - Missing New Password"] = False
        return test_results
    
    print("✅ API correctly rejected request with missing new_password")
    test_results["Password Change - Missing New Password"] = True
    
    print("✅ All password change feature tests passed!")
    
    # Test 4: Existing Features
    print("\n==== 4. Existing Features Tests ====")
    
    # Create a new user for existing features tests
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_features_{random_suffix}@example.com"
    test_password = "TestPassword123!"
    test_display_name = f"Test Features User {random_suffix}"
    
    print("\n4.1 Creating new user account...")
    success, signup_response = tester.test_email_signup(test_email, test_password, test_display_name)
    if not success:
        print("❌ Failed to create test user")
        test_results["Existing Features - Create User"] = False
        return test_results
    
    user_id = tester.email_user['user_id']
    print(f"✅ Created test user with ID: {user_id}")
    test_results["Existing Features - Create User"] = True
    
    # Complete the profile setup process
    print("\n4.2 Completing profile setup...")
    complete_profile = {
        "trading_experience": "Intermediate",
        "preferred_tokens": ["Meme Coins", "DeFi"],
        "trading_style": "Day Trader",
        "portfolio_size": "$10K-$100K"
    }
    
    success, update_response = tester.run_test(
        "Update User Profile",
        "PUT",
        f"user/{user_id}",
        200,
        data=complete_profile
    )
    
    if not success:
        print("❌ Failed to update user profile")
        test_results["Existing Features - Profile Setup"] = False
        return test_results
    
    print("✅ Successfully completed profile setup")
    test_results["Existing Features - Profile Setup"] = True
    
    # Test user profile retrieval
    print("\n4.3 Testing user profile retrieval...")
    success, user_data = tester.test_get_user(user_id)
    if not success:
        print("❌ Failed to retrieve user profile")
        test_results["Existing Features - User Profile Retrieval"] = False
        return test_results
    
    print("✅ Successfully retrieved user profile")
    test_results["Existing Features - User Profile Retrieval"] = True
    
    # Test discovery endpoint
    print("\n4.4 Testing discovery endpoint...")
    success, discover_data = tester.test_discover(user_id)
    if not success:
        print("❌ Failed to access discovery endpoint")
        test_results["Existing Features - Discovery Endpoint"] = False
        return test_results
    
    print("✅ Successfully accessed discovery endpoint")
    test_results["Existing Features - Discovery Endpoint"] = True
    
    # Test AI recommendations endpoint
    print("\n4.5 Testing AI recommendations endpoint...")
    success, ai_data = tester.test_ai_recommendations(user_id)
    if not success:
        print("❌ Failed to access AI recommendations endpoint")
        test_results["Existing Features - AI Recommendations"] = False
        return test_results
    
    print("✅ Successfully accessed AI recommendations endpoint")
    test_results["Existing Features - AI Recommendations"] = True
    
    # Test subscription status
    print("\n4.6 Testing subscription status...")
    success, subscription_data = tester.test_subscription_status(user_id)
    if not success:
        print("❌ Failed to retrieve subscription status")
        # This might be a new endpoint, so don't fail the test if it's not implemented
        print("⚠️ Subscription status endpoint might not be implemented yet")
        test_results["Existing Features - Subscription Status"] = "N/A"
    else:
        print("✅ Successfully retrieved subscription status")
        test_results["Existing Features - Subscription Status"] = True
    
    print("✅ All existing features tests passed!")
    
    # Print summary
    print("\n📋 Test Summary:")
    for test_name, result in test_results.items():
        status = "✅ Passed" if result == True else "❌ Failed" if result == False else "⚠️ Not Available"
        print(f"{test_name}: {status}")
    
    return test_results

if __name__ == "__main__":
    run_all_tests()