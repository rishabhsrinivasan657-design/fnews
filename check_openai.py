import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

def test_api():
    # Load .env file (with override=True to prioritize .env values)
    project_root = Path(__file__).parent
    load_dotenv(project_root / ".env", override=True)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-..."):
        print("❌ OPENAI_API_KEY is not configured in your .env file.")
        print("   Please add a working OpenAI API key to the .env file.")
        return
        
    print(f"🔑 OPENAI_API_KEY found in .env (starts with {api_key[:6]}...). Testing connection...")
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Respond with 'Hello World'"}],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip()
        print(f"✅ Connection successful! Response: '{result}'")
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")

if __name__ == "__main__":
    test_api()
