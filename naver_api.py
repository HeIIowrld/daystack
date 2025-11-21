"""Naver API wrapper - Geocoding and Directions"""
import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, TRAVEL_TIME_BUFFER

# 1. CRITICAL FIX: Ensure no hidden newlines/spaces exist
CLIENT_ID = str(NAVER_CLIENT_ID).strip()
CLIENT_SECRET = str(NAVER_CLIENT_SECRET).strip()

def geocode(address):
    """Convert address to coordinates (longitude,latitude)"""
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    
    # 2. Use Standard Capitalization
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET,
    }
    
    try:
        response = requests.get(url, headers=headers, params={"query": address})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('addresses'):
                x = data['addresses'][0]['x']
                y = data['addresses'][0]['y']
                print(f"OK Geocoded: {address} -> {x},{y}")
                return f"{x},{y}"
            else:
                print(f"No result found for: {address}")
        else:
            print(f"Geocoding Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Geocoding Exception: {e}")
    
    return None


def get_travel_duration(start, goal):
    """Get travel duration between two points"""
    url = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
    
    # 2. Use Standard Capitalization here too
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET,
    }
    
    params = {
        "start": start,
        "goal": goal,
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Check if 'route' exists to avoid crashing on empty results
            if 'route' in data and 'traoptimal' in data['route']:
                duration_ms = data['route']['traoptimal'][0]['summary']['duration']
                duration_min = int(duration_ms / 1000 / 60)
                total = duration_min + TRAVEL_TIME_BUFFER
                print(f"OK Travel: {duration_min}min + {TRAVEL_TIME_BUFFER}min buffer = {total}min")
                return total
            else:
                print("Error: Unexpected API response structure")
        else:
            print(f"Directions Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Directions Exception: {e}")
    
    return 0