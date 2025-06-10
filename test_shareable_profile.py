#!/usr/bin/env python3

import requests
import json
import base64
import tempfile
from PIL import Image
import io

BASE_URL = "http://localhost:8001"

def create_test_image():
    """Create a test image for upload"""
    img = Image.new('RGB', (100, 100), color = 'red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    return img_buffer

def test_new_endpoints():
    print("🚀 Testing New Shareable Profile Endpoints for Solm8\n")
    
    # Step 1: Create a demo user
    print("1. Creating demo user...")
    response = requests.post(f"{BASE_URL}/api/create-demo-user")
    if response.status_code != 200:
        print(f"❌ Failed to create demo user: {response.status_code}")
        return
    
    user_data = response.json()
    user_id = user_data['user_id']
    username = user_data['username']
    print(f"✅ Created user: {username} (ID: {user_id})")
    
    # Step 2: Test social links endpoints
    print("\n2. Testing social links...")
    social_links_data = {
        "twitter": "https://twitter.com/demo_trader",
        "discord": "https://discord.gg/demo",
        "telegram": "https://t.me/demo_trader",
        "website": "https://demo-trader.com"
    }
    
    # Update social links
    response = requests.post(f"{BASE_URL}/api/update-social-links/{user_id}", 
                           json=social_links_data)
    if response.status_code == 200:
        print("✅ Social links updated successfully")
    else:
        print(f"❌ Failed to update social links: {response.status_code}")
    
    # Get social links
    response = requests.get(f"{BASE_URL}/api/social-links/{user_id}")
    if response.status_code == 200:
        links = response.json()
        print(f"✅ Retrieved social links: {links}")
    else:
        print(f"❌ Failed to get social links: {response.status_code}")
    
    # Step 3: Test trading highlights
    print("\n3. Testing trading highlights...")
    
    # Upload trading highlight image
    test_image = create_test_image()
    files = {'file': ('test_pnl.jpg', test_image, 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/api/upload-trading-highlight/{user_id}", files=files)
    
    if response.status_code == 200:
        upload_result = response.json()
        image_data = upload_result['image_data']
        print("✅ Trading highlight image uploaded successfully")
        
        # Save trading highlight with details
        highlight_data = {
            "title": "Epic BONK Trade - 300% Gain!",
            "description": "Bought BONK at the perfect dip and rode it to the moon! 🚀",
            "image_data": image_data,
            "highlight_type": "pnl_screenshot", 
            "date_achieved": "2024-01-15",
            "profit_loss": "+$5,000",
            "percentage_gain": "+300%"
        }
        
        response = requests.post(f"{BASE_URL}/api/save-trading-highlight/{user_id}", 
                               json=highlight_data)
        if response.status_code == 200:
            highlight_result = response.json()
            highlight_id = highlight_result['highlight']['highlight_id']
            print("✅ Trading highlight saved successfully")
            
            # Get all highlights
            response = requests.get(f"{BASE_URL}/api/trading-highlights/{user_id}")
            if response.status_code == 200:
                highlights = response.json()
                print(f"✅ Retrieved {len(highlights)} trading highlights")
                
                # Test delete highlight
                response = requests.delete(f"{BASE_URL}/api/trading-highlights/{highlight_id}")
                if response.status_code == 200:
                    print("✅ Trading highlight deleted successfully")
                else:
                    print(f"❌ Failed to delete highlight: {response.status_code}")
            else:
                print(f"❌ Failed to get highlights: {response.status_code}")
        else:
            print(f"❌ Failed to save highlight: {response.status_code}")
    else:
        print(f"❌ Failed to upload image: {response.status_code}")
    
    # Step 4: Test public profile
    print("\n4. Testing public profile...")
    response = requests.get(f"{BASE_URL}/api/public-profile/{username}")
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Public profile retrieved successfully")
        print(f"   Display Name: {profile['display_name']}")
        print(f"   Trading Experience: {profile['trading_experience']}")
        print(f"   Social Links: {len(profile.get('social_links', {}))}")
        print(f"   Trading Highlights: {len(profile.get('trading_highlights', []))}")
    else:
        print(f"❌ Failed to get public profile: {response.status_code}")
    
    print("\n🎉 Shareable Profile Endpoint Testing Complete!")

if __name__ == "__main__":
    test_new_endpoints()