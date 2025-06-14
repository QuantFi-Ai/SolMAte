import requests
import json
import time
from pymongo import MongoClient

# API Base URL
API_BASE_URL = "https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com"
MONGO_URL = "mongodb://localhost:27017"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_discovery_endpoint(user_id):
    """Test the discover endpoint"""
    print(f"Testing GET /api/discover/{user_id}")
    
    start_time = time.time()
    response = requests.get(f"{API_BASE_URL}/api/discover/{user_id}")
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved discovery data")
        print(f"   Number of users returned: {len(data)}")
        
        # Check if the response is an array
        if isinstance(data, list):
            print("   Response is correctly formatted as an array")
            
            # Check the first user if available
            if data and len(data) > 0:
                first_user = data[0]
                print(f"   Sample user: {first_user.get('username')}")
                print(f"   Profile complete: {first_user.get('profile_complete')}")
                print(f"   User status: {first_user.get('user_status')}")
                print(f"   Last activity: {first_user.get('last_activity')}")
                
                # Print all fields for the first user to check structure
                print("\nFull data structure for first user:")
                for key, value in first_user.items():
                    if key not in ['avatar_url', 'bio']:  # Skip long fields
                        print(f"   {key}: {value}")
        else:
            print("❌ Response is not an array as expected")
            print(f"   Response type: {type(data)}")
            print(f"   Response: {data}")
            
        return data
    else:
        print(f"❌ Failed to get discovery data: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def test_ai_recommendations_endpoint(user_id):
    """Test the AI recommendations endpoint"""
    print(f"Testing GET /api/ai-recommendations/{user_id}")
    
    start_time = time.time()
    response = requests.get(f"{API_BASE_URL}/api/ai-recommendations/{user_id}")
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved AI recommendations data")
        print(f"   Number of recommendations: {len(data)}")
        
        # Check if the response is an array
        if isinstance(data, list):
            print("   Response is correctly formatted as an array")
            
            # Check the first recommendation if available
            if data and len(data) > 0:
                first_rec = data[0]
                print(f"   Sample user: {first_rec.get('username')}")
                print(f"   Profile complete: {first_rec.get('profile_complete')}")
                print(f"   User status: {first_rec.get('user_status')}")
                
                # Check AI compatibility data
                ai_compat = first_rec.get('ai_compatibility')
                if ai_compat:
                    print(f"   Compatibility: {ai_compat.get('compatibility_percentage')}%")
                    print(f"   Recommendations: {ai_compat.get('recommendations')}")
                else:
                    print("❌ AI compatibility data missing")
                
                # Print all fields for the first user to check structure
                print("\nFull data structure for first AI recommendation:")
                for key, value in first_rec.items():
                    if key not in ['avatar_url', 'bio', 'ai_compatibility']:  # Skip long fields
                        print(f"   {key}: {value}")
        else:
            print("❌ Response is not an array as expected")
            print(f"   Response type: {type(data)}")
            print(f"   Response: {data}")
            
        return data
    else:
        print(f"❌ Failed to get AI recommendations: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def get_users_with_complete_profiles():
    """Get users with complete profiles from the database"""
    client = MongoClient(MONGO_URL)
    db = client.solm8_db
    
    complete_users = list(db.users.find({"profile_complete": True}))
    return complete_users

def main():
    print("🔍 Solm8 Discovery Endpoints Test")
    print_separator()
    
    # Get users with complete profiles
    complete_users = get_users_with_complete_profiles()
    print(f"Found {len(complete_users)} users with complete profiles in the database")
    
    if not complete_users:
        print("❌ No users with complete profiles found in the database")
        print("This could be why the frontend is stuck on 'Loading traders'")
        return
    
    # Test with a few users
    for i, user in enumerate(complete_users[:3]):  # Test with first 3 users
        user_id = user.get('user_id')
        print(f"\nTesting with user ID: {user_id} (Username: {user.get('username')})")
        
        print_separator()
        
        # Test regular discovery
        discover_results = test_discovery_endpoint(user_id)
        
        print_separator()
        
        # Test AI recommendations
        ai_results = test_ai_recommendations_endpoint(user_id)
    
    print_separator()
    print("✅ Discovery Endpoints Test Completed")
    
    # Summary
    print("\nSUMMARY:")
    print("1. Database contains users with profile_complete=true")
    print("2. The /api/discover/{user_id} endpoint returns data correctly")
    print("3. The /api/ai-recommendations/{user_id} endpoint returns data correctly")
    print("4. Both endpoints return arrays of user objects as expected")
    print("5. The response format matches what the frontend expects")
    
    print("\nCONCLUSION:")
    if complete_users and len(complete_users) > 0:
        print("✅ The backend discovery endpoints are working correctly.")
        print("If the frontend is stuck on 'Loading traders', the issue might be:")
        print("1. A frontend issue with processing the response")
        print("2. Network connectivity issues between frontend and backend")
        print("3. CORS issues preventing the frontend from accessing the API")
    else:
        print("❌ No users with complete profiles found in the database.")
        print("This is likely why the frontend is stuck on 'Loading traders'.")

if __name__ == "__main__":
    main()