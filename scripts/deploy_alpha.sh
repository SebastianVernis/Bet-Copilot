#!/bin/bash
# Bet-Copilot Alpha Deployment Script

set -e  # Exit on error

echo "🚀 Bet-Copilot Alpha Deployment"
echo "================================"
echo ""

# Check if running in project root
if [ ! -f "main.py" ]; then
    echo "❌ Error: Run this script from project root"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose first."
    exit 1
fi

# Check .env file
if [ ! -f "docker/.env" ]; then
    echo "⚠️  No docker/.env found, copying from .env.example"
    cp docker/.env.example docker/.env
    echo "⚠️  Please edit docker/.env with your API keys"
    exit 1
fi

# Build and start containers
echo "📦 Building Docker image..."
cd docker
docker-compose build

echo ""
echo "🔄 Starting containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check health
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📡 Access Information:"
    echo "   - Web Terminal: http://localhost:7681"
    echo "   - Username: $(grep TTYD_USER .env | cut -d'=' -f2)"
    echo "   - Password: (check docker/.env)"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f ttyd"
    echo ""
    echo "🛑 Stop deployment:"
    echo "   docker-compose down"
else
    echo "❌ Deployment failed. Check logs:"
    echo "   docker-compose logs"
    exit 1
fi
