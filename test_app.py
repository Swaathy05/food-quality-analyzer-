import streamlit as st
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

st.title("🧪 Test App")
st.write("Testing if Streamlit works...")

# Test environment
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    st.success(f"✅ API Key loaded: {api_key[:10]}...")
else:
    st.error("❌ No API key found")

# Test Groq
try:
    from groq import Groq
    client = Groq(api_key=api_key)
    st.success("✅ Groq imported successfully")
    
    if st.button("Test AI"):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Say hello"}],
                model="llama-3.1-8b-instant",  # Updated model
                max_tokens=20
            )
            st.success(f"🎉 AI says: {response.choices[0].message.content}")
        except Exception as e:
            st.error(f"AI Error: {e}")
            
except Exception as e:
    st.error(f"❌ Groq import failed: {e}")

st.write("If you see this, Streamlit is working! 🎉")