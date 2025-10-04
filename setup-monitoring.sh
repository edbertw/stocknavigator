#!/bin/bash

# StockNavigator Monitoring Setup Script
# This script sets up Prometheus and Grafana monitoring for the StockNavigator application

echo "🚀 Setting up StockNavigator Monitoring with Prometheus and Grafana..."

# Create necessary directories
echo "📁 Creating monitoring directories..."
mkdir -p grafana-dashboards
mkdir -p prometheus-data
mkdir -p grafana-data

# Set proper permissions
echo "🔐 Setting up permissions..."
chmod 755 grafana-dashboards/
chmod 755 prometheus-data/
chmod 755 grafana-data/


# Build and start the monitoring stack
echo "🐳 Building and starting monitoring services..."
docker-compose up

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "✅ Monitoring setup complete!"
echo ""
echo "📊 Access your monitoring services:"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3000"
echo "   • Django App: http://localhost:8000"
echo ""
echo "🔑 Default Grafana credentials:"
echo "   • Username: admin"
echo "   • Password: admin"
echo ""
echo "📈 Next steps:"
echo "   1. Access Grafana at http://localhost:3000"
echo "   2. Add Prometheus as a data source (http://prometheus:9090)"
echo "   3. Import the provided dashboard JSON files from grafana-dashboards/"
echo "   4. Configure alerts as needed"
echo ""
echo "🛠️  To stop monitoring: docker-compose down"
echo "🛠️  To view logs: docker-compose logs -f [service_name]"
echo ""
echo "Happy monitoring! 📊✨"
