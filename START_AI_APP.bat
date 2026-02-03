@echo off
echo ============================================================
echo 🤖 AI FOOD QUALITY ANALYZER - REAL AI ANALYSIS
echo ============================================================
echo.
echo Starting AI-powered Food Quality Analyzer...
echo Using Groq Llama 3.1 70B for real AI analysis
echo.
echo The app will open at: http://localhost:8503
echo Press Ctrl+C to stop the application
echo ============================================================
echo.

cd /d "%~dp0"
streamlit run ai_analyzer.py --server.port 8503 --server.address localhost

pause