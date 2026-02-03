# Deploy to Streamlit Cloud

## Quick Setup (5 minutes)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Food Quality Analyzer"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file: `Food_Quality_Analyzer/food_quality_analyzer.py`

3. **Add Environment Variables**:
   - GROQ_API_KEY=your_groq_api_key
   - SECRET_KEY=your_secret_key

4. **Deploy**: Click "Deploy" and you're live!

**Pros**: Free, automatic HTTPS, easy updates
**Cons**: Limited resources, public repos only (for free tier)