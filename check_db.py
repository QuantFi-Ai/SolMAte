from pymongo import MongoClient
import json
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.solm8_db

# Count users by auth method
total_users = db.users.count_documents({})
email_users = db.users.count_documents({"auth_method": "email"})
wallet_users = db.users.count_documents({"auth_method": "wallet"})
twitter_users = db.users.count_documents({"auth_method": "twitter"})
demo_users = db.users.count_documents({"auth_method": "demo"})
no_auth_users = db.users.count_documents({"auth_method": {"$exists": False}})

print(f"Total users: {total_users}")
print(f"Email users: {email_users}")
print(f"Wallet users: {wallet_users}")
print(f"Twitter users: {twitter_users}")
print(f"Demo users: {demo_users}")
print(f"Users with no auth_method: {no_auth_users}")

# Check profile completion
complete_profiles = db.users.count_documents({"profile_complete": True})
incomplete_profiles = db.users.count_documents({"profile_complete": False})
print(f"\nUsers with complete profiles: {complete_profiles}")
print(f"Users with incomplete profiles: {incomplete_profiles}")

# Check email users
print("\nEmail users details:")
email_users_list = list(db.users.find({"auth_method": "email"}))
for user in email_users_list:
    print(f"User ID: {user.get('user_id')}")
    print(f"Username: {user.get('username')}")
    print(f"Profile Complete: {user.get('profile_complete')}")
    print(f"Trading Experience: {user.get('trading_experience')}")
    print(f"Preferred Tokens: {user.get('preferred_tokens')}")
    print(f"Trading Style: {user.get('trading_style')}")
    print(f"Portfolio Size: {user.get('portfolio_size')}")
    print("---")

# Check users with no auth method
if no_auth_users > 0:
    print("\nUsers with no auth_method:")
    no_auth_users_list = list(db.users.find({"auth_method": {"$exists": False}}))
    for user in no_auth_users_list[:5]:  # Show first 5 only
        print(f"User ID: {user.get('user_id')}")
        print(f"Username: {user.get('username')}")
        print(f"Profile Complete: {user.get('profile_complete')}")
        print("---")

# Check for users with missing required fields but marked as complete
inconsistent_users = list(db.users.find({
    "profile_complete": True,
    "$or": [
        {"trading_experience": ""},
        {"preferred_tokens": []},
        {"trading_style": ""},
        {"portfolio_size": ""}
    ]
}))

if inconsistent_users:
    print("\nUsers incorrectly marked as complete:")
    for user in inconsistent_users:
        print(f"User ID: {user.get('user_id')}")
        print(f"Username: {user.get('username')}")
        print(f"Auth Method: {user.get('auth_method')}")
        print(f"Trading Experience: {user.get('trading_experience')}")
        print(f"Preferred Tokens: {user.get('preferred_tokens')}")
        print(f"Trading Style: {user.get('trading_style')}")
        print(f"Portfolio Size: {user.get('portfolio_size')}")
        print("---")
else:
    print("\nNo users incorrectly marked as complete")

# Check for users with all required fields but not marked as complete
should_be_complete = list(db.users.find({
    "profile_complete": False,
    "trading_experience": {"$ne": ""},
    "preferred_tokens": {"$ne": []},
    "trading_style": {"$ne": ""},
    "portfolio_size": {"$ne": ""}
}))

if should_be_complete:
    print("\nUsers that should be marked as complete:")
    for user in should_be_complete:
        print(f"User ID: {user.get('user_id')}")
        print(f"Username: {user.get('username')}")
        print(f"Auth Method: {user.get('auth_method')}")
        print(f"Trading Experience: {user.get('trading_experience')}")
        print(f"Preferred Tokens: {user.get('preferred_tokens')}")
        print(f"Trading Style: {user.get('trading_style')}")
        print(f"Portfolio Size: {user.get('portfolio_size')}")
        print("---")
else:
    print("\nNo users incorrectly marked as incomplete")

# Check recently created users
recent_users = list(db.users.find().sort("created_at", -1).limit(5))
print("\nRecently created users:")
for user in recent_users:
    print(f"User ID: {user.get('user_id')}")
    print(f"Username: {user.get('username')}")
    print(f"Auth Method: {user.get('auth_method')}")
    print(f"Created At: {user.get('created_at')}")
    print(f"Profile Complete: {user.get('profile_complete')}")
    print("---")

# Check recently active users
recent_active = list(db.users.find().sort("last_activity", -1).limit(5))
print("\nRecently active users:")
for user in recent_active:
    print(f"User ID: {user.get('user_id')}")
    print(f"Username: {user.get('username')}")
    print(f"Auth Method: {user.get('auth_method')}")
    print(f"Last Activity: {user.get('last_activity')}")
    print(f"Profile Complete: {user.get('profile_complete')}")
    print("---")