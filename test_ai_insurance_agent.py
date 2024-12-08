import pytest
from unittest.mock import Mock, patch
from selenium.webdriver.common.by import By
from ai_insurance_agent import AIInsuranceAgent
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os
import json
import requests

# Test HTML with more complex form fields for AI analysis
TEST_HTML = """
<!DOCTYPE html>
<html>
<head><title>Insurance Claim Form</title></head>
<body>
    <form id="claim-form">
        <input type="text" id="policy-number" placeholder="Policy Number">
        <input type="date" id="incident-date" placeholder="Incident Date">
        <select id="claim-type">
            <option value="">Select Type</option>
            <option value="auto">Auto</option>
            <option value="home">Home</option>
            <option value="life">Life</option>
        </select>
        <input type="number" id="claim-amount" placeholder="Claim Amount">
        <textarea id="description" placeholder="Description"></textarea>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

# Mock OpenAI API response
MOCK_OPENAI_RESPONSE = {
    "policy-number": "POL123456",
    "incident-date": "2023-12-08",
    "claim-type": "auto",
    "claim-amount": "500",
    "description": "Minor fender bender in parking lot"
}

class MockOpenAIResponse:
    class Choice:
        class Message:
            def __init__(self, content):
                self.content = content

        def __init__(self, content):
            self.message = self.Message(json.dumps(content))

    def __init__(self, content):
        self.choices = [self.Choice(content)]

class TestAIInsuranceAgent:
    """Test suite for AIInsuranceAgent class."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, tmp_path):
        # Create test HTML file
        self.test_html_path = tmp_path / "test.html"
        with open(self.test_html_path, "w") as f:
            f.write(TEST_HTML)
        
        # Mock OpenAI client
        self.mock_openai = Mock()
        self.mock_openai.chat.completions.create.return_value = MockOpenAIResponse(MOCK_OPENAI_RESPONSE)
        
        # Initialize agent with mock OpenAI client
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            self.agent = AIInsuranceAgent()
            self.agent.client = self.mock_openai
        
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

    def test_initialization(self):
        """Test AI agent initialization"""
        assert isinstance(self.agent, AIInsuranceAgent)
        
        # Test initialization without API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with pytest.raises(ValueError):
                AIInsuranceAgent()

    def test_get_page_content(self):
        """Test page content extraction"""
        self.agent.initialize_browser()
        self.agent.driver.get(f"file://{self.test_html_path}")
        
        content = self.agent.get_page_content()
        assert "Insurance Claim Form" in content
        assert "Policy Number" in content
        assert "Submit" in content

    def test_analyze_page(self):
        """Test AI page analysis"""
        self.agent.initialize_browser()
        self.agent.driver.get(f"file://{self.test_html_path}")
        
        analysis = self.agent.analyze_page()
        assert analysis == MOCK_OPENAI_RESPONSE
        
        # Verify OpenAI was called with correct prompt
        call_args = self.mock_openai.chat.completions.create.call_args[1]
        assert "Task:" in call_args["messages"][1]["content"]
        assert "Insurance Claim Form" in call_args["messages"][1]["content"]

    def test_execute_task(self):
        """Test task execution based on AI analysis"""
        self.agent.initialize_browser()
        self.agent.driver.get(f"file://{self.test_html_path}")
        
        # Test successful execution
        success = self.agent.execute_task("Fill out an auto insurance claim")
        assert success
        
        # Verify field values
        for field_id, expected_value in MOCK_OPENAI_RESPONSE.items():
            element = self.agent.driver.find_element(By.CSS_SELECTOR, f"#{field_id}")
            if element.tag_name == "select":
                assert element.get_attribute("value") == expected_value
            else:
                assert element.get_attribute("value") == expected_value

    def test_error_handling(self):
        """Test error handling for network and field errors"""
        self.agent.initialize_browser()
        self.agent.driver.get(f"file://{self.test_html_path}")
        
        # Test network error handling
        self.mock_openai.chat.completions.create.side_effect = requests.exceptions.RequestException()
        success = self.agent.execute_task("Fill out a claim")
        assert not success
        
        # Test invalid field handling
        self.mock_openai.chat.completions.create.side_effect = None
        self.mock_openai.chat.completions.create.return_value = MockOpenAIResponse({
            "nonexistent-field": "test"
        })
        success = self.agent.execute_task("Fill out a claim")
        assert not success

    def test_process_claim_with_ai(self):
        """Test end-to-end claim processing with AI"""
        success = self.agent.process_claim_with_ai(
            url=f"file://{self.test_html_path}",
            task_description="Process an auto insurance claim for a fender bender"
        )
        assert success

    @patch('openai.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test handling of OpenAI API errors"""
        # Mock API error
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        # Replace agent's OpenAI client with mocked version
        self.agent.client = mock_openai.return_value
        
        self.agent.initialize_browser()
        self.agent.driver.get(f"file://{self.test_html_path}")
        
        success = self.agent.execute_task("Process a claim")
        assert not success

if __name__ == "__main__":
    pytest.main(["-v", "test_ai_insurance_agent.py"])
