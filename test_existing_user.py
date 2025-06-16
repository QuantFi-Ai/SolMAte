import requests
import json

# Base URL
base_url = "https://5ab0f635-9ff1-4325-81ed-c868d2618fac.preview.emergentagent.com/api"

# Test with a specific user ID
user_id = "087e057e-0b48-4222-b994-7e4208962470"  # Use the User A ID from our previous test

def test_endpoint(name, endpoint):
    """Test an API endpoint and print the response"""
    print(f"\n===== Testing {name} =====")
    url = f"{base_url}/{endpoint}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Number of items: {len(data)}")
                if len(data) > 0:
                    print(f"First item keys: {list(data[0].keys())}")
                    print(f"Sample data: {json.dumps(data[0], indent=2)[:500]}...")
            else:
                print(f"Response keys: {list(data.keys())}")
                print(f"Sample data: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Exception: {str(e)}")

# Test discovery endpoints
test_endpoint("Discover Users", f"discover/{user_id}")
test_endpoint("AI Recommendations", f"ai-recommendations/{user_id}")

# Test matches endpoints
test_endpoint("User Matches", f"matches/{user_id}")
test_endpoint("Matches with Messages", f"matches-with-messages/{user_id}")