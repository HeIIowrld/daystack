"""Naver API wrapper - Geocoding and Directions"""
import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, TRAVEL_TIME_BUFFER


def geocode(address):
    """Convert address to coordinates (longitude,latitude)"""
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
    }
    response = requests.get(url, headers=headers, params={"query": address})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('addresses'):
            x = data['addresses'][0]['x']
            y = data['addresses'][0]['y']
            return f"{x},{y}"
    return None


def get_travel_duration(start, goal):
    """
    Get travel duration between two points
    
    Args:
        start (str): "longitude,latitude" 
        goal (str): "longitude,latitude"
    
    Returns:
        int: Duration in minutes (including buffer)
    """
    url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
    }
    params = {
        "start": start,
        "goal": goal,
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Extract duration from traoptimal route
        duration_ms = data['route']['traoptimal'][0]['summary']['duration']
        duration_min = int(duration_ms / 1000 / 60)
        return duration_min + TRAVEL_TIME_BUFFER
    
    return 0


def get_travel_duration_from_addresses(start_address, goal_address):
    """Get travel duration between two addresses"""
    start_coords = geocode(start_address)
    goal_coords = geocode(goal_address)
    
    if not start_coords or not goal_coords:
        return 0
    
    return get_travel_duration(start_coords, goal_coords)


if __name__ == "__main__":
    # Test
    print("Testing Naver API...")
    
    # Test geocoding
    coords = geocode("강남역")
    print(f"강남역 coordinates: {coords}")
    
    # Test duration
    duration = get_travel_duration_from_addresses("강남역", "판교역")
    print(f"강남역 → 판교역: {duration}분")

