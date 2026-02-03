# Docker Deployment Guide

## Local Docker Setup

1. **Create .env file**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Build and run**:
   ```bash
   docker-compose up -d
   ```

3. **Access your app**:
   - Streamlit UI: http://localhost:8501
   - API: http://localhost:8000
   - Monitoring: http://localhost:3000 (Grafana)

## Production Docker Deployment

### On VPS/Cloud Server:

1. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Clone and deploy**:
   ```bash
   git clone your-repo
   cd Food_Quality_Analyzer
   docker-compose -f docker-compose.yml up -d
   ```

3. **Setup SSL** (optional):
   ```bash
   # Add SSL certificates to nginx/ssl/
   # Update nginx.conf for HTTPS
   ```

**Pros**: Full control, scalable, includes monitoring
**Cons**: Requires server management