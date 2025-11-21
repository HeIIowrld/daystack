"""
Directions module for calculating travel time between locations
Uses Naver Maps Directions 5 API
"""

import requests

from .config import Config
from .geocoding import get_location_coords


def get_travel_time(start_coords, end_coords, include_buffer=True):
    """
    Calculate travel time using Naver Maps API (aligned with valid curl request).
    """
    # UPDATED: Domain changed from 'naveropenapi' to 'maps' to match your curl command
    url = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
    
    headers = {
        "X-NCP-APIGW-API-KEY-ID": Config.NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": Config.NAVER_CLIENT_SECRET,
    }
    
    params = {
        "start": start_coords, # Format: "long,lat"
        "goal": end_coords,    # Format: "long,lat"
        "option": "trafast"    # Optional: Remove this line to match curl default (traoptimal)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the API returned code 0 (Success) inside the JSON body
            if data.get('code') != 0:
                print(f"API Logical Error: {data.get('message')}")
                return 0

            try:
                # Path data is usually under route -> trafast (or traoptimal) -> 0 -> summary
                route_key = "trafast" if params.get("option") == "trafast" else "traoptimal"
                
                duration_ms = data['route'][route_key][0]['summary']['duration']
                duration_min = int(duration_ms / 1000 / 60)
                
                if include_buffer:
                    duration_min += Config.TRAVEL_TIME_BUFFER
                
                return duration_min
                
            except (KeyError, IndexError) as e:
                print(f"Error parsing directions response structure: {e}")
                # Debug: Print keys to see what was returned
                print(f"Available keys: {data.get('route', {}).keys()}")
                return 0
        else:
            print(f"HTTP Error: {response.status_code}")
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


