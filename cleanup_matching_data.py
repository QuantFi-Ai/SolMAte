import os
from pymongo import MongoClient

def cleanup_matching_data():
    """
    Clean up demo users and duplicate swipes from the database
    to fix matching system issues.
    """
    print("🧹 Starting database cleanup for matching system...")
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(MONGO_URL)
    db = client.solm8_db
    
    # Step 1: Identify and remove demo users
    print("\n1️⃣ Cleaning up demo users...")
    
    # Find users with auth_method = 'demo'
    demo_users = list(db.users.find({"auth_method": "demo"}))
    print(f"Found {len(demo_users)} users with auth_method = 'demo'")
    
    # Find users with suspicious usernames
    suspicious_patterns = ['demo_', 'crypto_whale_', 'sol_degen_', 'test_']
    suspicious_query = {"$or": [{"username": {"$regex": pattern}} for pattern in suspicious_patterns]}
    suspicious_users = list(db.users.find(suspicious_query))
    print(f"Found {len(suspicious_users)} users with suspicious usernames")
    
    # Combine and deduplicate user IDs to remove
    user_ids_to_remove = set()
    
    for user in demo_users:
        user_ids_to_remove.add(user.get('user_id'))
        print(f"  Will remove demo user: {user.get('username')} (ID: {user.get('user_id')})")
    
    for user in suspicious_users:
        if user.get('auth_method') != 'email':  # Don't remove real email users
            user_ids_to_remove.add(user.get('user_id'))
            print(f"  Will remove suspicious user: {user.get('username')} (ID: {user.get('user_id')})")
    
    # Remove demo users
    if user_ids_to_remove:
        result = db.users.delete_many({"user_id": {"$in": list(user_ids_to_remove)}})
        print(f"Removed {result.deleted_count} demo/suspicious users")
        
        # Also remove any matches involving these users
        result = db.matches.delete_many({
            "$or": [
                {"user1_id": {"$in": list(user_ids_to_remove)}},
                {"user2_id": {"$in": list(user_ids_to_remove)}}
            ]
        })
        print(f"Removed {result.deleted_count} matches involving demo/suspicious users")
        
        # Also remove any swipes involving these users
        result = db.swipes.delete_many({
            "$or": [
                {"swiper_id": {"$in": list(user_ids_to_remove)}},
                {"target_id": {"$in": list(user_ids_to_remove)}}
            ]
        })
        print(f"Removed {result.deleted_count} swipes involving demo/suspicious users")
    else:
        print("No demo/suspicious users to remove")
    
    # Step 2: Clean up duplicate swipes
    print("\n2️⃣ Cleaning up duplicate swipes...")
    
    # Find all swipes
    all_swipes = list(db.swipes.find())
    print(f"Found {len(all_swipes)} total swipes")
    
    # Track unique swiper-target pairs
    unique_pairs = {}
    duplicate_swipe_ids = []
    
    for swipe in all_swipes:
        swipe_id = swipe.get('swipe_id')
        swiper_id = swipe.get('swiper_id')
        target_id = swipe.get('target_id')
        action = swipe.get('action')
        pair_key = f"{swiper_id}_{target_id}_{action}"
        
        if pair_key in unique_pairs:
            # This is a duplicate, mark for removal
            duplicate_swipe_ids.append(swipe_id)
        else:
            # This is the first occurrence, keep it
            unique_pairs[pair_key] = swipe_id
    
    # Remove duplicate swipes
    if duplicate_swipe_ids:
        result = db.swipes.delete_many({"swipe_id": {"$in": duplicate_swipe_ids}})
        print(f"Removed {result.deleted_count} duplicate swipes")
    else:
        print("No duplicate swipes to remove")
    
    # Step 3: Check for orphaned matches
    print("\n3️⃣ Checking for orphaned matches...")
    
    # Find all matches
    all_matches = list(db.matches.find())
    print(f"Found {len(all_matches)} total matches")
    
    # Check each match to ensure both users exist
    orphaned_match_ids = []
    
    for match in all_matches:
        match_id = match.get('match_id')
        user1_id = match.get('user1_id')
        user2_id = match.get('user2_id')
        
        user1 = db.users.find_one({"user_id": user1_id})
        user2 = db.users.find_one({"user_id": user2_id})
        
        if not user1 or not user2:
            orphaned_match_ids.append(match_id)
            print(f"  Orphaned match found: {match_id} (User1 exists: {bool(user1)}, User2 exists: {bool(user2)})")
    
    # Remove orphaned matches
    if orphaned_match_ids:
        result = db.matches.delete_many({"match_id": {"$in": orphaned_match_ids}})
        print(f"Removed {result.deleted_count} orphaned matches")
        
        # Also remove messages for these matches
        result = db.messages.delete_many({"match_id": {"$in": orphaned_match_ids}})
        print(f"Removed {result.deleted_count} messages from orphaned matches")
    else:
        print("No orphaned matches to remove")
    
    # Step 4: Check for inconsistent matches (missing mutual likes)
    print("\n4️⃣ Checking for inconsistent matches...")
    
    # Find all matches again (after orphaned ones were removed)
    all_matches = list(db.matches.find())
    
    # Check each match to ensure both users liked each other
    inconsistent_match_ids = []
    
    for match in all_matches:
        match_id = match.get('match_id')
        user1_id = match.get('user1_id')
        user2_id = match.get('user2_id')
        
        # Check if both users liked each other
        user1_liked_user2 = db.swipes.find_one({
            "swiper_id": user1_id,
            "target_id": user2_id,
            "action": "like"
        })
        
        user2_liked_user1 = db.swipes.find_one({
            "swiper_id": user2_id,
            "target_id": user1_id,
            "action": "like"
        })
        
        if not user1_liked_user2 or not user2_liked_user1:
            inconsistent_match_ids.append(match_id)
            print(f"  Inconsistent match found: {match_id}")
            print(f"    User1 liked User2: {bool(user1_liked_user2)}")
            print(f"    User2 liked User1: {bool(user2_liked_user1)}")
    
    # Remove inconsistent matches
    if inconsistent_match_ids:
        result = db.matches.delete_many({"match_id": {"$in": inconsistent_match_ids}})
        print(f"Removed {result.deleted_count} inconsistent matches")
        
        # Also remove messages for these matches
        result = db.messages.delete_many({"match_id": {"$in": inconsistent_match_ids}})
        print(f"Removed {result.deleted_count} messages from inconsistent matches")
    else:
        print("No inconsistent matches to remove")
    
    print("\n✅ Database cleanup completed successfully!")
    
    # Print summary of current database state
    users_count = db.users.count_documents({})
    matches_count = db.matches.count_documents({})
    swipes_count = db.swipes.count_documents({})
    messages_count = db.messages.count_documents({})
    
    print("\n📊 Current Database State:")
    print(f"  Users: {users_count}")
    print(f"  Matches: {matches_count}")
    print(f"  Swipes: {swipes_count}")
    print(f"  Messages: {messages_count}")

if __name__ == "__main__":
    cleanup_matching_data()
