"""Configuration for daystack"""
import os
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
LOC_CLIENT_ID = os.getenv('LOC_CLIENT_IDs')
LOC_CLIENT_SECRET = os.getenv('LOC_CLIENT_SECRET')
TRAVEL_TIME_BUFFER = int(os.getenv('TRAVEL_TIME_BUFFER', 15))


# LearnUs LMS credentials
YONSEI_USERNAME = os.getenv('YONSEI_USERNAME')
YONSEI_PASSWORD = os.getenv('YONSEI_PASSWORD')

