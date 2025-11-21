import unittest
import sys
import binascii
from unittest.mock import MagicMock, patch

# Import the crawler class from crawler.py
try:
    from crawler import LMSCrawler
except ImportError:
    print("❌ CRITICAL ERROR: Could not import 'crawler.py'.")
    print("   Make sure 'crawler.py' and 'test_lms_crawler.py' are in the same folder.")
    sys.exit(1)

class TestLMSCrawler(unittest.TestCase):

    def setUp(self):
        """Initialize crawler before each test."""
        self.crawler = LMSCrawler("test_user", "test_pass")

    def test_parse_input_tags(self):
        """Test if hidden input fields are extracted correctly."""
        print("\nRunning test_parse_input_tags...")
        html = """
        <form>
            <input type="hidden" name="S1" value="token_123">
            <input id="E3" value="encrypted_data">
            <input name="visible" value="should_be_included">
        </form>
        """
        result = self.crawler.parse_input_tags(html)
        self.assertEqual(result['S1'], 'token_123')
        self.assertEqual(result['E3'], 'encrypted_data')
        self.assertEqual(result['visible'], 'should_be_included')

    @patch('crawler.PKCS1_v1_5')
    @patch('crawler.RSA')
    def test_rsa_encrypt_format(self, mock_rsa, mock_pkcs1):
        """
        Test if RSA encryption calls the library correctly and formats as Hex.
        We mock the crypto library to avoid needing valid RSA keys.
        """
        print("Running test_rsa_encrypt_format...")
        
        # 1. Setup the Mocks
        # Mock the RSA Key object
        mock_key = MagicMock()
        mock_rsa.construct.return_value = mock_key
        
        # Mock the Cipher object
        mock_cipher = MagicMock()
        mock_pkcs1.new.return_value = mock_cipher
        
        # Configure the cipher to return a specific byte sequence when encrypt() is called
        # b'\xDE\xAD\xBE\xEF' -> Should become string "DEADBEEF"
        mock_cipher.encrypt.return_value = b'\xDE\xAD\xBE\xEF'

        # 2. Define Inputs
        modulus_hex = "A1" # Dummy hex
        exponent_hex = "03" # Dummy hex
        data = {"test": "data"}

        # 3. Run the function
        result_hex = self.crawler._rsa_encrypt(modulus_hex, exponent_hex, data)
        
        # 4. Assertions
        # Ensure RSA.construct was called with the integer values of our hex strings
        mock_rsa.construct.assert_called_with((161, 3)) # A1=161, 03=3
        
        # Ensure PKCS1_v1_5.new was initialized with the key
        mock_pkcs1.new.assert_called_with(mock_key)
        
        # Ensure the result matches the Hex Upper representation of the bytes
        self.assertEqual(result_hex, "DEADBEEF")

    @patch('requests.Session.get')
    def test_fetch_tasks_parsing(self, mock_get):
        """Test the core task parsing logic by mocking HTML responses."""
        print("Running test_fetch_tasks_parsing...")
        
        # --- Mock Response 1: Dashboard ---
        dashboard_html = """
        <ul class="my-course-lists">
            <li>
                <a class="course-link" href="https://ys.learnus.org/course/view.php?id=1001">
                    Introduction to Python
                </a>
            </li>
        </ul>
        """
        
        # --- Mock Response 2: Course Page ---
        course_html = """
        <div class="course-box-top">
            <!-- Task A: VALID INCOMPLETE TASK -->
            <div class="activity">
                <div class="instancename">Week 1 Assignment</div>
                <a href="https://ys.learnus.org/mod/assign/view.php?id=501"></a>
                <!-- The 'n' at the end means 'not completed' -->
                <img src="https://ys.learnus.org/theme/image.php/completion-auto-n" />
            </div>

            <!-- Task B: ALREADY COMPLETED (Should be ignored) -->
            <div class="activity">
                <div class="instancename">Week 1 Quiz</div>
                <a href="https://ys.learnus.org/mod/quiz/view.php?id=502"></a>
                <!-- The 'y' at the end means 'yes completed' -->
                <img src="https://ys.learnus.org/theme/image.php/completion-auto-y" />
            </div>

            <!-- Task C: RESTRICTED (Should be ignored) -->
            <div class="activity">
                <div class="instancename">Final Exam</div>
                <div class="isrestricted">Restricted: Not available unless...</div>
                <img src="https://ys.learnus.org/theme/image.php/completion-auto-n" />
            </div>
        </div>
        """

        # Configure the mock to return different content based on URL
        def side_effect(url, **kwargs):
            mock_resp = MagicMock()
            if url == self.crawler.LEARNUS_ORIGIN:
                mock_resp.text = dashboard_html
            elif "course/view.php" in url:
                mock_resp.text = course_html
            else:
                mock_resp.text = ""
            return mock_resp

        mock_get.side_effect = side_effect

        # Run the method
        tasks = self.crawler.fetch_tasks()

        # Assertions
        self.assertEqual(len(tasks), 1, "Should find exactly 1 incomplete task")
        
        task = tasks[0]
        self.assertEqual(task['course'], "Introduction to Python")
        self.assertEqual(task['task'], "Week 1 Assignment")
        self.assertEqual(task['link'], "https://ys.learnus.org/mod/assign/view.php?id=501")

if __name__ == '__main__':
    unittest.main(verbosity=2)