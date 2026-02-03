#!/usr/bin/env python3
"""
Simple runner script for Food Quality Analyzer
This script will set up everything and run the application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🔬 FOOD QUALITY ANALYZER - SETUP & RUN")
    print("=" * 60)
    print("Setting up your production-ready food analysis system...")
    print()

def check_python():
    """Check Python version"""
    print("✅ Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    # Essential packages for basic functionality
    essential_packages = [
        "streamlit==1.28.1",
        "pillow==10.0.1", 
        "pytesseract==0.3.10",
        "opencv-python-headless==4.8.1.78",
        "python-dotenv==1.0.0",
        "langchain-groq==0.1.5",
        "numpy==1.24.3",
        "pandas==2.0.3",
        "plotly==5.17.0",
        "pydantic==2.5.0",
        "sqlalchemy==2.0.23"
    ]
    
    for package in essential_packages:
        try:
            print(f"Installing {package.split('==')[0]}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"⚠️  Warning: Could not install {package}")
    
    print("✅ Essential packages installed!")

def check_tesseract():
    """Check if Tesseract is available"""
    print("\n🔍 Checking Tesseract OCR...")
    try:
        result = subprocess.run(["tesseract", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR found!")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  Tesseract OCR not found. Installing instructions:")
    system = platform.system().lower()
    
    if system == "windows":
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Or use: choco install tesseract (if you have Chocolatey)")
    elif system == "darwin":  # macOS
        print("   macOS: brew install tesseract")
    else:  # Linux
        print("   Linux: sudo apt-get install tesseract-ocr tesseract-ocr-eng")
    
    print("   ⚠️  OCR features may not work without Tesseract")
    return False

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    directories = ["uploads", "logs", "data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created!")

def check_api_key():
    """Check if API key is configured"""
    print("\n🔑 Checking API configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "gsk_your_api_key_here_replace_this" in content:
                print("⚠️  GROQ API key not configured!")
                print("   1. Go to https://console.groq.com/")
                print("   2. Sign up for free")
                print("   3. Create an API key")
                print("   4. Replace 'gsk_your_api_key_here_replace_this' in .env file")
                print("   ⚠️  AI analysis will not work without API key")
                return False
            else:
                print("✅ API key configured!")
                return True
    else:
        print("❌ .env file not found!")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    print("\n🚀 Starting Food Quality Analyzer...")
    print("   📱 Streamlit UI will open at: http://localhost:8501")
    print("   🛑 Press Ctrl+C to stop the application")
    print()
    
    try:
        # Change to the correct directory
        os.chdir(Path(__file__).parent)
        
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py", 
                       "--server.port=8501", "--server.address=localhost"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        print("\nTrying alternative method...")
        try:
            import streamlit.web.cli as stcli
            sys.argv = ["streamlit", "run", "app_streamlit.py"]
            stcli.main()
        except Exception as e2:
            print(f"❌ Alternative method failed: {e2}")
            print("\nManual run command:")
            print("streamlit run app_streamlit.py")

def main():
    """Main setup and run function"""
    print_banner()
    
    # Setup steps
    check_python()
    install_requirements()
    check_tesseract()
    setup_directories()
    api_configured = check_api_key()
    
    print("\n" + "=" * 60)
    print("🎯 SETUP COMPLETE!")
    print("=" * 60)
    
    if not api_configured:
        print("⚠️  Note: Configure your GROQ API key in .env file for full functionality")
    
    print("\n🚀 Starting the application...")
    input("Press Enter to continue...")
    
    run_streamlit()

if __name__ == "__main__":
    main()