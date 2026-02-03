import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Food Quality Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TextCleaner:
    @staticmethod
    def clean_text(text):
        """Clean and preprocess OCR extracted text"""
        # Remove HTML tags
        text = re.sub(r'<[^>]*?>', '', text)
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Keep alphanumeric, spaces, and common punctuation for nutrition labels
        text = re.sub(r'[^\w\s\.\,\:\;\%\(\)\-\+]', '', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s{2,}', ' ', text)
        # Trim whitespace
        text = text.strip()
        return text

class NutritionExtractor:
    @staticmethod
    def preprocess_image(image):
        """Preprocess image for better OCR results"""
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get better contrast
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Denoise
            denoised = cv2.medianBlur(thresh, 3)
            
            return denoised
        except Exception as e:
            st.error(f"Image preprocessing error: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_image(image):
        """Extract text from nutrition label image using OCR"""
        try:
            # Preprocess image
            processed_image = NutritionExtractor.preprocess_image(image)
            if processed_image is None:
                return ""
            
            # OCR configuration for better results
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()%:-+ '
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            return TextCleaner.clean_text(text)
        except Exception as e:
            st.error(f"OCR Error: {str(e)}")
            return ""

class HealthProfile:
    def __init__(self):
        self.allergies = []
        self.dietary_restrictions = []
        self.health_conditions = []
        self.age_group = ""
        self.activity_level = ""
    
    def set_profile(self, allergies, restrictions, conditions, age_group, activity_level):
        self.allergies = allergies
        self.dietary_restrictions = restrictions
        self.health_conditions = conditions
        self.age_group = age_group
        self.activity_level = activity_level

class FoodAnalyzer:
    def __init__(self):
        try:
            # Get API key from Streamlit secrets or environment
            api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
            if not api_key:
                st.error("⚠️ GROQ_API_KEY not found. Please add it to Streamlit secrets.")
                self.llm = None
                return
                
            self.llm = ChatGroq(
                temperature=0,
                groq_api_key=api_key,
                model_name="llama-3.3-70b-versatile"
            )
        except Exception as e:
            st.error(f"Failed to initialize AI model: {str(e)}")
            self.llm = None
    
    def analyze_nutrition_and_chemicals(self, nutrition_text, health_profile):
        """Analyze nutrition data and provide comprehensive health insights"""
        if not self.llm:
            return "AI analysis unavailable. Please check your GROQ_API_KEY in Streamlit secrets."
        
        prompt = PromptTemplate.from_template(
            """
            ### NUTRITION LABEL DATA:
            {nutrition_data}

            ### USER HEALTH PROFILE:
            Allergies: {allergies}
            Dietary Restrictions: {restrictions}
            Health Conditions: {conditions}
            Age Group: {age_group}
            Activity Level: {activity_level}

            ### ANALYSIS REQUIREMENTS:
            Please provide a comprehensive analysis including:

            1. **NUTRITIONAL BREAKDOWN**: List key nutrients, calories, and their values
            2. **CHEMICAL INGREDIENTS**: Identify preservatives, additives, artificial colors/flavors
            3. **HEALTH IMPACT ASSESSMENT**: 
               - Overall healthiness score (1-10)
               - Benefits and potential risks
               - Suitability for the user's health profile
            4. **CHEMICAL SAFETY ANALYSIS**:
               - Potentially harmful chemicals and their effects
               - Safe consumption limits
               - Long-term health implications
            5. **PERSONALIZED RECOMMENDATIONS**:
               - Should this person consume this product?
               - Suggested portion sizes
               - Frequency of consumption
               - Healthier alternatives if needed
            6. **ALLERGEN WARNINGS**: Check against user's allergies
            7. **NUTRITION SCORE**: Provide a nutrition quality score (1-10)

            ### RESPONSE FORMAT:
            Provide a clear, structured analysis that's easy to understand with proper markdown formatting.
            """
        )
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "nutrition_data": nutrition_text,
                "allergies": ', '.join(health_profile.allergies) if health_profile.allergies else "None",
                "restrictions": ', '.join(health_profile.dietary_restrictions) if health_profile.dietary_restrictions else "None",
                "conditions": ', '.join(health_profile.health_conditions) if health_profile.health_conditions else "None",
                "age_group": health_profile.age_group or "Not specified",
                "activity_level": health_profile.activity_level or "Not specified"
            })
            return response.content
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def answer_user_question(self, nutrition_text, health_profile, question):
        """Answer specific user questions about the product"""
        if not self.llm:
            return "AI analysis unavailable. Please check your GROQ_API_KEY in Streamlit secrets."
        
        prompt = PromptTemplate.from_template(
            """
            ### NUTRITION LABEL DATA:
            {nutrition_data}

            ### USER HEALTH PROFILE:
            Allergies: {allergies}
            Dietary Restrictions: {restrictions}
            Health Conditions: {conditions}

            ### USER QUESTION:
            {question}

            ### INSTRUCTION:
            Based on the nutrition data and user's health profile, provide a detailed answer to their question.
            Be specific and consider their personal health needs.
            """
        )
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "nutrition_data": nutrition_text,
                "allergies": ', '.join(health_profile.allergies) if health_profile.allergies else "None",
                "restrictions": ', '.join(health_profile.dietary_restrictions) if health_profile.dietary_restrictions else "None",
                "conditions": ', '.join(health_profile.health_conditions) if health_profile.health_conditions else "None",
                "question": question
            })
            return response.content
        except Exception as e:
            return f"Error answering question: {str(e)}"

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #4682B4;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .analysis-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4682B4;
        margin: 1rem 0;
    }
    .stAlert > div {
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🔬 Food Quality & Chemical Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("**Scan nutrition labels to analyze ingredients, chemicals, and get personalized health recommendations**")
    
    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'nutrition_text' not in st.session_state:
        st.session_state.nutrition_text = ""
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    
    # Initialize components
    analyzer = FoodAnalyzer()
    health_profile = HealthProfile()
    
    # Sidebar for health profile
    with st.sidebar:
        st.markdown('<h2 class="section-header">👤 Your Health Profile</h2>', unsafe_allow_html=True)
        
        # Allergies
        allergies_input = st.text_area("Allergies (one per line)", 
                                     placeholder="e.g., gluten\npeanuts\nlactose",
                                     help="Enter each allergy on a new line")
        allergies = [a.strip() for a in allergies_input.split('\n') if a.strip()]
        
        # Dietary restrictions
        restrictions_input = st.text_area("Dietary Restrictions (one per line)", 
                                        placeholder="e.g., low sugar\nhigh protein\nvegan",
                                        help="Enter each restriction on a new line")
        restrictions = [r.strip() for r in restrictions_input.split('\n') if r.strip()]
        
        # Health conditions
        conditions_input = st.text_area("Health Conditions (one per line)", 
                                      placeholder="e.g., diabetes\nhypertension\nheart disease",
                                      help="Enter each condition on a new line")
        conditions = [c.strip() for c in conditions_input.split('\n') if c.strip()]
        
        # Age group
        age_group = st.selectbox("Age Group", 
                               ["", "Child (0-12)", "Teen (13-19)", "Adult (20-64)", "Senior (65+)"])
        
        # Activity level
        activity_level = st.selectbox("Activity Level", 
                                    ["", "Sedentary", "Light", "Moderate", "Active", "Very Active"])
        
        # Set health profile
        health_profile.set_profile(allergies, restrictions, conditions, age_group, activity_level)
        
        # Profile summary
        if any([allergies, restrictions, conditions, age_group, activity_level]):
            st.markdown("---")
            st.markdown("**Profile Summary:**")
            if allergies:
                st.write(f"🚫 Allergies: {', '.join(allergies)}")
            if restrictions:
                st.write(f"🥗 Restrictions: {', '.join(restrictions)}")
            if conditions:
                st.write(f"🏥 Conditions: {', '.join(conditions)}")
            if age_group:
                st.write(f"👥 Age: {age_group}")
            if activity_level:
                st.write(f"🏃 Activity: {activity_level}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="section-header">📷 Upload Nutrition Label</h2>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose an image of the nutrition label",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear image of the product's nutrition facts label"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Nutrition Label", use_column_width=True)
            
            # Extract text button
            if st.button("🔍 Analyze Nutrition Label", type="primary", use_container_width=True):
                with st.spinner("Extracting text from image..."):
                    nutrition_text = NutritionExtractor.extract_text_from_image(image)
                    st.session_state.nutrition_text = nutrition_text
                
                if nutrition_text:
                    st.success("✅ Text extracted successfully!")
                    with st.expander("📝 Extracted Text"):
                        st.text(nutrition_text)
                    
                    # Perform analysis
                    with st.spinner("Analyzing nutrition data and chemicals..."):
                        analysis = analyzer.analyze_nutrition_and_chemicals(nutrition_text, health_profile)
                        st.session_state.conversation = [{"role": "analysis", "content": analysis}]
                        st.session_state.analysis_done = True
                        st.rerun()
                else:
                    st.error("❌ Could not extract text from image. Please try a clearer image.")
    
    with col2:
        if st.session_state.analysis_done:
            st.markdown('<h2 class="section-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
            
            # Display analysis
            for message in st.session_state.conversation:
                if message["role"] == "analysis":
                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    st.markdown(message["content"])
                    st.markdown('</div>', unsafe_allow_html=True)
                elif message["role"] == "user":
                    st.markdown(f"**❓ Your Question:** {message['content']}")
                elif message["role"] == "assistant":
                    st.markdown(f"**🤖 Answer:** {message['content']}")
            
            # Question input
            st.markdown('<h3 class="section-header">💬 Ask Questions</h3>', unsafe_allow_html=True)
            user_question = st.text_input("Ask about this product:", 
                                        placeholder="e.g., Is this safe for diabetics? What chemicals should I be concerned about?")
            
            if st.button("Submit Question", use_container_width=True):
                if user_question and st.session_state.nutrition_text:
                    # Add user question to conversation
                    st.session_state.conversation.append({"role": "user", "content": user_question})
                    
                    # Get answer
                    with st.spinner("Getting answer..."):
                        answer = analyzer.answer_user_question(
                            st.session_state.nutrition_text, 
                            health_profile, 
                            user_question
                        )
                        st.session_state.conversation.append({"role": "assistant", "content": answer})
                    
                    st.rerun()
                elif not user_question:
                    st.warning("Please enter a question.")
                else:
                    st.warning("Please analyze a nutrition label first.")
        else:
            st.markdown('<h2 class="section-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
            st.info("👆 Upload a nutrition label image and click 'Analyze' to see results here!")
    
    # Instructions
    with st.expander("📋 How to Use This App"):
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        1. **Set up your health profile** in the sidebar:
           - Add allergies, dietary restrictions, health conditions
           - Select your age group and activity level
        
        2. **Upload a nutrition label image**:
           - Use well-lit, clear photos
           - Ensure the nutrition facts label is fully visible
           - Avoid blurry or angled shots
        
        3. **Get AI-powered analysis**:
           - Click 'Analyze Nutrition Label'
           - Review comprehensive health insights
           - Get personalized recommendations
        
        4. **Ask specific questions**:
           - Type questions about the product
           - Get detailed answers based on your health profile
        
        ### 🎯 What This App Analyzes
        
        - **Nutritional Content**: Calories, macros, vitamins, minerals
        - **Chemical Ingredients**: Preservatives, additives, artificial compounds
        - **Health Impact**: Safety assessment, consumption recommendations
        - **Personalized Advice**: Tailored to your health profile
        - **Allergen Detection**: Checks against your specific allergies
        
        ### 💡 Tips for Best Results
        
        - Use high-resolution images
        - Ensure good lighting when taking photos
        - Keep the nutrition label flat and unfolded
        - Include ingredient lists when possible
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            🔬 Food Quality & Chemical Analyzer | Powered by AI | 
            <a href='https://github.com/yourusername/food-quality-analyzer' target='_blank'>GitHub</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()