@echo off
echo ============================================================
echo 🔬 FOOD QUALITY ANALYZER - STARTING APPLICATION
echo ============================================================
echo.
echo Starting the Food Quality Analyzer...
echo The app will open in your web browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo ============================================================
echo.

cd /d "%~dp0"
streamlit run simple_demo.py --server.port 8501 --server.address localhost

pause