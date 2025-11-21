import re
import os
from bs4 import BeautifulSoup

# ==========================================
# 1. The Core Logic (Same as your Crawler)
# ==========================================
def extract_task_details(activity, course_name="Test Course"):
    """
    Parses a single activity element (BeautifulSoup object).
    Returns dict if it's an incomplete task, else None.
    """
    # A. Filter: Skip if restricted
    if activity.select_one('.isrestricted'):
        return None
    
    # B. Filter: Check for Incomplete Status
    # Looking for images that indicate "Not Completed" (auto or manual)
    incomplete_marker = activity.select_one('img[src*="completion-auto-n"], img[src*="completion-manual-n"]')
    
    if not incomplete_marker:
        return None
        
    # C. Extract Data
    instancename = activity.select_one('.instancename')
    if not instancename:
        return None
        
    # Clean text
    raw_name = instancename.get_text(strip=True)
    task_name = re.sub(r'\s*(File|Assignment|Quiz|Url|Page|비공개|Hidden)\s*$', '', raw_name, flags=re.IGNORECASE)
    
    # Get Link
    link_tag = activity.select_one('a')
    task_link = link_tag['href'] if link_tag else "No Link"
    
    # Get Due Date (Simple attempt)
    due_date = "No deadline"
    # Yonsei/Moodle often puts dates in .text-danger or specific date containers
    date_node = activity.select_one('.text-danger, .activity-dates, .availabilityinfo') 
    if date_node:
        due_date = date_node.get_text(strip=True)

    return {
        'course': course_name,
        'task': task_name,
        'link': task_link,
        'due_date': due_date,
        'status': 'Incomplete'
    }

def parse_html_content(html_content, source_name="Raw HTML"):
    """
    Simulates the loop over a course page.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # We look in the main course areas
    search_areas = soup.select('.course-box-top, .total-sections, .course-content')
    
    found_tasks = []
    
    print(f"\n🔍 Scanning: {source_name}")
    print(f"   Found {len(search_areas)} main content sections.")
    
    for area in search_areas:
        activities = area.select('.activity')
        print(f"   Found {len(activities)} total activities in section.")
        
        for activity in activities:
            task = extract_task_details(activity, course_name=source_name)
            if task:
                found_tasks.append(task)
                
    return found_tasks

# ==========================================
# 2. Mock Data for Verification
# ==========================================
MOCK_HTML = """
<div class="total-sections">
    <!-- Case 1: Incomplete Auto-detect Task -->
    <div class="activity modtype_assign">
        <div class="activity-instance d-flex flex-column">
            <a href="https://ys.learnus.org/mod/assign/view.php?id=12345">
                <span class="instancename">Midterm Project Assignment<span class="accesshide"> Assignment</span></span>
            </a>
        </div>
        <div class="actions">
            <!-- The magic image that indicates incomplete -->
            <img src="https://ys.learnus.org/theme/image.php/coursemosv2/core/1700000/i/completion-auto-n" alt="Not completed">
        </div>
        <div class="activity-dates">Due: 2025-12-25 23:59</div>
    </div>

    <!-- Case 2: Completed Task (Should be ignored) -->
    <div class="activity modtype_quiz">
        <a href="#"><span class="instancename">Week 1 Quiz</span></a>
        <img src="https://ys.learnus.org/theme/image.php/coursemosv2/core/1700000/i/completion-auto-y" alt="Completed">
    </div>

    <!-- Case 3: Restricted Task (Should be ignored) -->
    <div class="activity modtype_assign">
        <span class="instancename">Final Exam</span>
        <div class="isrestricted">Restricted Not available unless: ...</div>
        <img src="https://ys.learnus.org/theme/image.php/coursemosv2/core/1700000/i/completion-auto-n">
    </div>
    
    <!-- Case 4: Manual Completion (Should be caught) -->
    <div class="activity modtype_resource">
         <a href="#"><span class="instancename">Lecture Notes PDF File</span></a>
         <img src="https://ys.learnus.org/theme/image.php/coursemosv2/core/1700000/i/completion-manual-n" alt="Mark as done">
    </div>
</div>
"""

# ==========================================
# 3. Test Runner
# ==========================================
if __name__ == "__main__":
    print("="*60)
    print(" LMS PARSER DIAGNOSTIC TOOL")
    print("="*60)
    
    # --- TEST 1: MOCK DATA ---
    print("\n--- Test 1: Mock HTML Data ---")
    mock_results = parse_html_content(MOCK_HTML, "Mock Course")
    
    if len(mock_results) == 2:
        print("✅ SUCCESS: Found exactly 2 incomplete tasks (1 Auto, 1 Manual).")
        for t in mock_results:
            print(f"   - [Found] {t['task']} (Due: {t['due_date']})")
    else:
        print(f"❌ FAILURE: Expected 2 tasks, found {len(mock_results)}.")

    # --- TEST 2: LOCAL FILE ---
    # Instructions: Save your browser page as 'yonsei_page.html' in this folder
    filename = "yonsei_page.html"
    
    if os.path.exists(filename):
        print(f"\n--- Test 2: Real File ({filename}) ---")
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
            real_results = parse_html_content(html, "Real Page Data")
            
            if not real_results:
                print("⚠️  No incomplete tasks found in file.")
                print("    (Check: Are you logged in? Is the file saved correctly?)")
            else:
                print(f"\n🎉 Found {len(real_results)} tasks in your file:")
                for i, t in enumerate(real_results, 1):
                    print(f"{i}. {t['task']}")
                    print(f"   Link: {t['link']}")
                    print(f"   Due:  {t['due_date']}")
                    print("-" * 40)
    else:
        print(f"\nℹ️  Skipping Test 2: '{filename}' not found.")
        print("   To test real data, save your Yonsei LearnUs course page (CTRL+S)")
        print(f"   as '{filename}' in this folder and run again.")