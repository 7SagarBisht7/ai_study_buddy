from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {api_key is not None}")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # Test a simple generation
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say hello in 5 words or less'
        )
        print(f"\n✅ Test successful!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")