import requests
import os
import json
import time
import uuid
import random
import string
from datetime import datetime
from pymongo import MongoClient

class ProductionDeploymentTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://solm8-tinder.emergent.host"
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_test_result(self, category, test_name, passed, details=""):
        """Log test result for summary"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "category": category,
            "test_name": test_name,
            "status": status,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")

    def test_environment_configuration(self):
        """Test environment configuration for production"""
        print("\n🔧 TESTING ENVIRONMENT CONFIGURATION")
        print("-" * 40)
        
        # Test 1: Verify backend URL is properly configured
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                backend_url_correct = self.base_url in str(health_data) or response.url.startswith(self.base_url)
                self.log_test_result(
                    "Environment", 
                    "Backend URL Configuration", 
                    backend_url_correct,
                    f"Backend responding at {self.base_url}"
                )
            else:
                self.log_test_result(
                    "Environment", 
                    "Backend URL Configuration", 
                    False,
                    f"Health endpoint returned {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Environment", 
                "Backend URL Configuration", 
                False,
                f"Connection failed: {str(e)}"
            )

        # Test 2: Test CORS configuration for production domains
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://solm8-tinder.emergent.host',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = requests.options(f"{self.api_url}/health", headers=headers, timeout=10)
            
            cors_working = (
                response.status_code in [200, 204] or 
                'Access-Control-Allow-Origin' in response.headers
            )
            
            self.log_test_result(
                "Environment", 
                "CORS Configuration", 
                cors_working,
                f"CORS headers: {dict(response.headers)}" if cors_working else "CORS headers missing"
            )
        except Exception as e:
            self.log_test_result(
                "Environment", 
                "CORS Configuration", 
                False,
                f"CORS test failed: {str(e)}"
            )

        # Test 3: Test environment variables loading
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                env_loaded = (
                    'environment' in health_data and 
                    'database_status' in health_data
                )
                self.log_test_result(
                    "Environment", 
                    "Environment Variables Loading", 
                    env_loaded,
                    f"Environment: {health_data.get('environment', 'unknown')}"
                )
            else:
                self.log_test_result(
                    "Environment", 
                    "Environment Variables Loading", 
                    False,
                    "Health endpoint not accessible"
                )
        except Exception as e:
            self.log_test_result(
                "Environment", 
                "Environment Variables Loading", 
                False,
                f"Failed to check environment: {str(e)}"
            )

    def test_database_connection(self):
        """Test database connection and operations"""
        print("\n🗄️ TESTING DATABASE CONNECTION")
        print("-" * 40)
        
        # Test 1: Database connectivity via health endpoint
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                db_connected = health_data.get('database_status') == 'connected'
                self.log_test_result(
                    "Database", 
                    "MongoDB Connection", 
                    db_connected,
                    f"Database status: {health_data.get('database_status', 'unknown')}"
                )
            else:
                self.log_test_result(
                    "Database", 
                    "MongoDB Connection", 
                    False,
                    f"Health check failed with status {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Database", 
                "MongoDB Connection", 
                False,
                f"Health check error: {str(e)}"
            )

        # Test 2: Database write operation
        try:
            # Create a test user to verify write operations
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            test_data = {
                "email": f"test_db_{random_suffix}@example.com",
                "password": "TestPassword123!",
                "display_name": f"DB Test User {random_suffix}"
            }
            
            response = requests.post(f"{self.api_url}/auth/email/signup", json=test_data, timeout=10)
            write_success = response.status_code == 200
            
            if write_success:
                user_data = response.json().get('user', {})
                test_user_id = user_data.get('user_id')
                
                self.log_test_result(
                    "Database", 
                    "Database Write Operations", 
                    True,
                    f"Successfully created user {test_user_id}"
                )
                
                # Test 3: Database read operation
                if test_user_id:
                    read_response = requests.get(f"{self.api_url}/user/{test_user_id}", timeout=10)
                    read_success = read_response.status_code == 200
                    
                    self.log_test_result(
                        "Database", 
                        "Database Read Operations", 
                        read_success,
                        f"Successfully read user data" if read_success else f"Read failed: {read_response.status_code}"
                    )
                    
                    # Test 4: Database update operation
                    if read_success:
                        update_data = {
                            "bio": "Updated bio for database test",
                            "trading_experience": "Intermediate"
                        }
                        update_response = requests.put(f"{self.api_url}/user/{test_user_id}", json=update_data, timeout=10)
                        update_success = update_response.status_code == 200
                        
                        self.log_test_result(
                            "Database", 
                            "Database Update Operations", 
                            update_success,
                            f"Successfully updated user" if update_success else f"Update failed: {update_response.status_code}"
                        )
                        
                        # Test 5: Data persistence
                        if update_success:
                            time.sleep(1)  # Brief delay to ensure persistence
                            verify_response = requests.get(f"{self.api_url}/user/{test_user_id}", timeout=10)
                            if verify_response.status_code == 200:
                                verify_data = verify_response.json()
                                persistence_success = verify_data.get('bio') == update_data['bio']
                                
                                self.log_test_result(
                                    "Database", 
                                    "Data Persistence", 
                                    persistence_success,
                                    f"Data persisted correctly" if persistence_success else "Data not persisted"
                                )
                            else:
                                self.log_test_result(
                                    "Database", 
                                    "Data Persistence", 
                                    False,
                                    "Failed to verify persistence"
                                )
            else:
                self.log_test_result(
                    "Database", 
                    "Database Write Operations", 
                    False,
                    f"User creation failed: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Database", 
                "Database Operations", 
                False,
                f"Database operation error: {str(e)}"
            )

    def test_server_configuration(self):
        """Test server configuration and settings"""
        print("\n⚙️ TESTING SERVER CONFIGURATION")
        print("-" * 40)
        
        # Test 1: Server binding and accessibility
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            server_accessible = response.status_code == 200
            
            self.log_test_result(
                "Server", 
                "Server Binding and Accessibility", 
                server_accessible,
                f"Server responding on {self.base_url}" if server_accessible else f"Server not accessible: {response.status_code}"
            )
            
            # Test 2: Production settings verification
            if server_accessible:
                health_data = response.json()
                production_env = health_data.get('environment') == 'production'
                
                self.log_test_result(
                    "Server", 
                    "Production Environment Settings", 
                    production_env,
                    f"Environment: {health_data.get('environment', 'unknown')}"
                )
                
                # Test 3: Server response time
                start_time = time.time()
                response = requests.get(f"{self.api_url}/health", timeout=10)
                response_time = time.time() - start_time
                
                good_response_time = response_time < 2.0  # Less than 2 seconds
                
                self.log_test_result(
                    "Server", 
                    "Server Response Time", 
                    good_response_time,
                    f"Response time: {response_time:.2f}s"
                )
                
        except Exception as e:
            self.log_test_result(
                "Server", 
                "Server Configuration", 
                False,
                f"Server test error: {str(e)}"
            )

        # Test 4: Logging configuration (check if server logs errors properly)
        try:
            # Make a request that should generate a 404 error
            response = requests.get(f"{self.api_url}/nonexistent-endpoint", timeout=10)
            proper_404 = response.status_code == 404
            
            if proper_404:
                try:
                    error_data = response.json()
                    has_timestamp = 'timestamp' in error_data
                    has_error_info = 'error' in error_data
                    
                    logging_working = has_timestamp and has_error_info
                    
                    self.log_test_result(
                        "Server", 
                        "Error Logging Configuration", 
                        logging_working,
                        f"Error response includes timestamp and error info" if logging_working else "Missing error details"
                    )
                except:
                    self.log_test_result(
                        "Server", 
                        "Error Logging Configuration", 
                        False,
                        "Error response not in JSON format"
                    )
            else:
                self.log_test_result(
                    "Server", 
                    "Error Logging Configuration", 
                    False,
                    f"Expected 404, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Server", 
                "Error Logging Configuration", 
                False,
                f"Logging test error: {str(e)}"
            )

    def test_api_endpoints(self):
        """Test core API endpoints functionality"""
        print("\n🔌 TESTING API ENDPOINTS")
        print("-" * 40)
        
        # Test 1: Health check endpoint
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            health_working = response.status_code == 200
            
            if health_working:
                health_data = response.json()
                has_required_fields = all(field in health_data for field in ['status', 'database_status', 'environment'])
                
                self.log_test_result(
                    "API", 
                    "Health Check Endpoint", 
                    has_required_fields,
                    f"Health data: {health_data}" if has_required_fields else "Missing required health fields"
                )
            else:
                self.log_test_result(
                    "API", 
                    "Health Check Endpoint", 
                    False,
                    f"Health check failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "API", 
                "Health Check Endpoint", 
                False,
                f"Health check error: {str(e)}"
            )

        # Test 2: Authentication endpoints
        try:
            # Test email signup
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            signup_data = {
                "email": f"test_auth_{random_suffix}@example.com",
                "password": "TestPassword123!",
                "display_name": f"Auth Test User {random_suffix}"
            }
            
            signup_response = requests.post(f"{self.api_url}/auth/email/signup", json=signup_data, timeout=10)
            signup_success = signup_response.status_code == 200
            
            self.log_test_result(
                "API", 
                "Email Signup Endpoint", 
                signup_success,
                f"Signup successful" if signup_success else f"Signup failed: {signup_response.status_code}"
            )
            
            # Test email login
            if signup_success:
                login_data = {
                    "email": signup_data["email"],
                    "password": signup_data["password"]
                }
                
                login_response = requests.post(f"{self.api_url}/auth/email/login", json=login_data, timeout=10)
                login_success = login_response.status_code == 200
                
                self.log_test_result(
                    "API", 
                    "Email Login Endpoint", 
                    login_success,
                    f"Login successful" if login_success else f"Login failed: {login_response.status_code}"
                )
                
                # Test user profile endpoint
                if login_success:
                    user_data = login_response.json().get('user', {})
                    user_id = user_data.get('user_id')
                    
                    if user_id:
                        profile_response = requests.get(f"{self.api_url}/user/{user_id}", timeout=10)
                        profile_success = profile_response.status_code == 200
                        
                        self.log_test_result(
                            "API", 
                            "User Profile Endpoint", 
                            profile_success,
                            f"Profile retrieved" if profile_success else f"Profile failed: {profile_response.status_code}"
                        )
                        
                        # Test profile update
                        if profile_success:
                            update_data = {
                                "bio": "Updated bio for API test",
                                "trading_experience": "Advanced"
                            }
                            
                            update_response = requests.put(f"{self.api_url}/user/{user_id}", json=update_data, timeout=10)
                            update_success = update_response.status_code == 200
                            
                            self.log_test_result(
                                "API", 
                                "Profile Update Endpoint", 
                                update_success,
                                f"Profile updated" if update_success else f"Update failed: {update_response.status_code}"
                            )
                            
                            # Test discovery endpoint
                            discovery_response = requests.get(f"{self.api_url}/discover/{user_id}", timeout=10)
                            discovery_success = discovery_response.status_code == 200
                            
                            self.log_test_result(
                                "API", 
                                "Discovery Endpoint", 
                                discovery_success,
                                f"Discovery working" if discovery_success else f"Discovery failed: {discovery_response.status_code}"
                            )
                            
                            # Test matches endpoint
                            matches_response = requests.get(f"{self.api_url}/matches/{user_id}", timeout=10)
                            matches_success = matches_response.status_code == 200
                            
                            self.log_test_result(
                                "API", 
                                "Matches Endpoint", 
                                matches_success,
                                f"Matches working" if matches_success else f"Matches failed: {matches_response.status_code}"
                            )
                            
        except Exception as e:
            self.log_test_result(
                "API", 
                "Authentication Endpoints", 
                False,
                f"Auth test error: {str(e)}"
            )

    def test_error_handling(self):
        """Test global exception handlers and error responses"""
        print("\n🚨 TESTING ERROR HANDLING")
        print("-" * 40)
        
        # Test 1: 404 Error handling
        try:
            response = requests.get(f"{self.api_url}/nonexistent-endpoint", timeout=10)
            proper_404 = response.status_code == 404
            
            if proper_404:
                try:
                    error_data = response.json()
                    has_error_format = all(field in error_data for field in ['error', 'status_code', 'timestamp'])
                    
                    self.log_test_result(
                        "Error Handling", 
                        "404 Error Response Format", 
                        has_error_format,
                        f"Error format correct" if has_error_format else f"Missing fields in error response"
                    )
                except:
                    self.log_test_result(
                        "Error Handling", 
                        "404 Error Response Format", 
                        False,
                        "Error response not in JSON format"
                    )
            else:
                self.log_test_result(
                    "Error Handling", 
                    "404 Error Response Format", 
                    False,
                    f"Expected 404, got {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Error Handling", 
                "404 Error Response Format", 
                False,
                f"404 test error: {str(e)}"
            )

        # Test 2: Validation error handling (422)
        try:
            # Send invalid signup data
            invalid_data = {
                "email": "invalid-email",  # Invalid email format
                "password": "123",  # Too short
                "display_name": ""  # Empty name
            }
            
            response = requests.post(f"{self.api_url}/auth/email/signup", json=invalid_data, timeout=10)
            validation_error = response.status_code in [400, 422]
            
            if validation_error:
                try:
                    error_data = response.json()
                    has_validation_format = 'error' in error_data or 'detail' in error_data
                    
                    self.log_test_result(
                        "Error Handling", 
                        "Validation Error Response", 
                        has_validation_format,
                        f"Validation error properly formatted" if has_validation_format else "Missing validation error details"
                    )
                except:
                    self.log_test_result(
                        "Error Handling", 
                        "Validation Error Response", 
                        False,
                        "Validation error response not in JSON format"
                    )
            else:
                self.log_test_result(
                    "Error Handling", 
                    "Validation Error Response", 
                    False,
                    f"Expected 400/422, got {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Error Handling", 
                "Validation Error Response", 
                False,
                f"Validation test error: {str(e)}"
            )

        # Test 3: Authentication error handling (401)
        try:
            # Try to login with wrong credentials
            wrong_creds = {
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(f"{self.api_url}/auth/email/login", json=wrong_creds, timeout=10)
            auth_error = response.status_code == 401
            
            if auth_error:
                try:
                    error_data = response.json()
                    has_auth_format = 'detail' in error_data or 'error' in error_data
                    
                    self.log_test_result(
                        "Error Handling", 
                        "Authentication Error Response", 
                        has_auth_format,
                        f"Auth error properly formatted" if has_auth_format else "Missing auth error details"
                    )
                except:
                    self.log_test_result(
                        "Error Handling", 
                        "Authentication Error Response", 
                        False,
                        "Auth error response not in JSON format"
                    )
            else:
                self.log_test_result(
                    "Error Handling", 
                    "Authentication Error Response", 
                    False,
                    f"Expected 401, got {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Error Handling", 
                "Authentication Error Response", 
                False,
                f"Auth error test error: {str(e)}"
            )

        # Test 4: General exception handling
        try:
            # Try to access user with invalid ID format
            response = requests.get(f"{self.api_url}/user/invalid-uuid-format", timeout=10)
            error_handled = response.status_code in [400, 404, 500]
            
            if error_handled:
                try:
                    error_data = response.json()
                    has_timestamp = 'timestamp' in error_data
                    
                    self.log_test_result(
                        "Error Handling", 
                        "General Exception Handling", 
                        has_timestamp,
                        f"Exception handled with timestamp" if has_timestamp else "Exception handled but missing timestamp"
                    )
                except:
                    self.log_test_result(
                        "Error Handling", 
                        "General Exception Handling", 
                        True,
                        "Exception handled (non-JSON response)"
                    )
            else:
                self.log_test_result(
                    "Error Handling", 
                    "General Exception Handling", 
                    False,
                    f"Unexpected status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Error Handling", 
                "General Exception Handling", 
                False,
                f"Exception test error: {str(e)}"
            )

    def run_all_tests(self):
        """Run all production deployment tests"""
        print("🚀 STARTING PRODUCTION DEPLOYMENT TESTS")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_environment_configuration()
        self.test_database_connection()
        self.test_server_configuration()
        self.test_api_endpoints()
        self.test_error_handling()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        self.print_summary(total_time)
        
        return self.tests_passed, self.tests_run

    def print_summary(self, total_time):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 PRODUCTION DEPLOYMENT TEST SUMMARY")
        print("=" * 60)
        
        # Overall results
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"Overall Results: {self.tests_passed}/{self.tests_run} tests passed ({success_rate:.1f}%)")
        print(f"Total Time: {total_time:.2f} seconds")
        print()
        
        # Results by category
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0, 'tests': []}
            
            categories[category]['total'] += 1
            if result['passed']:
                categories[category]['passed'] += 1
            categories[category]['tests'].append(result)
        
        for category, data in categories.items():
            category_rate = (data['passed'] / data['total']) * 100
            status = "✅ PASS" if data['passed'] == data['total'] else "❌ FAIL"
            print(f"{status} {category}: {data['passed']}/{data['total']} ({category_rate:.1f}%)")
            
            # Show failed tests
            failed_tests = [test for test in data['tests'] if not test['passed']]
            if failed_tests:
                for test in failed_tests:
                    print(f"    ❌ {test['test_name']}: {test['details']}")
        
        print()
        
        # Final verdict
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - BACKEND IS READY FOR PRODUCTION DEPLOYMENT!")
        elif success_rate >= 80:
            print("⚠️  MOSTLY READY - Some minor issues found but core functionality works")
        else:
            print("🚨 NOT READY - Significant issues found that need to be addressed")
        
        print("=" * 60)

def main():
    """Main function to run production deployment tests"""
    tester = ProductionDeploymentTester()
    passed, total = tester.run_all_tests()
    
    # Return exit code based on results
    if passed == total:
        exit(0)  # All tests passed
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()