import os
import json
from openai import OpenAI

def is_openai_available():
    """
    Check if OpenAI API is available and configured properly.
    
    Returns:
        bool: True if OpenAI API is available, False otherwise
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        return False
    
    # Force OpenAI integration enabled in environment
    os.environ['ENABLE_OPENAI'] = 'true'
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test API connection with minimal token usage
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the cheapest model for testing
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1  # Minimize token usage
        )
        
        # If we get a response without error, the API is available
        print("OpenAI API is available and working correctly")
        return True
    except Exception as e:
        # Check for quota error specifically
        error_str = str(e)
        if 'insufficient_quota' in error_str:
            print("OpenAI API Error: Quota exceeded. Please check billing settings.")
            
            # Save error info for UI display
            error_info = {
                "error_type": "quota_exceeded",
                "message": "You exceeded your current quota, please check your plan and billing details."
            }
            with open('openai_error_info.json', 'w') as f:
                json.dump(error_info, f)
        else:
            print(f"OpenAI API Error: {e}")
            
            # Save general error info
            error_info = {
                "error_type": "general_error",
                "message": str(e)
            }
            with open('openai_error_info.json', 'w') as f:
                json.dump(error_info, f)
        
        return False

if __name__ == "__main__":
    # Test if OpenAI is available
    if is_openai_available():
        print("OpenAI API is available and working correctly.")
    else:
        print("OpenAI API is not available or has quota/billing issues.")