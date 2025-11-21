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

# Load environment variables
load_dotenv()

class LMSCrawler:
    """
    LMS Crawler for Yonsei LearnUs.
    Logic synchronized with 'fetch-tasks.ts' and 'LearnUs YONSEI.html'.
    """
    
    LEARNUS_ORIGIN = "https://ys.learnus.org"
    INFRA_ORIGIN = "https://infra.yonsei.ac.kr"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.LEARNUS_ORIGIN
        })

    # ... [Login methods remain the same as previous version] ...
    def parse_input_tags(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        for input_tag in soup.find_all('input'):
            name = input_tag.get('name') or input_tag.get('id')
            value = input_tag.get('value', '')
            if name: data[name] = value
        return data

    def _rsa_encrypt(self, modulus_hex, exponent_hex, data_dict):
        modulus = int(modulus_hex, 16)
        exponent = int(exponent_hex, 16)
        public_key = RSA.construct((modulus, exponent))
        payload = json.dumps(data_dict).encode('utf-8')
        cipher = PKCS1_v1_5.new(public_key)
        return binascii.hexlify(cipher.encrypt(payload)).decode('utf-8').upper()

    def login(self):
        # ... [Insert the 5-step login flow from previous code here] ...
        # (Omitted for brevity, assume standard Moodle/Yonsei SSO flow)
        print(f"🔐 Starting SSO Login Flow for {self.username}...")
        try:
            resp1 = self.session.get(f"{self.LEARNUS_ORIGIN}/passni/sso/spLogin2.php")
            data1 = self.parse_input_tags(resp1.text)
            if not data1.get('S1'): return False

            payload2 = {'app_id': 'ednetYonsei', 'retUrl': 'https://ys.learnus.org', 'failUrl': 'https://ys.learnus.org', 'baseUrl': 'https://ys.learnus.org', 'S1': data1['S1'], 'refererUrl': 'https://ys.learnus.org'}
            resp2 = self.session.post(f"{self.INFRA_ORIGIN}/sso/PmSSOService", data=payload2)
            html2 = resp2.text
            sso_challenge = re.search(r"var ssoChallenge\s*=\s*'([^']+)'", html2)
            key_match = re.search(r"rsa\.setPublic\(\s*'([^']+)',\s*'([^']+)'", html2, re.IGNORECASE)
            if not sso_challenge or not key_match: return False

            enc_payload = {"userid": self.username, "userpw": self.password, "ssoChallenge": sso_challenge.group(1)}
            e2_hex = self._rsa_encrypt(key_match.group(1), key_match.group(2), enc_payload)
            
            payload3 = {'app_id': 'ednetYonsei', 'retUrl': 'https://ys.learnus.org', 'failUrl': 'https://ys.learnus.org', 'baseUrl': 'https://ys.learnus.org', 'loginType': 'invokeID', 'E2': e2_hex, 'refererUrl': 'https://ys.learnus.org'}
            resp3 = self.session.post(f"{self.INFRA_ORIGIN}/sso/PmSSOAuthService", data=payload3)
            data3 = self.parse_input_tags(resp3.text)
            if 'E3' not in data3: return False

            payload4 = {'app_id': 'ednetYonsei', 'retUrl': 'https://ys.learnus.org', 'failUrl': 'https://ys.learnus.org', 'baseUrl': 'https://ys.learnus.org', 'E3': data3.get('E3'), 'E4': data3.get('E4'), 'S2': data3.get('S2'), 'CLTID': data3.get('CLTID'), 'refererUrl': 'https://ys.learnus.org'}
            self.session.post(f"{self.LEARNUS_ORIGIN}/passni/sso/spLoginData.php", data=payload4)
            final_resp = self.session.get(f"{self.LEARNUS_ORIGIN}/passni/spLoginProcess.php")
            return 'logout.php' in final_resp.text or self.session.cookies.get('MoodleSession')
        except Exception as e:
            print(f"Login Error: {e}")
            return False

    def _extract_task_details(self, activity, course_name):
        """
        Extracts details if the task is incomplete.
        Logic Reference: fetch-tasks.ts
        DOM Reference: LearnUs YONSEI.html
        """
        # 1. Check Restriction (fetch-tasks.ts: :not(:has(.isrestricted)))
        if activity.select_one('.isrestricted'):
            return None
        
        # 2. Check Undone Status (fetch-tasks.ts: img[src$="completion-auto-n"])
        # We use *= to match the filename regardless of path/extension (.svg)
        incomplete_marker = activity.select_one('img[src*="completion-auto-n"]')
        if not incomplete_marker:
            return None
            
        # 3. Extract Name (Refined based on LearnUs YONSEI.html)
        instancename_tag = activity.select_one('.instancename')
        if not instancename_tag: return None
        
        # Clone to avoid modifying the original soup tree, then remove .accesshide
        # HTML Example: <span class="instancename">Homework<span class="accesshide "> Assignment</span></span>
        name_element = BeautifulSoup(str(instancename_tag), 'html.parser')
        for hidden in name_element.select('.accesshide'):
            hidden.decompose()
            
        task_name = name_element.get_text(strip=True)
        
        # 4. Extract Link
        link_tag = activity.select_one('a')
        task_link = link_tag['href'] if link_tag else ""
        
        # 5. Extract Due Date (Refined based on HTML VOD/Assignment structures)
        # VODs use .displayoptions .text-ubstrap
        # Assignments use .text-danger or .availabilityinfo
        due_date = "No deadline"
        
        date_node = activity.select_one('.text-danger') # Standard high priority
        if not date_node:
            date_node = activity.select_one('.displayoptions .text-ubstrap') # VOD specific
        if not date_node:
             date_node = activity.select_one('.activity-dates, .availabilityinfo') # Fallback
             
        if date_node: 
            due_date = date_node.get_text(strip=True).replace('~', '').strip()

        return {
            'course': course_name,
            'task': task_name,
            'link': task_link,
            'due_date': due_date,
            'status': 'Incomplete'
        }

    def fetch_tasks(self):
        if not self.username or not self.password: return []
        
        print("📥 Fetching course list from Dashboard...")
        try:
            resp = self.session.get(self.LEARNUS_ORIGIN)
            soup = BeautifulSoup(resp.text, 'html.parser')
        except Exception: return []
        
        courses = []
        # Selector matches LearnUs YONSEI.html Dashboard structure
        course_items = soup.select('.my-course-lists li')
        
        for item in course_items:
            link = item.select_one('.course-link')
            if not link: continue
            courses.append({'name': link.get_text(strip=True), 'url': link['href']})
            
        print(f"✓ Found {len(courses)} courses. Scanning course pages...")
        
        all_tasks = []
        for course in courses:
            # Skip if URL is not a view.php (dashboard links sometimes vary)
            if 'course/view.php' not in course['url']: continue

            time.sleep(0.1) # Polite delay
            try:
                course_resp = self.session.get(course['url'])
                course_soup = BeautifulSoup(course_resp.text, 'html.parser')
                
                # Logic Reference: fetch-tasks.ts (fixedTasks + weekTasks)
                search_areas = course_soup.select('.course-box-top, .total-sections')
                
                for area in search_areas:
                    activities = area.select('.activity')
                    for activity in activities:
                        task = self._extract_task_details(activity, course['name'])
                        if task:
                            all_tasks.append(task)
            except Exception: pass

        return all_tasks

# ==========================================
# Execution
# ==========================================
if __name__ == "__main__":
    USERNAME = os.getenv("YONSEI_USERNAME")
    PASSWORD = os.getenv("YONSEI_PASSWORD")

    if USERNAME and PASSWORD:
        crawler = LMSCrawler(USERNAME, PASSWORD)
        if crawler.login():
            tasks = crawler.fetch_tasks()
            print(f"\n📝 Found {len(tasks)} Undone Tasks (Auto-Completion Only)")
            for t in tasks:
                print(f"[{t['course']}] {t['task']}\n   Due: {t['due_date']}\n   Link: {t['link']}\n")