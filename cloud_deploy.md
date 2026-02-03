# Cloud Platform Deployment

## Heroku (Simple)

1. **Install Heroku CLI**
2. **Create Procfile**:
   ```
   web: streamlit run Food_Quality_Analyzer/food_quality_analyzer.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set GROQ_API_KEY=your_key
   git push heroku main
   ```

## Railway (Modern)

1. **Connect GitHub repo**
2. **Set environment variables**
3. **Deploy automatically**

## DigitalOcean App Platform

1. **Connect GitHub**
2. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `streamlit run Food_Quality_Analyzer/food_quality_analyzer.py --server.port=8080 --server.address=0.0.0.0`

## AWS/GCP/Azure

Use the Docker setup with their container services:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

**Pros**: Managed infrastructure, auto-scaling
**Cons**: Can be more expensive