@echo off
echo ============================================================
echo 🧠 SMART AI FOOD ANALYZER - AUTO MODEL DETECTION
echo ============================================================
echo.
echo Starting Smart AI Food Quality Analyzer...
echo ✅ Automatically detects and uses the best available AI model
echo ✅ Works with current Groq API models
echo ✅ Real AI analysis with fallback support
echo.
echo The app will open at: http://localhost:8506
echo Press Ctrl+C to stop
echo ============================================================
echo.

cd /d "%~dp0"
streamlit run smart_ai_app.py --server.port 8506

pause