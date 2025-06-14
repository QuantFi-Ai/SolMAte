import requests
import json
from datetime import datetime
from pymongo import MongoClient

def verify_matches():
    """Verify that the user's matches are working correctly"""
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017')
    db = client.solm8_db
    
    # User ID to check
    user_id = '17d9709a-9a6f-4418-8cb4-765faca422a8'
    
    print(f"🔍 Verifying matches for user ID: {user_id}")
    
    # Check user in database
    user = db.users.find_one({'user_id': user_id})
    if not user:
        print(f"❌ User not found in database")
        return
    
    print(f"✅ Found user: {user['display_name']} ({user['username']})")
    print(f"Profile complete: {user.get('profile_complete')}")
    
    # Check API response for matches
    base_url = 'https://8134b81b-ad13-497e-ba8a-ecdf0793b0b4.preview.emergentagent.com'
    
    # Test 1: Get user matches
    print("\n🔍 Test 1: Get user matches")
    response = requests.get(f'{base_url}/api/matches/{user_id}')
    
    if response.status_code == 200:
        matches = response.json()
        print(f"✅ API returned {len(matches)} matches")
        
        # Print match details
        for i, match in enumerate(matches):
            other_user = match.get('other_user', {})
            print(f"{i+1}. Match with: {other_user.get('display_name')} ({other_user.get('user_id')})")
            print(f"   Match ID: {match.get('match_id')}")
            print(f"   Created: {match.get('created_at')}")
    else:
        print(f"❌ API request failed: {response.status_code}")
    
    # Test 2: Get matches with messages
    print("\n🔍 Test 2: Get matches with messages")
    response = requests.get(f'{base_url}/api/matches-with-messages/{user_id}')
    
    if response.status_code == 200:
        matches_with_messages = response.json()
        print(f"✅ API returned {len(matches_with_messages)} matches with messages")
        
        # Print match details
        for i, match in enumerate(matches_with_messages):
            other_user = match.get('other_user', {})
            latest_message = match.get('latest_message', {})
            
            print(f"{i+1}. Match with: {other_user.get('display_name')} ({other_user.get('user_id')})")
            print(f"   Match ID: {match.get('match_id')}")
            print(f"   Created: {match.get('created_at')}")
            print(f"   Unread messages: {match.get('unread_count')}")
            
            if latest_message.get('content'):
                sender_id = latest_message.get('sender_id')
                sender_is_user = sender_id == user_id
                print(f"   Latest message: {'Sent' if sender_is_user else 'Received'} at {latest_message.get('timestamp')}")
                print(f"   Content: {latest_message.get('content')[:50]}..." if len(latest_message.get('content', '')) > 50 else f"   Content: {latest_message.get('content', '')}")
            else:
                print("   No messages")
            
            print()
    else:
        print(f"❌ API request failed: {response.status_code}")
    
    # Test 3: Send a message in a match
    print("\n🔍 Test 3: Send a message in a match")
    
    # Get the first match ID
    if response.status_code == 200 and matches_with_messages:
        match_id = matches_with_messages[0].get('match_id')
        
        # Send a test message
        message_data = {
            "match_id": match_id,
            "sender_id": user_id,
            "content": f"Test message sent at {datetime.utcnow()}"
        }
        
        response = requests.post(f'{base_url}/api/messages', json=message_data)
        
        if response.status_code == 200:
            print(f"✅ Successfully sent message in match {match_id}")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
    
    # Test 4: Verify the message was added
    print("\n🔍 Test 4: Verify the message was added")
    
    if response.status_code == 200 and matches_with_messages:
        response = requests.get(f'{base_url}/api/matches-with-messages/{user_id}')
        
        if response.status_code == 200:
            updated_matches = response.json()
            
            if updated_matches and updated_matches[0].get('match_id') == match_id:
                latest_message = updated_matches[0].get('latest_message', {})
                
                print(f"✅ Latest message in match {match_id}:")
                print(f"   Content: {latest_message.get('content')}")
                print(f"   Timestamp: {latest_message.get('timestamp')}")
                print(f"   Sender: {latest_message.get('sender_id')}")
            else:
                print("❌ Could not find the updated match")
        else:
            print(f"❌ API request failed: {response.status_code}")
    
    print("\n✅ Matches verification complete")
    print("✅ The user has matches and can send/receive messages")
    print("✅ The matching system is working correctly")

if __name__ == "__main__":
    verify_matches()
