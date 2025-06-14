from pymongo import MongoClient
import requests
import json
from datetime import datetime

def fix_matches_query_issue():
    """Fix the issue with matches query not returning all matches"""
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017')
    db = client.solm8_db
    
    # User ID to check
    user_id = '17d9709a-9a6f-4418-8cb4-765faca422a8'
    
    print(f"🔍 Investigating matches query issue for user ID: {user_id}")
    
    # Check user in database
    user = db.users.find_one({'user_id': user_id})
    if not user:
        print(f"❌ User not found in database")
        return
    
    print(f"✅ Found user: {user['display_name']} ({user['username']})")
    
    # Check matches using different query approaches
    matches_or = list(db.matches.find({
        '$or': [
            {'user1_id': user_id},
            {'user2_id': user_id}
        ]
    }))
    
    matches_user1 = list(db.matches.find({'user1_id': user_id}))
    matches_user2 = list(db.matches.find({'user2_id': user_id}))
    
    print(f"Matches using $or query: {len(matches_or)}")
    print(f"Matches as user1: {len(matches_user1)}")
    print(f"Matches as user2: {len(matches_user2)}")
    
    # Check API response
    base_url = 'https://2cb408cb-0812-4c97-821c-53c0d3b60524.preview.emergentagent.com'
    response = requests.get(f'{base_url}/api/matches/{user_id}')
    api_matches = []
    
    if response.status_code == 200:
        api_matches = response.json()
        print(f"Matches from API: {len(api_matches)}")
    else:
        print(f"❌ API request failed: {response.status_code}")
    
    # Identify the issue
    if len(matches_or) < len(matches_user1) + len(matches_user2):
        print("❌ Query issue detected: $or query not returning all matches")
    
    if len(matches_or) == 0 and (len(matches_user1) > 0 or len(matches_user2) > 0):
        print("❌ Serious query issue: $or query returns nothing despite matches existing")
    
    # Check for type mismatches in user IDs
    print("\n🔍 Checking for type mismatches in user IDs...")
    
    # Get all matches that might involve this user
    potential_matches = []
    for match in db.matches.find():
        if str(match.get('user1_id')) == user_id or str(match.get('user2_id')) == user_id:
            potential_matches.append(match)
    
    print(f"Potential matches found: {len(potential_matches)}")
    
    # Check for type mismatches
    type_mismatches = []
    for match in potential_matches:
        user1_id = match.get('user1_id')
        user2_id = match.get('user2_id')
        
        if type(user1_id) != type(user_id) or type(user2_id) != type(user_id):
            type_mismatches.append({
                'match_id': match.get('match_id'),
                'user1_id': user1_id,
                'user1_type': type(user1_id).__name__,
                'user2_id': user2_id,
                'user2_type': type(user2_id).__name__,
                'expected_type': type(user_id).__name__
            })
    
    if type_mismatches:
        print(f"❌ Found {len(type_mismatches)} matches with type mismatches:")
        for mismatch in type_mismatches:
            print(f"  Match ID: {mismatch['match_id']}")
            print(f"  User1 ID: {mismatch['user1_id']} (Type: {mismatch['user1_type']})")
            print(f"  User2 ID: {mismatch['user2_id']} (Type: {mismatch['user2_type']})")
            print(f"  Expected Type: {mismatch['expected_type']}")
            print()
    else:
        print("✅ No type mismatches found")
    
    # Fix the issue by ensuring all user IDs are strings
    print("\n🔧 Fixing user ID types in matches collection...")
    
    updated_count = 0
    for match in potential_matches:
        match_id = match.get('match_id')
        user1_id = match.get('user1_id')
        user2_id = match.get('user2_id')
        
        # Convert IDs to strings if needed
        updates = {}
        if type(user1_id) != str:
            updates['user1_id'] = str(user1_id)
        
        if type(user2_id) != str:
            updates['user2_id'] = str(user2_id)
        
        if updates:
            db.matches.update_one(
                {'match_id': match_id},
                {'$set': updates}
            )
            updated_count += 1
            print(f"Updated match ID: {match_id}")
    
    print(f"✅ Updated {updated_count} matches")
    
    # Verify the fix
    print("\n🔍 Verifying the fix...")
    
    matches_after = list(db.matches.find({
        '$or': [
            {'user1_id': user_id},
            {'user2_id': user_id}
        ]
    }))
    
    print(f"Matches using $or query after fix: {len(matches_after)}")
    
    if len(matches_after) == len(matches_user1) + len(matches_user2):
        print("✅ Fix successful: $or query now returns all matches")
    else:
        print("❌ Fix unsuccessful: $or query still not returning all matches")
    
    # Check API response again
    response_after = requests.get(f'{base_url}/api/matches/{user_id}')
    
    if response_after.status_code == 200:
        api_matches_after = response_after.json()
        print(f"Matches from API after fix: {len(api_matches_after)}")
        
        if len(api_matches_after) == len(matches_after):
            print("✅ API response matches database query")
        else:
            print("❌ API response still doesn't match database query")
    else:
        print(f"❌ API request failed: {response_after.status_code}")

if __name__ == "__main__":
    fix_matches_query_issue()
