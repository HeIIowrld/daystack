import requests
from bs4 import BeautifulSoup
import json
import re
import time
import binascii
import os
from dotenv import load_dotenv
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# Load environment variables from .env file
load_dotenv()

class LMSCrawler:
    """
    LMS Crawler based on yontil-main logic (Yonsei LearnUs).
    Key Features ported from TypeScript:
    1. 5-Step SSO Login Flow (login-learnus.ts)
    2. RSA Encryption for credentials
    3. Moodle 'Completion' status checking (fetch-tasks.ts)
    """
    
    LEARNUS_ORIGIN = "https://ys.learnus.org"
    INFRA_ORIGIN = "https://infra.yonsei.ac.kr"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        
        # Mimic Chrome headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.LEARNUS_ORIGIN
        })

    def parse_input_tags(self, html):
        """Extract hidden input fields from a form response."""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        for input_tag in soup.find_all('input'):
            name = input_tag.get('name') or input_tag.get('id')
            value = input_tag.get('value', '')
            if name:
                data[name] = value
        return data

    def _rsa_encrypt(self, modulus_hex, exponent_hex, data_dict):
        """
        Port of node-forge RSA encryption from login-learnus.ts
        Constructs public key from hex modulus/exponent and encrypts JSON payload.
        """
        # 1. Construct Public Key
        modulus = int(modulus_hex, 16)
        exponent = int(exponent_hex, 16)
        public_key = RSA.construct((modulus, exponent))
        
        # 2. Prepare Payload (JSON string)
        payload = json.dumps(data_dict).encode('utf-8')
        
        # 3. Encrypt using PKCS1_v1_5
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_bytes = cipher.encrypt(payload)
        
        # 4. Return as Hex string (UpperCase)
        return binascii.hexlify(encrypted_bytes).decode('utf-8').upper()

    def login(self):
        """
        Implements the 5-step login flow defined in login-learnus.ts
        """
        print(f"🔐 Starting SSO Login Flow for {self.username}...")

        try:
            # --- Step 1: Initial Handshake ---
            # Endpoint: /passni/sso/spLogin2.php
            resp1 = self.session.get(f"{self.LEARNUS_ORIGIN}/passni/sso/spLogin2.php")
            data1 = self.parse_input_tags(resp1.text)
            
            if not data1.get('S1'):
                print("✗ Failed Step 1: No S1 token found.")
                return False

            # --- Step 2: Get Encryption Keys & Challenge ---
            # Endpoint: INFRA_ORIGIN/sso/PmSSOService
            payload2 = {
                'app_id': 'ednetYonsei',
                'retUrl': 'https://ys.learnus.org',
                'failUrl': 'https://ys.learnus.org',
                'baseUrl': 'https://ys.learnus.org',
                'S1': data1['S1'],
                'refererUrl': 'https://ys.learnus.org'
            }
            resp2 = self.session.post(f"{self.INFRA_ORIGIN}/sso/PmSSOService", data=payload2)
            
            # Regex extract keys (logic from login-learnus.ts: fetch2)
            html2 = resp2.text
            sso_challenge = re.search(r"var ssoChallenge\s*=\s*'([^']+)'", html2)
            key_match = re.search(r"rsa\.setPublic\(\s*'([^']+)',\s*'([^']+)'", html2, re.IGNORECASE)

            if not sso_challenge or not key_match:
                print("✗ Failed Step 2: Could not extract RSA keys or Challenge.")
                return False

            sso_challenge = sso_challenge.group(1)
            key_modulus = key_match.group(1)
            key_exponent = key_match.group(2)

            # --- Step 3: RSA Authentication ---
            # Endpoint: INFRA_ORIGIN/sso/PmSSOAuthService
            # Logic: Encrypt {userid, userpw, ssoChallenge} -> E2
            
            enc_payload = {
                "userid": self.username,
                "userpw": self.password,
                "ssoChallenge": sso_challenge
            }
            
            e2_hex = self._rsa_encrypt(key_modulus, key_exponent, enc_payload)
            
            payload3 = {
                'app_id': 'ednetYonsei',
                'retUrl': 'https://ys.learnus.org',
                'failUrl': 'https://ys.learnus.org',
                'baseUrl': 'https://ys.learnus.org',
                'loginType': 'invokeID',
                'E2': e2_hex,
                'refererUrl': 'https://ys.learnus.org'
            }
            
            resp3 = self.session.post(f"{self.INFRA_ORIGIN}/sso/PmSSOAuthService", data=payload3)
            data3 = self.parse_input_tags(resp3.text)
            
            if 'E3' not in data3:
                print("✗ Failed Step 3: Authentication rejected (Wrong password?).")
                return False

            # --- Step 4: Validate with LearnUs ---
            # Endpoint: /passni/sso/spLoginData.php
            payload4 = {
                'app_id': 'ednetYonsei',
                'retUrl': 'https://ys.learnus.org',
                'failUrl': 'https://ys.learnus.org',
                'baseUrl': 'https://ys.learnus.org',
                'E3': data3.get('E3'),
                'E4': data3.get('E4'),
                'S2': data3.get('S2'),
                'CLTID': data3.get('CLTID'),
                'refererUrl': 'https://ys.learnus.org'
            }
            self.session.post(f"{self.LEARNUS_ORIGIN}/passni/sso/spLoginData.php", data=payload4)

            # --- Step 5: Finalize Session ---
            # Endpoint: /passni/spLoginProcess.php
            final_resp = self.session.get(f"{self.LEARNUS_ORIGIN}/passni/spLoginProcess.php")
            
            if 'logout.php' in final_resp.text or self.session.cookies.get('MoodleSession'):
                print("✓ Login Successful")
                return True
            else:
                print("✗ Login Finalization Failed")
                return False

        except Exception as e:
            print(f"⚠ Exception during login: {e}")
            return False

    def fetch_tasks(self):
        """
        Fetches tasks using patterns from fetch-tasks.ts
        Specifically looks for 'completion-auto-n' images which indicate incomplete status.
        """
        print("📥 Fetching course list...")
        
        # 1. Get Dashboard/Course List
        # Note: yontil code grabs from .my-course-lists on the main page or dashboard
        resp = self.session.get(self.LEARNUS_ORIGIN)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        courses = []
        course_items = soup.select('.my-course-lists li')
        
        if not course_items:
            # Fallback: Try standard Moodle dashboard if custom theme selector fails
            course_items = soup.select('.course-list-item') 

        for item in course_items:
            link = item.select_one('.course-link, a')
            if not link: continue
            
            course_name = link.get_text(strip=True)
            course_url = link['href']
            
            # Filter out non-course links if necessary
            if 'course/view.php' not in course_url:
                continue
                
            courses.append({
                'name': course_name,
                'url': course_url
            })
            
        print(f"✓ Found {len(courses)} courses. Scanning for assignments...")
        
        all_tasks = []
        
        # 2. Scan each course for incomplete tasks
        for course in courses:
            # print(f"  - Scanning {course['name']}...")
            course_resp = self.session.get(course['url'])
            course_soup = BeautifulSoup(course_resp.text, 'html.parser')
            
            # Selectors from fetch-tasks.ts:
            # .course-box-top .activity:has(img[src$="completion-auto-n"]):not(:has(.isrestricted))
            # .total-sections .activity:has(img[src$="completion-auto-n"]):not(:has(.isrestricted))
            
            # BeautifulSoup doesn't fully support complex :has css selectors natively in find_all without soupsieve (which is usually included),
            # but explicit iterating is safer and more robust in pure python.
            
            activities = course_soup.select('.activity')
            
            for activity in activities:
                # Filter 1: Check if restricted
                if activity.select_one('.isrestricted'):
                    continue
                    
                # Filter 2: Check for "Incomplete" image marker
                # yontil looks for img src ending in "completion-auto-n"
                completion_img = activity.select_one('img[src$="completion-auto-n"]')
                
                if completion_img:
                    # Extract Task Info
                    instancename = activity.select_one('.instancename')
                    if not instancename: continue
                    
                    task_name = instancename.get_text(strip=True)
                    # Remove " hidden" text usually found in instancename spans
                    task_name = task_name.replace(" Hidden", "").replace(" 비공개", "")
                    
                    task_link_tag = activity.select_one('a')
                    task_link = task_link_tag['href'] if task_link_tag else "#"
                    
                    all_tasks.append({
                        'course': course['name'],
                        'task': task_name,
                        'link': task_link,
                        'type': 'Assignment/Quiz' # You could distinguish based on class names (modtype_assign, etc)
                    })

        return all_tasks

# Usage Example
if __name__ == "__main__":
    USERNAME = os.getenv("YONSEI_USERNAME")
    PASSWORD = os.getenv("YONSEI_PASSWORD")

    if not USERNAME or not PASSWORD:
        print("❌ Error: Credentials not found. Please create a .env file with YONSEI_USERNAME and YONSEI_PASSWORD.")
        exit(1)
    
    crawler = LMSCrawler(USERNAME, PASSWORD)
    
    if crawler.login():
        tasks = crawler.fetch_tasks()
        print("\n📝 Incomplete Tasks Found:")
        for t in tasks:
            print(f"[{t['course']}] {t['task']}")
            print(f"   Link: {t['link']}")
            print("-" * 30)
    else:
        print("Login failed.")