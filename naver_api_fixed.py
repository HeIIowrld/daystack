"""Naver API wrapper - Geocoding and Directions (FIXED URLs)"""
import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, TRAVEL_TIME_BUFFER


def geocode(address):
    """Convert address to coordinates (longitude,latitude)"""
    # Try new Maps API endpoint first
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
    }
    
    try:
        response = requests.get(url, headers=headers, params={"query": address})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('addresses'):
                x = data['addresses'][0]['x']
                y = data['addresses'][0]['y']
                print(f"✓ Geocoded: {address} → {x},{y}")
                return f"{x},{y}"
        else:
            print(f"❌ Geocoding Error ({response.status_code}): {address}")
            print(f"   Response: {response.text}")
            
            # Helpful error messages
            if response.status_code == 401:
                print("\n⚠️  ERROR 401: Permission Denied")
                print("   Possible causes:")
                print("   1. API keys are incorrect in .env file")
                print("   2. Maps Geocoding API not enabled in Naver Cloud Platform")
                print("   3. Check your subscription at: https://console.ncloud.com/")
                
    except Exception as e:
        print(f"❌ Geocoding Exception: {e}")
    
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
    # Use Maps API endpoint (not naveropenapi)
    url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
    }
    params = {
        "start": start,
        "goal": goal,
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Extract duration from traoptimal route
            duration_ms = data['route']['traoptimal'][0]['summary']['duration']
            duration_min = int(duration_ms / 1000 / 60)
            total_with_buffer = duration_min + TRAVEL_TIME_BUFFER
            print(f"✓ Travel time: {duration_min}분 (+ {TRAVEL_TIME_BUFFER}분 buffer = {total_with_buffer}분)")
            return total_with_buffer
        else:
            print(f"❌ Directions Error ({response.status_code})")
            print(f"   Response: {response.text}")
            
            # Helpful error messages
            if response.status_code == 401:
                print("\n⚠️  ERROR 401: Permission Denied")
                print("   Possible causes:")
                print("   1. API keys are incorrect in .env file")
                print("   2. Directions 5 API not enabled in Naver Cloud Platform")
                print("   3. Check your subscription at: https://console.ncloud.com/")
                
    except Exception as e:
        print(f"❌ Directions Exception: {e}")
    
    return 0


def get_travel_duration_from_addresses(start_address, goal_address):
    """Get travel duration between two addresses"""
    print(f"\n🗺️  Calculating: {start_address} → {goal_address}")
    
    start_coords = geocode(start_address)
    goal_coords = geocode(goal_address)
    
    if not start_coords or not goal_coords:
        print(f"❌ Failed to geocode one or both addresses")
        return 0
    
    return get_travel_duration(start_coords, goal_coords)


def validate_api_keys():
    """Validate that API keys are configured"""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("\n❌ ERROR: Naver API keys not found!")
        print("   Please create .env file with:")
        print("   NAVER_CLIENT_ID=your_client_id")
        print("   NAVER_CLIENT_SECRET=your_client_secret")
        return False
    
    if NAVER_CLIENT_ID == "your_client_id_here":
        print("\n❌ ERROR: Please replace placeholder API keys in .env")
        return False
    
    print(f"✓ API keys loaded")
    print(f"  Client ID: {NAVER_CLIENT_ID[:10]}...")
    return True


if __name__ == "__main__":
    print("="*60)
    print("Testing Naver Maps API")
    print("="*60)
    
    if not validate_api_keys():
        exit(1)
    
    # Test geocoding
    print("\n📍 Test 1: Geocoding")
    coords = geocode("강남역")
    
    if coords:
        # Test directions
        print("\n📍 Test 2: Travel Time")
        duration = get_travel_duration_from_addresses("강남역", "판교역")
        
        if duration > 0:
            print(f"\n✅ All tests passed!")
        else:
            print(f"\n⚠️  Travel time calculation failed")
    else:
        print(f"\n⚠️  Geocoding failed - check API subscription")

