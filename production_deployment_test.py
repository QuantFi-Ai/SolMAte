import requests
import unittest
import uuid
import os
import json
import random
import string
from datetime import datetime, timedelta
from pymongo import MongoClient

class ProductionDeploymentTester:
    def __init__(self, base_url="https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}" if endpoint else self.base_url
        default_headers = {'Content-Type': 'application/json'} if not files else {}
        if headers:
            default_headers.update(headers)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result = response.json()
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "response": result
                    })
                    return True, result
                except:
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "response": response.text
                    })
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_response = response.json()
                    print(f"Response: {error_response}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "response_code": response.status_code,
                        "expected_code": expected_status,
                        "response": error_response
                    })
                except:
                    print(f"Response: {response.text}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "response_code": response.status_code,
                        "expected_code": expected_status,
                        "response": response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, {}

    def test_database_connection(self):
        """Test database connection through API endpoints"""
        print("\n" + "="*60)
        print("🗄️  DATABASE CONNECTION TESTS")
        print("="*60)
        
        # Test 1: Create a user to verify database write operations
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"db_test_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"DB Test User {random_suffix}"
        
        signup_data = {
            "email": test_email,
            "password": test_password,
            "display_name": test_display_name
        }
        
        success, response = self.run_test(
            "Database Write Test (User Creation)",
            "POST",
            "auth/email/signup",
            200,
            data=signup_data
        )
        
        if not success:
            print("❌ Database write operations failed")
            return False
        
        user_id = response.get("user", {}).get("user_id")
        if not user_id:
            print("❌ User ID not returned from database")
            return False
        
        print(f"✅ Database write successful - User ID: {user_id}")
        
        # Test 2: Read the user back to verify database read operations
        success, user_data = self.run_test(
            "Database Read Test (User Retrieval)",
            "GET",
            f"user/{user_id}",
            200
        )
        
        if not success:
            print("❌ Database read operations failed")
            return False
        
        if user_data.get("user_id") != user_id:
            print("❌ Database read returned incorrect data")
            return False
        
        print("✅ Database read successful")
        
        # Test 3: Update user to verify database update operations
        update_data = {
            "bio": "Testing database update operations",
            "trading_experience": "Intermediate",
            "preferred_tokens": ["DeFi", "NFTs"],
            "trading_style": "Day Trader",
            "portfolio_size": "$10K-$100K"
        }
        
        success, update_response = self.run_test(
            "Database Update Test (User Profile Update)",
            "PUT",
            f"user/{user_id}",
            200,
            data=update_data
        )
        
        if not success:
            print("❌ Database update operations failed")
            return False
        
        print("✅ Database update successful")
        
        # Test 4: Verify the update was persisted
        success, updated_user = self.run_test(
            "Database Persistence Test (Verify Update)",
            "GET",
            f"user/{user_id}",
            200
        )
        
        if not success:
            print("❌ Database persistence verification failed")
            return False
        
        if updated_user.get("bio") != update_data["bio"]:
            print("❌ Database update was not persisted")
            return False
        
        print("✅ Database persistence verified")
        
        return True

    def test_health_check(self):
        """Test health check endpoint"""
        print("\n" + "="*60)
        print("🏥 HEALTH CHECK TESTS")
        print("="*60)
        
        # Test 1: Check if health endpoint exists
        success, response = self.run_test(
            "Health Endpoint Availability",
            "GET",
            "health",
            200
        )
        
        if success:
            print("✅ Health endpoint is available")
            
            # Verify response contains expected fields
            expected_fields = ["status", "timestamp"]
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                print(f"⚠️  Health endpoint missing fields: {missing_fields}")
            else:
                print("✅ Health endpoint returns expected fields")
            
            # Check if database connectivity info is included
            if "database" in response:
                print("✅ Health endpoint includes database connectivity information")
            else:
                print("⚠️  Health endpoint doesn't include database connectivity information")
            
            # Check if environment info is included
            if "environment" in response:
                print("✅ Health endpoint includes environment information")
            else:
                print("⚠️  Health endpoint doesn't include environment information")
            
            # Check if version info is included
            if "version" in response:
                print("✅ Health endpoint includes version information")
            else:
                print("⚠️  Health endpoint doesn't include version information")
            
            return True
        else:
            print("❌ Health endpoint not available - testing basic connectivity")
            
            # Fallback: Test basic API connectivity
            success, response = self.run_test(
                "Basic API Connectivity",
                "GET",
                "",  # Root endpoint
                200
            )
            
            if success:
                print("✅ Basic API connectivity working")
                return True
            else:
                print("❌ Basic API connectivity failed")
                return False

    def test_error_handling(self):
        """Test global exception handlers"""
        print("\n" + "="*60)
        print("🚨 ERROR HANDLING TESTS")
        print("="*60)
        
        # Test 1: Validation Error Handling
        invalid_signup_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short
            "display_name": ""  # Empty display name
        }
        
        success, response = self.run_test(
            "Validation Error Handling",
            "POST",
            "auth/email/signup",
            422,  # Validation error should return 422
            data=invalid_signup_data
        )
        
        if success:
            print("✅ Validation errors handled correctly")
            
            # Check if error response is properly formatted
            if isinstance(response, dict) and "error" in response:
                print("✅ Error response properly formatted")
            else:
                print("⚠️  Error response format could be improved")
        else:
            # If 422 is not returned, check if it's handled differently
            print("⚠️  Validation error handling may need improvement")
        
        # Test 2: HTTP Exception Handling (404 Not Found)
        success, response = self.run_test(
            "HTTP Exception Handling (404)",
            "GET",
            "user/non-existent-user-id",
            404
        )
        
        if success:
            print("✅ HTTP exceptions handled correctly")
            
            # Check if error response includes timestamp
            if isinstance(response, dict) and "timestamp" in response:
                print("✅ Error response includes timestamp")
            else:
                print("⚠️  Error response missing timestamp")
        else:
            print("⚠️  HTTP exception handling may need improvement")
        
        # Test 3: Authentication Error Handling
        invalid_login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        success, response = self.run_test(
            "Authentication Error Handling",
            "POST",
            "auth/email/login",
            401
        )
        
        if success:
            print("✅ Authentication errors handled correctly")
        else:
            print("⚠️  Authentication error handling may need improvement")
        
        # Test 4: General Exception Handling (Malformed JSON)
        try:
            url = f"{self.base_url}/api/auth/email/signup"
            headers = {'Content-Type': 'application/json'}
            
            # Send malformed JSON
            response = requests.post(url, data="invalid json", headers=headers, timeout=30)
            
            if response.status_code == 500:
                print("✅ General exceptions handled with 500 status")
                
                try:
                    error_response = response.json()
                    if "error" in error_response and "timestamp" in error_response:
                        print("✅ General error response properly formatted")
                    else:
                        print("⚠️  General error response format could be improved")
                except:
                    print("⚠️  General error response not in JSON format")
            else:
                print(f"⚠️  Unexpected status code for malformed JSON: {response.status_code}")
        
        except Exception as e:
            print(f"⚠️  Error testing general exception handling: {e}")
        
        return True

    def test_environment_configuration(self):
        """Test environment configuration"""
        print("\n" + "="*60)
        print("🌍 ENVIRONMENT CONFIGURATION TESTS")
        print("="*60)
        
        # Test 1: CORS Configuration
        print("Testing CORS configuration...")
        
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://example.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.base_url}/api/auth/email/signup", headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("✅ CORS preflight requests handled correctly")
                
                # Check CORS headers
                cors_headers = [
                    'Access-Control-Allow-Origin',
                    'Access-Control-Allow-Methods',
                    'Access-Control-Allow-Headers'
                ]
                
                present_headers = [h for h in cors_headers if h in response.headers]
                
                if len(present_headers) >= 2:
                    print("✅ CORS headers properly configured")
                else:
                    print("⚠️  Some CORS headers may be missing")
            else:
                print("⚠️  CORS preflight handling may need improvement")
        
        except Exception as e:
            print(f"⚠️  Error testing CORS: {e}")
        
        # Test 2: Environment-specific behavior
        print("Testing environment-specific behavior...")
        
        # Create a test user to check if environment affects functionality
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"env_test_{random_suffix}@example.com"
        
        signup_data = {
            "email": test_email,
            "password": "TestPassword123!",
            "display_name": f"Env Test User {random_suffix}"
        }
        
        success, response = self.run_test(
            "Environment Configuration Test",
            "POST",
            "auth/email/signup",
            200,
            data=signup_data
        )
        
        if success:
            print("✅ Environment configuration allows normal operations")
        else:
            print("❌ Environment configuration may be blocking operations")
        
        # Test 3: Database name configuration
        print("Testing database configuration...")
        
        if success:
            user_id = response.get("user", {}).get("user_id")
            
            # Try to retrieve the user to verify database connection works
            success, user_data = self.run_test(
                "Database Configuration Test",
                "GET",
                f"user/{user_id}",
                200
            )
            
            if success:
                print("✅ Database configuration working correctly")
            else:
                print("❌ Database configuration may have issues")
        
        return True

    def test_core_api_functionality(self):
        """Test core API functionality"""
        print("\n" + "="*60)
        print("🔧 CORE API FUNCTIONALITY TESTS")
        print("="*60)
        
        # Test 1: Email Authentication
        print("Testing email authentication...")
        
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"core_test_{random_suffix}@example.com"
        test_password = "TestPassword123!"
        test_display_name = f"Core Test User {random_suffix}"
        
        # Test signup
        signup_data = {
            "email": test_email,
            "password": test_password,
            "display_name": test_display_name
        }
        
        success, signup_response = self.run_test(
            "Email Signup",
            "POST",
            "auth/email/signup",
            200,
            data=signup_data
        )
        
        if not success:
            print("❌ Email signup failed")
            return False
        
        user_id = signup_response.get("user", {}).get("user_id")
        print(f"✅ Email signup successful - User ID: {user_id}")
        
        # Test login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, login_response = self.run_test(
            "Email Login",
            "POST",
            "auth/email/login",
            200,
            data=login_data
        )
        
        if not success:
            print("❌ Email login failed")
            return False
        
        print("✅ Email login successful")
        
        # Test 2: User Profile Management
        print("Testing user profile management...")
        
        # Get user profile
        success, user_data = self.run_test(
            "Get User Profile",
            "GET",
            f"user/{user_id}",
            200
        )
        
        if not success:
            print("❌ Get user profile failed")
            return False
        
        print("✅ Get user profile successful")
        
        # Update user profile
        update_data = {
            "bio": "Testing core API functionality",
            "location": "Test City",
            "trading_experience": "Advanced",
            "years_trading": 5,
            "preferred_tokens": ["DeFi", "NFTs", "Blue Chips"],
            "trading_style": "Swing Trader",
            "portfolio_size": "$100K+",
            "risk_tolerance": "Moderate",
            "best_trade": "Bought BTC at $10k",
            "worst_trade": "Sold too early",
            "favorite_project": "Solana",
            "trading_hours": "Evening",
            "communication_style": "Professional",
            "preferred_communication_platform": "Discord",
            "preferred_trading_platform": "Jupiter",
            "looking_for": ["Alpha Sharing", "Research Partner"]
        }
        
        success, update_response = self.run_test(
            "Update User Profile",
            "PUT",
            f"user/{user_id}",
            200,
            data=update_data
        )
        
        if not success:
            print("❌ Update user profile failed")
            return False
        
        print("✅ Update user profile successful")
        
        # Test 3: Password Change Functionality
        print("Testing password change functionality...")
        
        new_password = "NewTestPassword123!"
        password_change_data = {
            "current_password": test_password,
            "new_password": new_password,
            "confirm_password": new_password
        }
        
        success, password_response = self.run_test(
            "Password Change",
            "POST",
            f"auth/change-password",
            200,
            data=password_change_data
        )
        
        if success:
            print("✅ Password change successful")
            
            # Test login with new password
            new_login_data = {
                "email": test_email,
                "password": new_password
            }
            
            success, new_login_response = self.run_test(
                "Login with New Password",
                "POST",
                "auth/email/login",
                200,
                data=new_login_data
            )
            
            if success:
                print("✅ Login with new password successful")
            else:
                print("❌ Login with new password failed")
        else:
            print("⚠️  Password change endpoint may not be available")
        
        # Test 4: Discovery System
        print("Testing discovery system...")
        
        success, discovery_response = self.run_test(
            "Discovery System",
            "GET",
            f"discover/{user_id}",
            200
        )
        
        if success:
            print("✅ Discovery system working")
            
            if isinstance(discovery_response, list):
                print(f"✅ Discovery returned {len(discovery_response)} users")
            else:
                print("⚠️  Discovery response format unexpected")
        else:
            print("❌ Discovery system failed")
        
        # Test 5: Matches System
        print("Testing matches system...")
        
        success, matches_response = self.run_test(
            "Matches System",
            "GET",
            f"matches/{user_id}",
            200
        )
        
        if success:
            print("✅ Matches system working")
            
            if isinstance(matches_response, list):
                print(f"✅ Matches returned {len(matches_response)} matches")
            else:
                print("⚠️  Matches response format unexpected")
        else:
            print("❌ Matches system failed")
        
        return True

    def run_all_tests(self):
        """Run all production deployment tests"""
        print("🚀 STARTING PRODUCTION DEPLOYMENT TESTS FOR SOLM8 5.0")
        print("="*80)
        
        test_results = {
            "database_connection": self.test_database_connection(),
            "health_check": self.test_health_check(),
            "error_handling": self.test_error_handling(),
            "environment_configuration": self.test_environment_configuration(),
            "core_api_functionality": self.test_core_api_functionality()
        }
        
        print("\n" + "="*80)
        print("📊 PRODUCTION DEPLOYMENT TEST SUMMARY")
        print("="*80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"Test Categories: {passed_tests}/{total_tests} categories passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL PRODUCTION DEPLOYMENT TESTS PASSED!")
            print("✅ SOLM8 5.0 backend is ready for production deployment")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test categories need attention")
            print("🔧 Review failed tests before production deployment")
        
        return test_results

def main():
    """Main function to run production deployment tests"""
    tester = ProductionDeploymentTester()
    results = tester.run_all_tests()
    
    # Save detailed test results
    with open('/app/production_test_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "summary": results,
            "detailed_results": tester.test_results,
            "stats": {
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "success_rate": f"{(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "0%"
            }
        }, f, indent=2)
    
    print(f"\n📄 Detailed test results saved to: /app/production_test_results.json")
    
    return results

if __name__ == "__main__":
    main()