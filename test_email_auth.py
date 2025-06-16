import requests
import unittest
import random
import string
import json
from datetime import datetime

class EmailAuthTester:
    def __init__(self, base_url="https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.email_user = None

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

    def run_email_auth_tests(self):
        """Run all email authentication tests"""
        print("🚀 Starting Solm8 Email Authentication Tests")
        
        # Test email signup
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
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = EmailAuthTester()
    tester.run_email_auth_tests()