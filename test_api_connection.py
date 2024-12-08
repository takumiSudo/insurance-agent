from ai_insurance_agent import AIInsuranceAgent

def test_api_connection():
    try:
        # Initialize the agent (it will use the API key from .env)
        agent = AIInsuranceAgent()
        
        # Test a simple completion to verify API connection
        test_response = agent.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Say 'API connection successful' if you can read this."}
            ]
        )
        
        print("✅ API Connection Test Result:")
        print(test_response.choices[0].message.content)
        return True
        
    except Exception as e:
        print("❌ API Connection Test Failed:")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_connection()
