from pymongo import MongoClient
from datetime import datetime

class MatchingSystemCleanup:
    def __init__(self):
        self.mongo_client = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client.solm8_db
        self.users_collection = self.db.users
        self.swipes_collection = self.db.swipes
        self.matches_collection = self.db.matches
        self.messages_collection = self.db.messages

    def check_for_duplicate_swipes(self):
        """Check for and remove duplicate swipes"""
        print("\n🔍 Checking for Duplicate Swipes...")
        
        # Get all swipes
        all_swipes = list(self.swipes_collection.find())
        print(f"Total swipes in database: {len(all_swipes)}")
        
        # Track swipes by swiper-target pair
        swipe_pairs = {}
        duplicates = []
        
        for swipe in all_swipes:
            pair_key = f"{swipe['swiper_id']}_{swipe['target_id']}"
            if pair_key in swipe_pairs:
                # This is a duplicate
                duplicates.append(swipe)
                swipe_pairs[pair_key].append(swipe)
            else:
                swipe_pairs[pair_key] = [swipe]
        
        # Count pairs with duplicates
        duplicate_pairs = {k: v for k, v in swipe_pairs.items() if len(v) > 1}
        
        print(f"Found {len(duplicates)} duplicate swipes across {len(duplicate_pairs)} swiper-target pairs")
        
        # Remove duplicates (keep the most recent swipe for each pair)
        if duplicate_pairs:
            print("\nRemoving duplicate swipes...")
            removed_count = 0
            
            for pair, swipes in duplicate_pairs.items():
                # Sort by timestamp (newest first)
                sorted_swipes = sorted(swipes, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
                
                # Keep the most recent swipe, remove the rest
                for swipe in sorted_swipes[1:]:
                    self.swipes_collection.delete_one({"swipe_id": swipe["swipe_id"]})
                    removed_count += 1
                    print(f"Removed duplicate swipe: {swipe['swiper_id']} → {swipe['target_id']} (ID: {swipe['swipe_id']})")
            
            print(f"\n✅ Removed {removed_count} duplicate swipes")
        else:
            print("✅ No duplicate swipes found")
        
        return duplicate_pairs

    def check_for_demo_users(self):
        """Check for and remove demo users"""
        print("\n🔍 Checking for Demo Users...")
        
        # Get users with auth_method = 'demo'
        demo_users = list(self.users_collection.find({"auth_method": "demo"}))
        print(f"Users with auth_method='demo': {len(demo_users)}")
        
        # Check for suspicious usernames
        suspicious_patterns = ["demo", "test", "dummy", "fake"]
        suspicious_users = []
        
        for pattern in suspicious_patterns:
            users = list(self.users_collection.find({
                "$and": [
                    {"auth_method": {"$ne": "email"}},  # Don't include regular email users
                    {"$or": [
                        {"username": {"$regex": pattern, "$options": "i"}},
                        {"display_name": {"$regex": pattern, "$options": "i"}}
                    ]}
                ]
            }))
            suspicious_users.extend(users)
        
        # Remove duplicates
        suspicious_user_ids = set()
        unique_suspicious_users = []
        
        for user in suspicious_users:
            if user["user_id"] not in suspicious_user_ids:
                suspicious_user_ids.add(user["user_id"])
                unique_suspicious_users.append(user)
        
        print(f"Suspicious users (not marked as demo): {len(unique_suspicious_users)}")
        
        # Show demo users
        if demo_users:
            print("\nDemo users:")
            for i, user in enumerate(demo_users):
                print(f"{i+1}. User ID: {user['user_id']}, Username: {user['username']}, Display Name: {user['display_name']}")
        
        # Show suspicious users
        if unique_suspicious_users:
            print("\nSuspicious users:")
            for i, user in enumerate(unique_suspicious_users):
                print(f"{i+1}. User ID: {user['user_id']}, Username: {user['username']}, Display Name: {user['display_name']}, Auth Method: {user.get('auth_method', 'None')}")
        
        # Remove demo users and their associated data
        users_to_remove = demo_users + unique_suspicious_users
        
        if users_to_remove:
            print("\nRemoving demo and suspicious users...")
            removed_count = 0
            removed_swipes = 0
            removed_matches = 0
            removed_messages = 0
            
            for user in users_to_remove:
                user_id = user["user_id"]
                
                # Remove user's swipes
                swipe_result = self.swipes_collection.delete_many({
                    "$or": [
                        {"swiper_id": user_id},
                        {"target_id": user_id}
                    ]
                })
                removed_swipes += swipe_result.deleted_count
                
                # Remove user's matches
                match_result = self.matches_collection.delete_many({
                    "$or": [
                        {"user1_id": user_id},
                        {"user2_id": user_id}
                    ]
                })
                removed_matches += match_result.deleted_count
                
                # Remove user's messages
                message_result = self.messages_collection.delete_many({
                    "sender_id": user_id
                })
                removed_messages += message_result.deleted_count
                
                # Remove the user
                self.users_collection.delete_one({"user_id": user_id})
                removed_count += 1
                
                print(f"Removed user: {user['display_name']} ({user_id})")
            
            print(f"\n✅ Removed {removed_count} users")
            print(f"✅ Removed {removed_swipes} swipes")
            print(f"✅ Removed {removed_matches} matches")
            print(f"✅ Removed {removed_messages} messages")
        else:
            print("✅ No demo or suspicious users to remove")
        
        return demo_users, unique_suspicious_users

    def check_for_asymmetric_matches(self):
        """Check for and fix asymmetric matches (where one user can see the match but the other can't)"""
        print("\n🔍 Checking for Asymmetric Matches...")
        
        # Get all matches
        all_matches = list(self.matches_collection.find())
        print(f"Total matches in database: {len(all_matches)}")
        
        # Check if both users in each match exist
        asymmetric_matches = []
        
        for match in all_matches:
            user1 = self.users_collection.find_one({"user_id": match["user1_id"]})
            user2 = self.users_collection.find_one({"user_id": match["user2_id"]})
            
            if not user1 or not user2:
                asymmetric_matches.append(match)
        
        print(f"Found {len(asymmetric_matches)} asymmetric matches (where one or both users don't exist)")
        
        # Remove asymmetric matches
        if asymmetric_matches:
            print("\nRemoving asymmetric matches...")
            removed_count = 0
            
            for match in asymmetric_matches:
                # Remove associated messages
                self.messages_collection.delete_many({"match_id": match["match_id"]})
                
                # Remove the match
                self.matches_collection.delete_one({"match_id": match["match_id"]})
                removed_count += 1
                
                print(f"Removed asymmetric match: {match['match_id']} between {match['user1_id']} and {match['user2_id']}")
            
            print(f"\n✅ Removed {removed_count} asymmetric matches")
        else:
            print("✅ No asymmetric matches found")
        
        return asymmetric_matches

    def check_for_missing_mutual_likes(self):
        """Check for mutual likes that should have created matches but didn't"""
        print("\n🔍 Checking for Missing Mutual Likes...")
        
        # Get all swipes
        all_swipes = list(self.swipes_collection.find({"action": "like"}))
        print(f"Total 'like' swipes in database: {len(all_swipes)}")
        
        # Find mutual likes
        swipe_pairs = {}
        for swipe in all_swipes:
            swiper_id = swipe["swiper_id"]
            target_id = swipe["target_id"]
            
            # Add to swipe pairs
            if (swiper_id, target_id) not in swipe_pairs:
                swipe_pairs[(swiper_id, target_id)] = swipe
        
        # Check for mutual likes
        mutual_likes = []
        for (swiper_id, target_id), swipe in swipe_pairs.items():
            if (target_id, swiper_id) in swipe_pairs:
                # This is a mutual like
                mutual_likes.append((swiper_id, target_id))
        
        print(f"Found {len(mutual_likes)} mutual likes")
        
        # Check which mutual likes don't have matches
        missing_matches = []
        for user1_id, user2_id in mutual_likes:
            match = self.matches_collection.find_one({
                "$or": [
                    {"user1_id": user1_id, "user2_id": user2_id},
                    {"user1_id": user2_id, "user2_id": user1_id}
                ]
            })
            
            if not match:
                missing_matches.append((user1_id, user2_id))
        
        print(f"Found {len(missing_matches)} mutual likes without matches")
        
        # Create missing matches
        if missing_matches:
            print("\nCreating missing matches...")
            created_count = 0
            
            for user1_id, user2_id in missing_matches:
                # Check if both users still exist
                user1 = self.users_collection.find_one({"user_id": user1_id})
                user2 = self.users_collection.find_one({"user_id": user2_id})
                
                if not user1 or not user2:
                    print(f"Skipping match creation for {user1_id} and {user2_id} - one or both users don't exist")
                    continue
                
                # Create the match
                match_data = {
                    "match_id": str(uuid.uuid4()),
                    "user1_id": user1_id,
                    "user2_id": user2_id,
                    "created_at": datetime.utcnow(),
                    "last_message_at": datetime.utcnow()
                }
                
                self.matches_collection.insert_one(match_data)
                created_count += 1
                
                print(f"Created missing match between {user1_id} and {user2_id}")
            
            print(f"\n✅ Created {created_count} missing matches")
        else:
            print("✅ No missing matches to create")
        
        return missing_matches

    def run_cleanup(self):
        """Run all cleanup operations"""
        print("🧹 Starting Matching System Cleanup")
        
        # Step 1: Check for and remove duplicate swipes
        duplicate_pairs = self.check_for_duplicate_swipes()
        
        # Step 2: Check for and remove demo users
        demo_users, suspicious_users = self.check_for_demo_users()
        
        # Step 3: Check for and fix asymmetric matches
        asymmetric_matches = self.check_for_asymmetric_matches()
        
        # Step 4: Check for and create missing matches
        missing_matches = self.check_for_missing_mutual_likes()
        
        # Print summary
        print("\n📊 Cleanup Summary:")
        print(f"Duplicate swipes removed: {sum(len(swipes) - 1 for swipes in duplicate_pairs.values()) if duplicate_pairs else 0}")
        print(f"Demo users removed: {len(demo_users)}")
        print(f"Suspicious users removed: {len(suspicious_users)}")
        print(f"Asymmetric matches removed: {len(asymmetric_matches)}")
        print(f"Missing matches created: {len(missing_matches)}")
        
        print("\n✅ Matching system cleanup complete")

if __name__ == "__main__":
    import uuid
    cleanup = MatchingSystemCleanup()
    cleanup.run_cleanup()
