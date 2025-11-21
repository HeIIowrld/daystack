"""
Geocoding module for converting addresses to coordinates
Uses Naver Maps Geocoding API
"""

import requests
from config import Config


def get_location_coords(address):
    """
    Convert an address to coordinates (longitude, latitude)
    
    Args:
        address (str): Address to geocode (e.g., "분당구 불정로 6" or "강남역")
    
    Returns:
        str: Coordinates in "longitude,latitude" format, or None if not found
    """
    # Resolve location aliases
    address = Config.resolve_location(address)
    
    if not address:
        print(f"Error: Empty address provided")
        return None
    
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": Config.NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": Config.NAVER_CLIENT_SECRET,
    }
    params = {
        "query": address
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('addresses') and len(data['addresses']) > 0:
                # x: 경도(longitude), y: 위도(latitude)
                x = data['addresses'][0]['x']
                y = data['addresses'][0]['y']
                return f"{x},{y}"
            else:
                print(f"Warning: No results found for address: {address}")
                return None
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making geocoding request: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing geocoding response: {e}")
        return None


def test_geocoding():
    """Test function for geocoding"""
    test_addresses = [
        "분당구 불정로 6",
        "강남역",
        "판교역",
        "서울대학교"
    ]
    
    print("=== Geocoding Test ===")
    for address in test_addresses:
        coords = get_location_coords(address)
        if coords:
            print(f"✓ {address} -> {coords}")
        else:
            print(f"✗ {address} -> Failed to geocode")
    print()


if __name__ == "__main__":
    # Validate configuration before running tests
    try:
        Config.validate()
        test_geocoding()
    except ValueError as e:
        print(f"Configuration error: {e}")

