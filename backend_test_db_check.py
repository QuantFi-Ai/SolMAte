import requests
import json
from pymongo import MongoClient

# API Base URL
API_BASE_URL = "https://8134b81b-ad13-497e-ba8a-ecdf0793b0b4.preview.emergentagent.com"
MONGO_URL = "mongodb://localhost:27017"

def print_separator():
    print("\n" + "="*80 + "\n")

def check_database_users():
    """Check users directly in the database"""
    print("Checking users directly in the database...")
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URL)
    db = client.solm8_db
    
    # Get all users
    users = list(db.users.find())
    total_users = len(users)
    
    # Count users by auth method
    auth_methods = {}
    for user in users:
        auth_method = user.get('auth_method', 'none')
        auth_methods[auth_method] = auth_methods.get(auth_method, 0) + 1
    
    # Count users with complete profiles
    complete_profiles = sum(1 for user in users if user.get('profile_complete', False))
    
    print(f"Total users in database: {total_users}")
    print(f"Users by auth method: {auth_methods}")
    print(f"Users with complete profiles: {complete_profiles}")
    
    # Get a sample of users with complete profiles
    complete_users = list(db.users.find({"profile_complete": True}).limit(5))
    
    print("\nSample of users with complete profiles:")
    for i, user in enumerate(complete_users):
        print(f"{i+1}. User ID: {user.get('user_id')}")
        print(f"   Username: {user.get('username')}")
        print(f"   Auth Method: {user.get('auth_method')}")
        print(f"   Trading Experience: {user.get('trading_experience')}")
        print(f"   Preferred Tokens: {user.get('preferred_tokens')}")
        print(f"   Trading Style: {user.get('trading_style')}")
        print(f"   Portfolio Size: {user.get('portfolio_size')}")
        print(f"   Last Activity: {user.get('last_activity')}")
        print()
    
    return complete_users

def test_discovery_with_real_users(complete_users):
    """Test discovery with real user IDs from the database"""
    if not complete_users:
        print("No users with complete profiles found")
        return
    
    print("Testing discovery with real user IDs...")
    
    for i, user in enumerate(complete_users[:2]):  # Test with first 2 users
        user_id = user.get('user_id')
        print(f"\nTesting discovery for user ID: {user_id}")
        
        # Test regular discovery
        response = requests.get(f"{API_BASE_URL}/api/discover/{user_id}")
        
        if response.status_code == 200:
            discover_results = response.json()
            print(f"✅ Discovery returned {len(discover_results)} potential matches")
            
            # Show the first 2 matches
            if discover_results and len(discover_results) > 0:
                print("\nSample of discovery results:")
                for j, match in enumerate(discover_results[:2]):
                    print(f"{j+1}. User ID: {match.get('user_id')}")
                    print(f"   Username: {match.get('username')}")
                    print(f"   Profile Complete: {match.get('profile_complete')}")
                    print(f"   Last Activity: {match.get('last_activity')}")
        else:
            print(f"❌ Failed to get discovery results: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
        
        # Test AI recommendations
        response = requests.get(f"{API_BASE_URL}/api/ai-recommendations/{user_id}")
        
        if response.status_code == 200:
            ai_results = response.json()
            print(f"\n✅ AI recommendations returned {len(ai_results)} potential matches")
            
            # Show the first 2 AI recommendations
            if ai_results and len(ai_results) > 0:
                print("\nSample of AI recommendations:")
                for j, match in enumerate(ai_results[:2]):
                    print(f"{j+1}. User ID: {match.get('user_id')}")
                    print(f"   Username: {match.get('username')}")
                    print(f"   Compatibility: {match.get('ai_compatibility', {}).get('compatibility_percentage')}%")
                    print(f"   Profile Complete: {match.get('profile_complete')}")
        else:
            print(f"❌ Failed to get AI recommendations: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)

def main():
    print("🔍 Solm8 Database and Discovery Check")
    print_separator()
    
    # Check users in the database
    complete_users = check_database_users()
    
    print_separator()
    
    # Test discovery with real users
    test_discovery_with_real_users(complete_users)
    
    print_separator()
    print("✅ Check completed")

if __name__ == "__main__":
    main()