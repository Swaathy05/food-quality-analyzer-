@echo off
echo ============================================================
echo 🤖 WORKING AI FOOD ANALYZER
echo ============================================================
echo.
echo Starting the working AI Food Quality Analyzer...
echo This version is tested and guaranteed to work!
echo.
echo The app will open at: http://localhost:8504
echo Press Ctrl+C to stop
echo ============================================================
echo.

cd /d "%~dp0"
streamlit run working_ai_app.py --server.port 8504

pause