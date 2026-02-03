# 🔬 Food Quality & Chemical Analyzer

An AI-powered web application that analyzes nutrition labels to provide comprehensive health insights, chemical safety assessments, and personalized dietary recommendations.

## ✨ Features

- **🖼️ OCR Text Extraction**: Upload nutrition label images and extract text automatically
- **🤖 AI-Powered Analysis**: Uses Groq's LLaMA 3.3 70B model for comprehensive analysis
- **👤 Personalized Health Profiles**: Set allergies, dietary restrictions, and health conditions
- **🧪 Chemical Safety Analysis**: Identifies potentially harmful additives and preservatives
- **📊 Nutrition Scoring**: Provides health scores and consumption recommendations
- **💬 Interactive Q&A**: Ask specific questions about any food product
- **⚠️ Allergen Warnings**: Automatic detection based on your profile

## 🚀 Live Demo

**[Try the app live on Streamlit Cloud!](https://your-app-name.streamlit.app)**

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Groq LLaMA 3.3 70B Versatile
- **OCR**: Tesseract with OpenCV
- **Image Processing**: PIL, OpenCV
- **Language Chain**: LangChain with Groq integration

## 📋 Requirements

```
streamlit==1.28.1
pillow==10.0.1
pytesseract==0.3.10
opencv-python-headless==4.8.1.78
numpy==1.24.3
python-dotenv==1.0.0
langchain-core==0.2.43
langchain-groq==0.1.5
groq==0.11.0
pydantic==2.12.5
requests==2.31.0
```

## 🔧 Setup & Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/food-quality-analyzer.git
   cd food-quality-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_streamlit.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env file
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser** to `http://localhost:8501`

### Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Food Quality Analyzer"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
   - Set main file: `streamlit_app.py`
   - Add secrets:
     ```
     GROQ_API_KEY = "your_groq_api_key_here"
     SECRET_KEY = "your_secret_key_here"
     ```

3. **Deploy and share!**

## 🎯 How to Use

1. **Set Your Health Profile**: Add allergies, dietary restrictions, health conditions, age group, and activity level in the sidebar

2. **Upload Nutrition Label**: Take a clear photo of any food product's nutrition facts label and upload it

3. **Get AI Analysis**: Click "Analyze" to receive comprehensive insights including:
   - Nutritional breakdown
   - Chemical ingredient analysis
   - Health impact assessment
   - Personalized recommendations
   - Allergen warnings
   - Nutrition quality score

4. **Ask Questions**: Type specific questions about the product for detailed answers

## 📸 Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)

### Analysis Results
![Analysis Results](screenshots/analysis-results.png)

### Health Profile Setup
![Health Profile](screenshots/health-profile.png)

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key for AI analysis | Yes |
| `SECRET_KEY` | Secret key for session management | Yes |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing fast AI inference
- **Streamlit** for the amazing web framework
- **Tesseract** for OCR capabilities
- **OpenCV** for image processing
- **LangChain** for AI orchestration

## 📞 Support

If you have any questions or issues, please:
1. Check the [Issues](https://github.com/yourusername/food-quality-analyzer/issues) page
2. Create a new issue if needed
3. Contact: your-email@example.com

---

**Made with ❤️ for healthier food choices**