@echo off
echo 🚀 Food Quality Analyzer - GitHub Deployment Script
echo.

echo Step 1: Initializing Git repository...
git init

echo Step 2: Adding all files...
git add .

echo Step 3: Creating initial commit...
git commit -m "Initial commit - Food Quality Analyzer with AI-powered nutrition analysis"

echo Step 4: Setting main branch...
git branch -M main

echo.
echo ⚠️  IMPORTANT: Before continuing, you need to:
echo 1. Create a new repository on GitHub named 'food-quality-analyzer'
echo 2. Copy the repository URL (e.g., https://github.com/yourusername/food-quality-analyzer.git)
echo.
set /p repo_url="Enter your GitHub repository URL: "

echo Step 5: Adding remote origin...
git remote add origin %repo_url%

echo Step 6: Pushing to GitHub...
git push -u origin main

echo.
echo ✅ Successfully pushed to GitHub!
echo.
echo 🌐 Next steps for Streamlit Cloud deployment:
echo 1. Go to https://share.streamlit.io
echo 2. Click "New app"
echo 3. Connect your GitHub account
echo 4. Select your repository: food-quality-analyzer
echo 5. Set main file path: streamlit_app.py
echo 6. Add secrets in Advanced settings:
echo    GROQ_API_KEY = your_groq_api_key_here
echo    SECRET_KEY = your_secret_key_here
echo 7. Click "Deploy"
echo.
echo 🎉 Your app will be live at: https://your-app-name.streamlit.app
echo.
pause