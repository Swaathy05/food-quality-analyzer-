@echo off
echo ========================================
echo    Enterprise Food Quality Analyzer
echo         Tier 1 Production App
echo ========================================
echo.

echo [INFO] Starting Enterprise Food Analyzer...
echo [INFO] Features: Real OCR, Barcode Scan, Analytics, Export
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
)

REM Install required packages if needed
echo [INFO] Checking dependencies...
pip install -q streamlit python-dotenv groq pillow pandas plotly opencv-python pytesseract pyzbar[scripts] sqlite3

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found. Creating from template...
    copy .env.example .env 2>nul
    echo [INFO] Please edit .env file with your API keys
)

echo.
echo [INFO] Launching Enterprise Food Analyzer...
echo [INFO] Access at: http://localhost:8501
echo [INFO] Press Ctrl+C to stop
echo.

REM Run the enterprise application
streamlit run enterprise_app.py --server.port 8501 --server.address localhost

echo.
echo [INFO] Enterprise Food Analyzer stopped.
pause