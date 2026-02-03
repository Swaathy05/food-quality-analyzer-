#!/usr/bin/env python3
"""
Food Quality Analyzer Setup Script
This script helps set up the environment for the Food Quality Analyzer
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_tesseract():
    """Provide instructions for Tesseract installation"""
    system = platform.system().lower()
    
    print("\n📋 Tesseract OCR Installation Instructions:")
    
    if system == "windows":
        print("Windows:")
        print("1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install Tesseract (default location: C:\\Program Files\\Tesseract-OCR)")
        print("3. Add Tesseract to your PATH environment variable")
        print("4. Or set TESSDATA_PREFIX environment variable")
        
    elif system == "darwin":  # macOS
        print("macOS:")
        print("1. Install using Homebrew: brew install tesseract")
        print("2. Or download from: https://github.com/tesseract-ocr/tesseract")
        
    elif system == "linux":
        print("Linux:")
        print("Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("CentOS/RHEL: sudo yum install tesseract")
        print("Arch: sudo pacman -S tesseract")
    
    print("\n⚠️  Make sure Tesseract is accessible from command line by running: tesseract --version")

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python packages installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python packages")
        sys.exit(1)

def setup_env_file():
    """Set up environment file"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("\n🔧 Setting up environment file...")
            with open(".env.example", "r") as example:
                content = example.read()
            
            with open(".env", "w") as env_file:
                env_file.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your GROQ_API_KEY")
            print("   Get your free API key from: https://console.groq.com/")
        else:
            print("❌ .env.example file not found")
    else:
        print("✅ .env file already exists")

def main():
    print("🔬 Food Quality Analyzer Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Install Python requirements
    install_requirements()
    
    # Setup environment file
    setup_env_file()
    
    # Tesseract installation instructions
    install_tesseract()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Install Tesseract OCR (see instructions above)")
    print("2. Edit .env file and add your GROQ_API_KEY")
    print("3. Run the application: streamlit run food_quality_analyzer.py")

if __name__ == "__main__":
    main()