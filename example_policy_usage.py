import os
from dotenv import load_dotenv
from ai_insurance_agent import AIInsuranceAgent
from policy.policy_types import Action

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize agent with policy
    agent = AIInsuranceAgent(
        api_key=os.getenv("OPENAI_API_KEY"),
        policy_file="policies/insurance_agent_policy.json"
    )
    
    try:
        # Initialize browser
        agent.initialize_browser()
        
        # Try to access a page (this should be allowed)
        agent.driver.get("http://localhost:8000/claim-form")
        
        print("\n=== Testing Allowed Actions ===")
        
        # Test reading page content (should be allowed)
        try:
            content = agent.get_page_content()
            print("✅ Successfully read page content")
        except PermissionError as e:
            print(f"❌ Failed to read page content: {e}")
            
        # Test filling allowed form field (should be allowed)
        try:
            agent.fill_form_field("policy-number", "POL123456")
            print("✅ Successfully filled policy number")
        except PermissionError as e:
            print(f"❌ Failed to fill policy number: {e}")
            
        print("\n=== Testing Denied Actions ===")
            
        # Try to fill sensitive data (should be denied)
        try:
            agent.fill_form_field("credit-card", "1234-5678-9012-3456")
            print("❌ Unexpectedly allowed to fill credit card")
        except PermissionError as e:
            print("✅ Correctly denied credit card input")
            
        # Try to access unauthorized domain
        agent.driver.get("http://localhost:8001/claim-form")
        try:
            content = agent.get_page_content()
            print("❌ Unexpectedly allowed to read unauthorized domain")
        except PermissionError as e:
            print("✅ Correctly denied access to unauthorized domain")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        if agent.driver:
            agent.driver.quit()

if __name__ == "__main__":
    main()
