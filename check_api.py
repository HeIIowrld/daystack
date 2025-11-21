"""
Diagnostic script to check Naver API configuration
Run this to troubleshoot 401 errors
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("NAVER API CONFIGURATION CHECKER")
print("="*70)

# Check 1: .env file exists
print("\n1️⃣  Checking .env file...")
if os.path.exists('.env'):
    print("   ✓ .env file found")
else:
    print("   ❌ .env file NOT found")
    print("   → Create .env file: cp env.example .env")
    exit(1)

# Check 2: API keys loaded
print("\n2️⃣  Checking API keys...")
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

if not client_id:
    print("   ❌ NAVER_CLIENT_ID not found in .env")
    exit(1)

if not client_secret:
    print("   ❌ NAVER_CLIENT_SECRET not found in .env")
    exit(1)

if client_id == "your_client_id_here":
    print("   ❌ API keys still have placeholder values")
    print("   → Edit .env and add your real API keys")
    exit(1)

print(f"   ✓ NAVER_CLIENT_ID: {client_id[:15]}...")
print(f"   ✓ NAVER_CLIENT_SECRET: {client_secret[:15]}...")

# Check 3: Test API connection
print("\n3️⃣  Testing API connection...")
print("   Attempting to geocode '강남역'...")

import requests

url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret,
}

try:
    response = requests.get(url, headers=headers, params={"query": "강남역"})
    
    if response.status_code == 200:
        print("   ✅ API call successful!")
        data = response.json()
        if data.get('addresses'):
            coords = data['addresses'][0]
            print(f"   ✓ Geocoded: 강남역 → ({coords['x']}, {coords['y']})")
        else:
            print("   ⚠️  No results returned")
    
    elif response.status_code == 401:
        print("   ❌ ERROR 401: Permission Denied")
        print(f"   Response: {response.text}")
        print("\n   POSSIBLE CAUSES:")
        print("   1. API keys are incorrect")
        print("      → Double-check keys in Naver Cloud Console")
        print("   2. Maps Geocoding API not enabled")
        print("      → Go to: https://console.ncloud.com/")
        print("      → Navigate to: AI·NAVER API > Application")
        print("      → Click your application")
        print("      → Enable 'Maps Geocoding' API")
        print("   3. Subscription not active")
        print("      → Check if you have an active subscription")
        exit(1)
    
    else:
        print(f"   ❌ Unexpected error: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

except Exception as e:
    print(f"   ❌ Exception: {e}")
    exit(1)

# Check 4: Test Directions API
print("\n4️⃣  Testing Directions API...")
print("   Attempting to get directions: 강남역 → 판교역...")

# First get coordinates for both places
coords_start = None
coords_goal = None

for address in ["강남역", "판교역"]:
    response = requests.get(url, headers=headers, params={"query": address})
    if response.status_code == 200:
        data = response.json()
        if data.get('addresses'):
            coords = data['addresses'][0]
            if address == "강남역":
                coords_start = f"{coords['x']},{coords['y']}"
            else:
                coords_goal = f"{coords['x']},{coords['y']}"

if coords_start and coords_goal:
    dir_url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    dir_headers = {
        "x-ncp-apigw-api-key-id": client_id,
        "x-ncp-apigw-api-key": client_secret,
    }
    
    response = requests.get(dir_url, headers=dir_headers, params={
        "start": coords_start,
        "goal": coords_goal
    })
    
    if response.status_code == 200:
        print("   ✅ Directions API call successful!")
        data = response.json()
        duration_ms = data['route']['traoptimal'][0]['summary']['duration']
        duration_min = int(duration_ms / 1000 / 60)
        print(f"   ✓ Travel time: {duration_min}분")
    
    elif response.status_code == 401:
        print("   ❌ ERROR 401: Permission Denied")
        print(f"   Response: {response.text}")
        print("\n   POSSIBLE CAUSES:")
        print("   1. Directions 5 API not enabled")
        print("      → Go to: https://console.ncloud.com/")
        print("      → Navigate to: AI·NAVER API > Application")
        print("      → Click your application")
        print("      → Enable 'Directions 5' API")
        exit(1)
    
    else:
        print(f"   ❌ Unexpected error: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

print("\n" + "="*70)
print("✅ ALL CHECKS PASSED!")
print("="*70)
print("\nYour Naver API is configured correctly.")
print("You can now run: python daystack.py")

