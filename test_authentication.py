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

class AuthenticationTester:
    def __init__(self, base_url="https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.email_user = None
        self.wallet_user = None
        self.wallet_message = None

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

    # Email Authentication Tests
    
    def test_email_signup(self, email=None, password=None, display_name=None):
        """Test email signup"""
        if not email:
            # Generate random email to avoid conflicts
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"trader_{random_suffix}@solm8.com"
        
        if not password:
            password = "SecurePass123"
            
        if not display_name:
            display_name = f"Test Trader {random_suffix}"
            
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
            
        return success, response, data
    
    def test_email_signup_duplicate(self, email, password="SecurePass123", display_name="Duplicate Test Trader"):
        """Test email signup with duplicate email (should fail)"""
        data = {
            "email": email,
            "password": password,
            "display_name": display_name
        }
        
        # This should fail with 400 status code
        return self.run_test(
            "Email Signup (Duplicate)",
            "POST",
            "auth/email/signup",
            400,
            data=data
        )
    
    def test_email_signup_missing_fields(self):
        """Test email signup with missing fields (should fail)"""
        # Missing password
        data = {
            "email": "missing_fields@solm8.com",
            "display_name": "Missing Fields Trader"
        }
        
        # This should fail with 422 status code (validation error)
        return self.run_test(
            "Email Signup (Missing Fields)",
            "POST",
            "auth/email/signup",
            422,
            data=data
        )
    
    def test_email_login(self, email, password="SecurePass123"):
        """Test email login"""
        data = {
            "email": email,
            "password": password
        }
        
        return self.run_test(
            "Email Login",
            "POST",
            "auth/email/login",
            200,
            data=data
        )
    
    def test_email_login_invalid(self, email, wrong_password="WrongPassword123"):
        """Test email login with invalid credentials (should fail)"""
        data = {
            "email": email,
            "password": wrong_password
        }
        
        # This should fail with 401 status code
        return self.run_test(
            "Email Login (Invalid Credentials)",
            "POST",
            "auth/email/login",
            401,
            data=data
        )
    
    def test_email_login_nonexistent(self):
        """Test email login with non-existent email (should fail)"""
        data = {
            "email": "nonexistent_user@solm8.com",
            "password": "SomePassword123"
        }
        
        # This should fail with 401 status code
        return self.run_test(
            "Email Login (Non-existent User)",
            "POST",
            "auth/email/login",
            401,
            data=data
        )
    
    # Wallet Authentication Tests
    
    def test_get_wallet_message(self):
        """Test getting message for wallet signature"""
        success, response = self.run_test(
            "Get Wallet Message",
            "GET",
            "auth/wallet/message",
            200
        )
        
        if success:
            self.wallet_message = response.get("message")
            print(f"Got wallet message: {self.wallet_message}")
            
        return success, response
    
    def test_wallet_connect(self, wallet_address=None, signature=None, message=None):
        """Test connecting with Solana wallet"""
        if not wallet_address:
            # Generate random wallet address
            wallet_address = ''.join(random.choices(string.ascii_lowercase + string.digits, k=44))
            
        if not signature:
            # Generate random signature
            signature = ''.join(random.choices(string.ascii_lowercase + string.digits, k=88))
            
        if not message:
            message = self.wallet_message or f"Sign this message to authenticate with Solm8: {int(time.time())}"
            
        data = {
            "wallet_address": wallet_address,
            "signature": signature,
            "message": message
        }
        
        success, response = self.run_test(
            "Wallet Connect",
            "POST",
            "auth/wallet/connect",
            200,
            data=data
        )
        
        if success:
            self.wallet_user = response.get("user")
            print(f"Connected wallet user: {self.wallet_user['username']}")
            
        return success, response, data
    
    def test_wallet_connect_duplicate(self, wallet_address, signature=None, message=None):
        """Test connecting with the same wallet address again"""
        if not signature:
            # Generate random signature
            signature = ''.join(random.choices(string.ascii_lowercase + string.digits, k=88))
            
        if not message:
            message = self.wallet_message or f"Sign this message to authenticate with Solm8: {int(time.time())}"
            
        data = {
            "wallet_address": wallet_address,
            "signature": signature,
            "message": message
        }
        
        # This should succeed with 200 status code (existing user login)
        return self.run_test(
            "Wallet Connect (Duplicate)",
            "POST",
            "auth/wallet/connect",
            200,
            data=data
        )
    
    def test_wallet_connect_invalid(self):
        """Test connecting with invalid wallet address (should fail)"""
        data = {
            "wallet_address": "invalid",  # Too short
            "signature": "some_signature",
            "message": "some_message"
        }
        
        # This should fail with 400 status code
        return self.run_test(
            "Wallet Connect (Invalid)",
            "POST",
            "auth/wallet/connect",
            400,
            data=data
        )

    def verify_password_not_exposed(self, user_data):
        """Verify that password is not exposed in user data"""
        if 'password' in user_data or 'password_hash' in user_data:
            print("❌ Password security verification failed - password/hash exposed in API response")
            return False
        else:
            print("✅ Password security verification passed - not exposed in API response")
            self.tests_passed += 1
            self.tests_run += 1
            return True

    def run_authentication_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Solm8 Authentication Tests")
        
        # Email Authentication Tests
        print("\n🔑 Testing Email Authentication...")
        
        # Test email signup with valid data
        success, signup_response, signup_data = self.test_email_signup()
        if not success:
            print("❌ Email signup failed, stopping authentication tests")
            return False
            
        # Verify user was created with correct auth_method
        if self.email_user.get('auth_method') != "email":
            print("❌ Email user auth_method verification failed - expected 'email'")
            self.tests_run += 1
            return False
        else:
            print("✅ Email user auth_method verification passed")
            self.tests_passed += 1
            self.tests_run += 1
        
        # Verify password is not stored in plain text or exposed
        self.verify_password_not_exposed(self.email_user)
            
        # Test duplicate email signup (should fail)
        success, _ = self.test_email_signup_duplicate(signup_data["email"])
        if not success:
            print("❌ Duplicate email test failed - should return 400")
            return False
            
        # Test missing fields (should fail)
        success, _ = self.test_email_signup_missing_fields()
        if not success:
            print("❌ Missing fields test failed - should return 422")
            return False
            
        # Test valid login
        success, login_response = self.test_email_login(signup_data["email"], signup_data["password"])
        if not success:
            print("❌ Email login failed")
            return False
        
        # Verify password is not exposed in login response
        self.verify_password_not_exposed(login_response.get('user', {}))
            
        # Test invalid password
        success, _ = self.test_email_login_invalid(signup_data["email"])
        if not success:
            print("❌ Invalid password test failed - should return 401")
            return False
            
        # Test non-existent user
        success, _ = self.test_email_login_nonexistent()
        if not success:
            print("❌ Non-existent user test failed - should return 401")
            return False
        
        # Wallet Authentication Tests
        print("\n💼 Testing Wallet Authentication...")
        
        # Test getting wallet message
        success, message_response = self.test_get_wallet_message()
        if not success:
            print("❌ Get wallet message failed")
            return False
            
        # Verify message format
        if not self.wallet_message or "Sign this message to authenticate with Solm8" not in self.wallet_message:
            print("❌ Wallet message verification failed - unexpected format")
            self.tests_run += 1
            return False
        else:
            print("✅ Wallet message verification passed")
            self.tests_passed += 1
            self.tests_run += 1
            
        # Test wallet connect
        success, connect_response, wallet_data = self.test_wallet_connect()
        if not success:
            print("❌ Wallet connect failed")
            return False
            
        # Verify user was created with correct auth_method
        if self.wallet_user.get('auth_method') != "wallet":
            print("❌ Wallet user auth_method verification failed - expected 'wallet'")
            self.tests_run += 1
            return False
        else:
            print("✅ Wallet user auth_method verification passed")
            self.tests_passed += 1
            self.tests_run += 1
            
        # Test connecting with same wallet again (should succeed as login)
        success, _ = self.test_wallet_connect_duplicate(wallet_data["wallet_address"])
        if not success:
            print("❌ Wallet reconnect test failed - should return 200")
            return False
            
        # Test invalid wallet address
        success, _ = self.test_wallet_connect_invalid()
        if not success:
            print("❌ Invalid wallet test failed - should return 400")
            return False
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_authentication_tests()