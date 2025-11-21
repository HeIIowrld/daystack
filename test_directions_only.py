"""Test ONLY directions (no geocoding) - using your curl coordinates"""
import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

print("Testing Directions API ONLY (no geocoding)\n")

# Use exact coordinates from your working curl
start = "127.1058342,37.359708"
goal = "129.075986,35.179470"

# Try BOTH URLs to see which works
urls_to_try = [
    ("naveropenapi", "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"),
    ("maps", "https://maps.apigw.ntruss.com/map-direction/v1/driving"),
]

for name, url in urls_to_try:
    print(f"Trying {name}: {url}")
    
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
    }
    
    params = {
        "start": start,
        "goal": goal
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            print(f"  SUCCESS with {name}!\n")
            data = response.json()
            duration_ms = data['route']['traoptimal'][0]['summary']['duration']
            duration_min = int(duration_ms / 1000 / 60)
            print(f"  Duration: {duration_min} minutes\n")
            break
        else:
            print(f"  FAILED: {response.status_code}")
            print(f"  Response: {response.text}\n")
            
    except Exception as e:
        print(f"  Exception: {e}\n")

