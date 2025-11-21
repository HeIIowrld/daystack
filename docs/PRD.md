1. 프로젝트 개요
목표: Coursemos LMS 과제 자동 크롤링 + 네이버 지도 API 기반 이동 시간 계산을 통한 일정 자동 최적화

핵심 기술: Python (Backend/Crawler), Naver Maps API (Directions, Geocoding)

2. 시스템 아키텍처 (Naver Maps 중심)
코드 스니펫

graph TD
    A[사용자/DB] -->|1. 출발지 & 도착지 주소| B(Naver Geocoding API)
    B -->|2. 위도/경도 변환 (x, y)| C(Naver Directions 5 API)
    C -->|3. 이동 경로 및 소요 시간(ms) 반환| D{스케줄러 로직}
    E[Coursemos 크롤러] -->|과제 및 소요시간 데이터| D
    D -->|이동시간 제외 후 가용 시간 계산| F[최적화된 시간표 생성]
3. 사전 준비 사항 (Naver Cloud Platform)
네이버 지도를 개발에 사용하기 위해서는 Naver Cloud Platform (NCP) 콘솔에서 애플리케이션을 등록해야 합니다.

Naver Cloud Platform 회원가입 및 결제수단 등록 (무료 사용량 범위 내 차감)

AI·NAVER API > Application 등록

필요한 API 선택:

Maps (Web Dynamic Map): 지도 표시용

Geocoding: 주소 -> 좌표 변환용

Directions 5: 자동차 기준 길찾기 (이동 시간 산출용)

(참고: 네이버는 대중교통 길찾기 Open API를 일반에게 공개하지 않으므로, 도보/자동차 기준으로 계산하거나 ODsay 등 제3자 API를 병행해야 할 수 있음)

인증키 확인: Client ID와 Client Secret 발급

4. Python 구현 가이드
4.1. 필수 라이브러리 설치
Bash

pip install requests
4.2. 모듈 1: 주소를 좌표로 변환 (Geocoding)
일정표에 "강남역", "서울대학교"처럼 텍스트로 적힌 장소를 API가 이해할 수 있는 좌표로 바꿔야 합니다.

Python

import requests
import json

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"

def get_location_coords(address):
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['addresses']:
            # x: 경도(longitude), y: 위도(latitude)
            x = data['addresses'][0]['x']
            y = data['addresses'][0]['y']
            return f"{x},{y}"
        else:
            return None
    else:
        print("Error:", response.status_code)
        return None

# 테스트
# print(get_location_coords("분당구 불정로 6"))
4.3. 모듈 2: 이동 시간 계산 (Directions 5)
두 좌표 사이의 실제 이동 시간을 가져옵니다.

Python

def get_travel_time(start_coords, end_coords):
    # start, goal 파라미터는 "경도,위도" 순서
    url = f"https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving?start={start_coords}&goal={end_coords}&option=trafast"
    
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            # 밀리초(ms) 단위로 반환되므로 분(minute)으로 변환
            duration_ms = data['route']['trafast'][0]['summary']['duration']
            duration_min = duration_ms / 1000 / 60
            return int(duration_min)
        except (KeyError, IndexError):
            return 0
    else:
        print("Error:", response.status_code)
        return 0

# 사용 예시
# start = get_location_coords("강남역")
# end = get_location_coords("판교역")
# time = get_travel_time(start, end)
# print(f"예상 소요 시간: {time}분")
5. 알고리즘 로직: 일정 재배치 (Auto-Rescheduling)
이동 시간을 고려하여 실제로 과제를 할 수 있는 시간이 얼마나 남았는지 계산하는 핵심 로직입니다.

5.1. 데이터 구조 예시
Python

current_schedule = [
    {"name": "수업 A", "end_time": "13:00", "location": "학교"},
    {"name": "아르바이트", "start_time": "15:00", "location": "강남역"}
]

todo_list = [
    {"task": "온라인 강의 듣기", "estimated_time": 40}, # 40분 소요
    {"task": "보고서 작성", "estimated_time": 90}       # 90분 소요
]
5.2. 재배치 계산 로직 (Pseudocode)
Python

def calculate_free_time(schedule_item_1, schedule_item_2):
    # 1. 두 장소 간 이동 시간 계산
    loc1 = get_location_coords(schedule_item_1['location'])
    loc2 = get_location_coords(schedule_item_2['location'])
    travel_time = get_travel_time(loc1, loc2)
    
    # 2. 시간 차이 계산 (분 단위)
    # (실제 구현 시 datetime 모듈 사용 필수)
    gap_total = (schedule_item_2['start_time'] - schedule_item_1['end_time']).minutes
    
    # 3. 순수 가용 시간 도출
    real_free_time = gap_total - travel_time
    
    return real_free_time

# 메인 실행 흐름
free_time = calculate_free_time(current_schedule[0], current_schedule[1])
print(f"이동 시간 제외하고 남는 시간: {free_time}분")

if free_time >= todo_list[0]['estimated_time']:
    print(f"'{todo_list[0]['task']}'을(를) 이 시간에 할당합니다!")
else:
    print("시간이 부족하여 할 일을 배치할 수 없습니다.")
6. 추가 고려사항 (Tip)
오차 범위 설정: 네이버 지도 API가 주는 시간은 '예상' 시간이므로, 실제 스케줄링할 때는 **+10~15분의 버퍼(여유 시간)**를 두도록 코딩하세요.

주소 정제: 사용자가 "학교"라고만 입력하면 API가 못 찾습니다. DB에 미리 {"학교": "서울시 관악구 관악로 1"} 처럼 자주 가는 곳의 정확한 주소를 매핑해두어야 합니다.

비용: 네이버 지도 API는 월별 무료 사용량이 넉넉한 편(Directions 5 기준 월 300만 건 무료 등, 정책 확인 필요)이나, 크레딧 등록이 필요하므로 확인이 필요합니다.