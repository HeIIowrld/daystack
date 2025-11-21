"""
Configuration module for the YCC Scheduler
Loads environment variables and provides configuration settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for API credentials and settings"""
    
    # Naver API Credentials
    NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
    NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
    LOC_CLIENT_ID = os.getenv('LOC_CLIENT_ID')
    LOC_CLIENT_SECRET = os.getenv('LOC_CLIENT_SECRET')
    
    # Travel time buffer (in minutes) - adds safety margin to travel time estimates
    TRAVEL_TIME_BUFFER = int(os.getenv('TRAVEL_TIME_BUFFER', 15))
    
    # Location aliases - Map common names to full addresses
    LOCATION_ALIASES = {
        "학교": "분당구 불정로 6",
        "집": "",  # User should fill this in
        "도서관": "",  # User should fill this in
    }
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.NAVER_CLIENT_ID or not cls.NAVER_CLIENT_SECRET:
            raise ValueError(
                "Naver API credentials not found. "
                "Please create a .env file with NAVER_CLIENT_ID and NAVER_CLIENT_SECRET"
            )
        return True
    
    @classmethod
    def resolve_location(cls, location):
        """Resolve location aliases to full addresses"""
        return cls.LOCATION_ALIASES.get(location, location)


