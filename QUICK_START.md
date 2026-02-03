# 🚀 Quick Start Guide

## How to Run the Food Quality Analyzer

### Option 1: Double-Click to Run (Easiest)
1. **Double-click** `START_APP.bat` 
2. **Wait** for the app to start (takes 10-30 seconds)
3. **Open browser** and go to: `http://localhost:8501`
4. **Start analyzing** food products!

### Option 2: Command Line
```bash
# Navigate to the folder
cd Food_Quality_Analyzer

# Run the demo
streamlit run simple_demo.py
```

### Option 3: Full Version (with API key)
```bash
# Run the full version
streamlit run app_streamlit.py
```

## 🎯 What You'll See

1. **🏠 Welcome Screen**: Professional food analyzer interface
2. **👤 Health Profile**: Set up your allergies and health conditions
3. **📷 Upload Section**: Upload nutrition label photos
4. **🎯 Demo Button**: Try sample analysis without uploading
5. **📊 Results**: Comprehensive food analysis with:
   - Health scores
   - Chemical detection
   - Personalized recommendations
   - Risk assessments

## 🔧 Troubleshooting

### If the app doesn't start:
1. Make sure Python is installed
2. Install Streamlit: `pip install streamlit pillow`
3. Run: `streamlit run simple_demo.py`

### If you see "Email:" prompt:
- Just press Enter to skip
- The app will start after this

### If port 8501 is busy:
- Try: `streamlit run simple_demo.py --server.port 8502`
- Then go to: `http://localhost:8502`

## 🎉 Demo Features

The demo version includes:
- ✅ Full UI with professional design
- ✅ Mock nutrition analysis
- ✅ Chemical detection simulation
- ✅ Health recommendations
- ✅ Risk assessments
- ✅ Export options
- ✅ All features working without API keys

## 🔑 For Full Version

To use the full version with real AI analysis:
1. Get free API key from: https://console.groq.com/
2. Edit `.env` file and add your key
3. Run: `streamlit run app_streamlit.py`

---

**🎯 Ready to analyze food quality like a pro!**