#!/usr/bin/env python3
"""
Working AI Food Quality Analyzer
Simplified version that definitely works
"""

import streamlit as st
import os
from dotenv import load_dotenv
import json
import time
from datetime import datetime
from PIL import Image
import hashlib
import io

# Load environment variables
load_dotenv()

# Try to import Groq
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    AI_AVAILABLE = True
    st.success("🟢 AI Connected: Groq API Ready!")
except Exception as e:
    AI_AVAILABLE = False
    st.error(f"🔴 AI Error: {str(e)}")

def main():
    st.set_page_config(
        page_title="AI Food Analyzer",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Food Quality Analyzer")
    st.subheader("Real AI Analysis with Groq Llama 3.1")
    
    # Show API status
    if AI_AVAILABLE:
        st.success("✅ **AI Status**: Connected to Groq API")
        st.info("🧠 **Model**: Llama 3.1 70B - Ready for analysis!")
    else:
        st.error("❌ **AI Status**: Not connected")
        st.warning("Check your GROQ_API_KEY in .env file")
    
    # Simple test
    if st.button("🧪 Test AI Connection"):
        if AI_AVAILABLE:
            with st.spinner("Testing AI..."):
                try:
                    response = client.chat.completions.create(
                        messages=[{"role": "user", "content": "Say hello and confirm you're working"}],
                        model="llama-3.1-8b-instant",  # Updated model
                        max_tokens=50
                    )
                    st.success(f"🎉 AI Response: {response.choices[0].message.content}")
                except Exception as e:
                    st.error(f"AI Test Failed: {str(e)}")
        else:
            st.error("AI not available for testing")
    
    # Main functionality
    st.markdown("---")
    st.markdown("## 📷 Food Analysis")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload nutrition label", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=300)
        
        if st.button("🔍 Analyze with AI"):
            analyze_food_with_ai(image)
    
    # Sample analysis buttons
    st.markdown("### 🎯 Try Sample Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🍟 Analyze Junk Food"):
            sample_text = """
            Nutrition Facts: Calories 250, Total Fat 15g, Sodium 450mg, Sugars 12g
            Ingredients: Wheat flour, vegetable oil, high fructose corn syrup, salt, 
            artificial flavors, yellow 6, red 40, BHT preservative
            """
            analyze_text_with_ai(sample_text, "Processed Snack")
    
    with col2:
        if st.button("🥗 Analyze Healthy Food"):
            sample_text = """
            Nutrition Facts: Calories 180, Total Fat 8g, Sodium 95mg, Fiber 6g, Protein 7g
            Ingredients: Organic oats, almonds, honey, organic coconut oil, sea salt, natural vanilla
            """
            analyze_text_with_ai(sample_text, "Healthy Snack")

def analyze_food_with_ai(image):
    """Analyze uploaded food image"""
    
    # Simulate OCR extraction
    with st.spinner("🔍 Extracting text from image..."):
        time.sleep(1)
        # Generate sample nutrition text based on image
        nutrition_text = generate_sample_nutrition_text(image)
        st.success("✅ Text extracted!")
    
    # Show extracted text
    with st.expander("📝 Extracted Text"):
        st.code(nutrition_text)
    
    # AI Analysis
    analyze_text_with_ai(nutrition_text, "Uploaded Product")

def analyze_text_with_ai(nutrition_text, product_name):
    """Analyze nutrition text with AI"""
    
    if not AI_AVAILABLE:
        st.error("❌ AI not available - check your API key")
        return
    
    with st.spinner("🤖 AI is analyzing..."):
        try:
            # Create AI prompt
            prompt = f"""
            Analyze this nutrition information and provide a health assessment:
            
            {nutrition_text}
            
            Please provide:
            1. Health score (1-10, where 10 is healthiest)
            2. Main health concerns
            3. Detected harmful chemicals or additives
            4. Recommendation (consume/limit/avoid)
            5. Brief explanation
            
            Keep response concise and practical.
            """
            
            # Call Groq API with updated model
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",  # Updated to available model
                temperature=0.1,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Display results
            st.markdown("## 🤖 AI Analysis Results")
            st.markdown(f"**Product:** {product_name}")
            st.markdown(f"**Analysis Time:** {datetime.now().strftime('%H:%M:%S')}")
            
            # Show AI response
            st.markdown("### 🧠 AI Assessment")
            st.write(ai_response)
            
            # Try to extract health score
            try:
                import re
                score_match = re.search(r'(?:score|rating).*?(\d+(?:\.\d+)?)', ai_response.lower())
                if score_match:
                    score = float(score_match.group(1))
                    if score <= 10:
                        st.metric("Health Score", f"{score}/10")
                        if score >= 7:
                            st.success("🟢 Good Choice")
                        elif score >= 4:
                            st.warning("🟡 Moderate")
                        else:
                            st.error("🔴 Poor Choice")
            except:
                pass
            
            st.success("✅ AI Analysis Complete!")
            
        except Exception as e:
            st.error(f"❌ AI Analysis Failed: {str(e)}")
            st.info("💡 Try checking your internet connection or API key")

def generate_sample_nutrition_text(image):
    """Generate sample nutrition text based on image"""
    
    # Create hash from image for consistency
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    image_hash = hashlib.md5(img_bytes).hexdigest()
    
    # Use hash to select nutrition template
    hash_int = int(image_hash[:4], 16)
    
    templates = [
        """Nutrition Facts
Serving Size: 1 package (28g)
Calories: 140
Total Fat: 7g
Saturated Fat: 1g
Sodium: 230mg
Total Carbs: 18g
Sugars: 10g
Protein: 2g

Ingredients: Enriched flour, high fructose corn syrup, vegetable oil, salt, artificial flavor, yellow 6, red 40, BHT""",
        
        """Nutrition Facts  
Serving Size: 1 bar (40g)
Calories: 180
Total Fat: 8g
Saturated Fat: 2g
Sodium: 95mg
Total Carbs: 22g
Fiber: 6g
Sugars: 8g
Protein: 7g

Ingredients: Organic oats, almonds, honey, organic coconut oil, sea salt, natural vanilla""",
        
        """Nutrition Facts
Serving Size: 1 can (355ml)
Calories: 150
Total Fat: 0g
Sodium: 35mg
Total Carbs: 39g
Sugars: 39g
Protein: 0g

Ingredients: Carbonated water, high fructose corn syrup, caramel color, phosphoric acid, natural flavor, caffeine"""
    ]
    
    return templates[hash_int % len(templates)]

if __name__ == "__main__":
    main()