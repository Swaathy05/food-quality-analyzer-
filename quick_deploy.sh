#!/bin/bash

# Quick Deploy Script for Food Quality Analyzer
echo "🚀 Food Quality Analyzer - Quick Deploy"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Please log out and back in, then run this script again"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing"
    echo "Press Enter when ready..."
    read
fi

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Access your app:"
    echo "   Streamlit UI: http://localhost:8501"
    echo "   API: http://localhost:8000"
    echo "   Monitoring: http://localhost:3000"
    echo ""
    echo "📊 Check logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
else
    echo "❌ Deployment failed. Check logs: docker-compose logs"
fi