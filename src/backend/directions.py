"""
Directions module for calculating travel time between locations
Uses Naver Maps Directions 5 API
"""

import requests
from config import Config
from geocoding import get_location_coords


def get_travel_time(start_coords, end_coords, include_buffer=True):
    """
    Calculate travel time between two coordinate points
    
    Args:
        start_coords (str): Starting coordinates in "longitude,latitude" format
        end_coords (str): Ending coordinates in "longitude,latitude" format
        include_buffer (bool): Whether to include safety buffer time
    
    Returns:
        int: Travel time in minutes (including buffer if enabled)
    """
    url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    
    headers = {
        "X-NCP-APIGW-API-KEY-ID": Config.NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": Config.NAVER_CLIENT_SECRET,
    }
    
    params = {
        "start": start_coords,
        "goal": end_coords,
        "option": "trafast"  # trafast = 실시간 빠른길
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            try:
                # 밀리초(ms) 단위로 반환되므로 분(minute)으로 변환
                duration_ms = data['route']['trafast'][0]['summary']['duration']
                duration_min = int(duration_ms / 1000 / 60)
                
                # Add buffer time for safety margin
                if include_buffer:
                    duration_min += Config.TRAVEL_TIME_BUFFER
                
                return duration_min
                
            except (KeyError, IndexError) as e:
                print(f"Error parsing directions response: {e}")
                return 0
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return 0
            
    except requests.exceptions.RequestException as e:
        print(f"Error making directions request: {e}")
        return 0


def get_travel_time_from_addresses(start_address, end_address, include_buffer=True):
    """
    Calculate travel time between two addresses
    
    Args:
        start_address (str): Starting address
        end_address (str): Ending address
        include_buffer (bool): Whether to include safety buffer time
    
    Returns:
        int: Travel time in minutes, or 0 if geocoding fails
    """
    # Geocode both addresses
    start_coords = get_location_coords(start_address)
    end_coords = get_location_coords(end_address)
    
    if not start_coords or not end_coords:
        print(f"Failed to geocode addresses: {start_address} -> {end_address}")
        return 0
    
    return get_travel_time(start_coords, end_coords, include_buffer)


def test_directions():
    """Test function for directions/travel time calculation"""
    test_routes = [
        ("강남역", "판교역"),
        ("서울대학교", "강남역"),
    ]
    
    print("=== Travel Time Calculation Test ===")
    print(f"(Buffer time: {Config.TRAVEL_TIME_BUFFER} minutes)")
    print()
    
    for start, end in test_routes:
        travel_time = get_travel_time_from_addresses(start, end)
        if travel_time > 0:
            print(f"✓ {start} → {end}: {travel_time}분")
        else:
            print(f"✗ {start} → {end}: Failed to calculate")
    print()


if __name__ == "__main__":
    # Validate configuration before running tests
    try:
        Config.validate()
        test_directions()
    except ValueError as e:
        print(f"Configuration error: {e}")

