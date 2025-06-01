import os
from openai import OpenAI

# Get API key from environment
api_key = os.environ.get('OPENAI_API_KEY')

try:
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Test API connection
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello, testing API connection"}]
    )
    
    print("Test successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")