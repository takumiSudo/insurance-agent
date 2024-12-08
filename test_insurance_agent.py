import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from insurance_agent import InsuranceClaimAgent
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

# Create a simple HTML file for testing
TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Insurance Claim Test Page</title>
</head>
<body>
    <form id="claim-form">
        <input type="text" id="policy-number" name="policy-number">
        <input type="text" id="claim-amount" name="claim-amount">
        <button type="submit" id="submit-btn">Submit</button>
    </form>
</body>
</html>
"""

class TestInsuranceClaimAgent:
    @pytest.fixture(autouse=True)
    def setup_method(self, tmp_path):
        # Create test HTML file
        self.test_html_path = tmp_path / "test.html"
        with open(self.test_html_path, "w") as f:
            f.write(TEST_HTML)
        
        # Initialize the agent
        self.agent = InsuranceClaimAgent()
        
        # Start local server
        self.server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        yield
        
        # Cleanup
        if self.agent.driver:
            self.agent.close_browser()
        self.server.shutdown()
        self.server.server_close()

    def test_initialize_browser(self):
        """Test browser initialization"""
        self.agent.initialize_browser()
        assert self.agent.driver is not None
        self.agent.close_browser()

    def test_validate_number(self):
        """Test number validation"""
        # Test valid numbers
        assert self.agent.validate_number("100.50", 0, 1000)
        assert self.agent.validate_number(50)
        
        # Test invalid numbers
        assert not self.agent.validate_number("abc")
        assert not self.agent.validate_number("100", 200, 300)
        assert not self.agent.validate_number("-50", 0, 100)

    def test_validate_currency_format(self):
        """Test currency format validation"""
        # Test valid formats
        assert self.agent.validate_currency_format("$1,234.56")
        assert self.agent.validate_currency_format("1234.56")
        assert self.agent.validate_currency_format("$100.00")
        
        # Test invalid formats
        assert not self.agent.validate_currency_format("abc")
        assert not self.agent.validate_currency_format("$1.234.56")
        assert not self.agent.validate_currency_format("$1000,00")

    def test_process_claim_input(self):
        """Test claim input processing"""
        # Test valid claim data
        valid_claim = {
            "claim_amount": "1,234.56",
            "policy_number": "POL123456"
        }
        assert self.agent.process_claim_input(valid_claim)
        
        # Test invalid claim data
        invalid_claim = {
            "claim_amount": "invalid_amount",
            "policy_number": "POL123456"
        }
        assert not self.agent.process_claim_input(invalid_claim)
        
        # Test missing required field
        incomplete_claim = {
            "claim_amount": "1,234.56"
        }
        assert not self.agent.process_claim_input(incomplete_claim)

    def test_ui_interactions(self):
        """Test UI interactions with a local test page"""
        self.agent.initialize_browser()
        
        # Navigate to test page
        self.agent.driver.get(f"file://{self.test_html_path}")
        
        # Test filling form fields
        assert self.agent.fill_form_field("#policy-number", "POL123456", By.CSS_SELECTOR)
        assert self.agent.fill_form_field("#claim-amount", "1234.56", By.CSS_SELECTOR)
        
        # Test clicking button
        assert self.agent.click_element("#submit-btn", By.CSS_SELECTOR)

    def test_error_handling(self):
        """Test error handling for UI interactions"""
        self.agent.initialize_browser()
        
        # Test clicking non-existent element
        assert not self.agent.click_element("#non-existent-button", By.CSS_SELECTOR, timeout=2)
        
        # Test filling non-existent form field
        assert not self.agent.fill_form_field("#non-existent-field", "test", By.CSS_SELECTOR)

if __name__ == "__main__":
    pytest.main(["-v", "test_insurance_agent.py"])
