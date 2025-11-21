"""
Test script that matches the exact curl format that worked
"""
import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

print("Testing with EXACT curl format...\n")

# Test coordinates from your curl example
start = "127.1058342,37.359708"
goal = "129.075986,35.179470"

# URL from curl (maps.apigw.ntruss.com)
url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"

# Headers matching curl exactly (lowercase)
headers = {
    "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
    "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
}

# Parameters
params = {
    "start": start,
    "goal": goal
}

print(f"URL: {url}")
print(f"Headers: x-ncp-apigw-api-key-id: {NAVER_CLIENT_ID[:10]}...")
print(f"Params: start={start}, goal={goal}\n")

try:
    response = requests.get(url, headers=headers, params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS!\n")
        data = response.json()
        
        # Extract duration
        duration_ms = data['route']['traoptimal'][0]['summary']['duration']
        duration_min = int(duration_ms / 1000 / 60)
        
        print(f"Duration: {duration_min} minutes")
        print(f"\nFull response:")
        print(f"  Distance: {data['route']['traoptimal'][0]['summary']['distance']} meters")
        print(f"  Toll fare: {data['route']['traoptimal'][0]['summary'].get('tollFare', 0)} KRW")
        
    else:
        print(f"❌ FAILED")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

