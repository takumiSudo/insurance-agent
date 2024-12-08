from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.select import Select
from typing import Union, Dict, Any
import re
import logging

class InsuranceClaimAgent:
    def __init__(self):
        """Initialize the Insurance Claim Agent with basic configuration."""
        self.driver = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('InsuranceClaimAgent')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def initialize_browser(self):
        """Initialize the web browser for UI interactions."""
        try:
            self.driver = webdriver.Chrome()
            self.driver.implicitly_wait(10)
            self.logger.info("Browser initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    def close_browser(self):
        """Close the browser session."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser session closed")

    def click_element(self, selector: str, by: "By" = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        """
        Click an element on the page.
        
        Args:
            selector: The selector to find the element
            by: The method to locate the element (default: CSS_SELECTOR)
            timeout: Maximum time to wait for element
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        try:
            # Use WebDriverWait to wait for the element to be clickable
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            self.logger.info(f"Successfully clicked element with {by}: {selector}")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Failed to click element with {by}: {selector}. Error: {e}")
            return False

    def validate_number(self, value: Union[str, float], 
                       min_value: float = None, 
                       max_value: float = None) -> bool:
        """
        Validate if a number is within specified range and is a valid number.
        
        Args:
            value: The value to validate
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            num_value = float(value)
            
            if min_value is not None and num_value < min_value:
                self.logger.warning(f"Value {num_value} is below minimum {min_value}")
                return False
                
            if max_value is not None and num_value > max_value:
                self.logger.warning(f"Value {num_value} is above maximum {max_value}")
                return False
                
            return True
        except ValueError:
            self.logger.error(f"Invalid number format: {value}")
            return False

    def validate_currency_format(self, value: str) -> bool:
        """
        Validate if a string is in proper currency format.
        
        Args:
            value: The string to validate
            
        Returns:
            bool: True if valid currency format, False otherwise
        """
        # Regular expression for common currency formats (e.g., $1,234.56 or 1234.56)
        currency_pattern = r'^\$?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?$'
        is_valid = bool(re.match(currency_pattern, value.strip()))
        
        if not is_valid:
            self.logger.warning(f"Invalid currency format: {value}")
        
        return is_valid

    def fill_form_field(self, field_id: str, value: str) -> bool:
        """
        Fill a form field with the given value.
        
        Args:
            field_id: The ID of the form field (without #)
            value: The value to fill in
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, f"#{field_id}")
            
            # Handle different input types
            tag_name = element.tag_name.lower()
            input_type = element.get_attribute("type") if tag_name == "input" else None
            
            if tag_name == "select":
                select = Select(element)
                select.select_by_value(value)
            elif input_type == "date":
                # Clear any existing value
                element.clear()
                # Use JavaScript to set the value directly
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]",
                    element,
                    value
                )
            else:
                element.clear()
                element.send_keys(value)
                
            self.logger.info(f"Successfully filled field #{field_id} with value {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling form field #{field_id}: {str(e)}")
            return False

    def process_claim_input(self, claim_data: Dict[str, Any]) -> bool:
        """
        Process an insurance claim input from user.
        
        Args:
            claim_data: Dictionary containing claim information
            
        Returns:
            bool: True if claim was processed successfully, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ['claim_amount', 'policy_number']
            for field in required_fields:
                if field not in claim_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate claim amount
            if not self.validate_currency_format(str(claim_data['claim_amount'])):
                return False

            # Log successful validation
            self.logger.info("Claim input validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing claim input: {str(e)}")
            return False
