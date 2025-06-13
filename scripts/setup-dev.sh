#!/bin/bash

# Agent Transformation Engine - Development Setup Script
# This script sets up the complete ATE development environment

set -e

echo "🚀 Setting up Agent Transformation Engine Development Environment"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p data/{postgres,redis,elasticsearch,storage}
mkdir -p config/{development,staging,production}

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOF
# ATE Platform Environment Configuration
ENVIRONMENT=development

# Database Configuration
POSTGRES_DB=ate_platform
POSTGRES_USER=ate
POSTGRES_PASSWORD=ate_password_change_in_production
DATABASE_URL=postgresql://ate:ate_password_change_in_production@postgres:5432/ate_platform

# Redis Configuration
REDIS_URL=redis://redis:6379

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Service URLs (for development)
AUTH_SERVICE_URL=http://auth-service:5001
PARSING_SERVICE_URL=http://parsing-service:5002
TENANT_SERVICE_URL=http://tenant-service:5003
STORAGE_SERVICE_URL=http://storage-service:5004

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000

# Monitoring Configuration
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://elasticsearch:9200
EOF
    echo "✅ Created .env file with default configuration"
else
    echo "ℹ️  .env file already exists, skipping creation"
fi

# Create database initialization script
echo "🗄️  Setting up database initialization..."
mkdir -p scripts
cat > scripts/init-db.sql << EOF
-- ATE Platform Database Initialization

-- Create databases for different services
CREATE DATABASE ate_auth;
CREATE DATABASE ate_analysis;
CREATE DATABASE ate_intelligence;
CREATE DATABASE ate_opportunities;
CREATE DATABASE ate_architecture;

-- Create users and grant permissions
CREATE USER ate_auth WITH PASSWORD 'ate_auth_password';
CREATE USER ate_analysis WITH PASSWORD 'ate_analysis_password';
CREATE USER ate_intelligence WITH PASSWORD 'ate_intelligence_password';
CREATE USER ate_opportunities WITH PASSWORD 'ate_opportunities_password';
CREATE USER ate_architecture WITH PASSWORD 'ate_architecture_password';

GRANT ALL PRIVILEGES ON DATABASE ate_auth TO ate_auth;
GRANT ALL PRIVILEGES ON DATABASE ate_analysis TO ate_analysis;
GRANT ALL PRIVILEGES ON DATABASE ate_intelligence TO ate_intelligence;
GRANT ALL PRIVILEGES ON DATABASE ate_opportunities TO ate_opportunities;
GRANT ALL PRIVILEGES ON DATABASE ate_architecture TO ate_architecture;

-- Enable necessary extensions
\c ate_platform;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
EOF

# Create Docker build script
echo "🐳 Creating Docker build script..."
cat > scripts/build.sh << 'EOF'
#!/bin/bash

# Build all ATE services
echo "🔨 Building ATE services..."

# Build core services
echo "Building core services..."
docker-compose build auth-service
docker-compose build tenant-service
docker-compose build storage-service

# Build analysis services
echo "Building analysis services..."
docker-compose build parsing-service
docker-compose build dependency-service
docker-compose build quality-service

# Build intelligence services
echo "Building intelligence services..."
docker-compose build domain-service
docker-compose build process-service

# Build opportunity services
echo "Building opportunity services..."
docker-compose build opportunity-service
docker-compose build business-case-service

# Build architecture services
echo "Building architecture services..."
docker-compose build architecture-service

# Build API gateway and frontend
echo "Building API gateway and frontend..."
docker-compose build api-gateway
docker-compose build frontend

echo "✅ All services built successfully!"
EOF

chmod +x scripts/build.sh

# Create development start script
echo "🚀 Creating development start script..."
cat > scripts/start-dev.sh << 'EOF'
#!/bin/bash

# Start ATE development environment
echo "🚀 Starting ATE development environment..."

# Start infrastructure services first
echo "Starting infrastructure services..."
docker-compose up -d postgres redis elasticsearch

# Wait for services to be ready
echo "Waiting for infrastructure services to be ready..."
sleep 10

# Start core services
echo "Starting core services..."
docker-compose up -d auth-service tenant-service storage-service

# Wait for core services
sleep 5

# Start analysis services
echo "Starting analysis services..."
docker-compose up -d parsing-service dependency-service quality-service

# Start intelligence services
echo "Starting intelligence services..."
docker-compose up -d domain-service process-service

# Start opportunity services
echo "Starting opportunity services..."
docker-compose up -d opportunity-service business-case-service

# Start architecture services
echo "Starting architecture services..."
docker-compose up -d architecture-service

# Start API gateway and frontend
echo "Starting API gateway and frontend..."
docker-compose up -d api-gateway frontend

# Start monitoring services
echo "Starting monitoring services..."
docker-compose up -d prometheus grafana kibana

echo "✅ ATE development environment started!"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend:     http://localhost:3000"
echo "  API Gateway:  http://localhost:8000"
echo "  Grafana:      http://localhost:3001 (admin/admin)"
echo "  Kibana:       http://localhost:5601"
echo "  Prometheus:   http://localhost:9090"
echo ""
echo "📊 Service Status:"
docker-compose ps
EOF

chmod +x scripts/start-dev.sh

# Create stop script
echo "🛑 Creating stop script..."
cat > scripts/stop.sh << 'EOF'
#!/bin/bash

# Stop ATE development environment
echo "🛑 Stopping ATE development environment..."

docker-compose down

echo "✅ ATE development environment stopped!"
EOF

chmod +x scripts/stop.sh

# Create logs script
echo "📋 Creating logs script..."
cat > scripts/logs.sh << 'EOF'
#!/bin/bash

# View logs for ATE services
if [ -z "$1" ]; then
    echo "📋 Showing logs for all services..."
    docker-compose logs -f
else
    echo "📋 Showing logs for $1..."
    docker-compose logs -f "$1"
fi
EOF

chmod +x scripts/logs.sh

# Create test script
echo "🧪 Creating test script..."
cat > scripts/test.sh << 'EOF'
#!/bin/bash

# Run tests for ATE services
echo "🧪 Running ATE tests..."

# Run unit tests for each service
services=("auth-service" "parsing-service" "opportunity-service" "architecture-service")

for service in "${services[@]}"; do
    echo "Testing $service..."
    docker-compose exec "$service" python -m pytest tests/ -v
done

echo "✅ All tests completed!"
EOF

chmod +x scripts/test.sh

# Create requirements files for Python services
echo "📦 Creating Python requirements files..."

# Core auth service requirements
mkdir -p core/auth-service
cat > core/auth-service/requirements.txt << EOF
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.3
psycopg2-binary==2.9.7
redis==4.6.0
bcrypt==4.0.1
marshmallow==3.20.1
python-dotenv==1.0.0
gunicorn==21.2.0
prometheus-client==0.17.1
EOF

# Parsing service requirements
mkdir -p analysis/parsing-service
cat > analysis/parsing-service/requirements.txt << EOF
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
redis==4.6.0
tree-sitter==0.20.1
tree-sitter-python==0.20.4
tree-sitter-javascript==0.20.1
tree-sitter-java==0.20.2
ast-tools==0.1.0
python-dotenv==1.0.0
gunicorn==21.2.0
prometheus-client==0.17.1
EOF

# Create Dockerfiles for services
echo "🐳 Creating Dockerfiles..."

# Auth service Dockerfile
cat > core/auth-service/Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src/main.py

# Expose port
EXPOSE 5001

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "src.main:app"]
EOF

# Parsing service Dockerfile
cat > analysis/parsing-service/Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src/main.py

# Expose port
EXPOSE 5002

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "4", "src.main:app"]
EOF

echo "✅ Development environment setup complete!"
echo ""
echo "🚀 To start the ATE development environment:"
echo "  ./scripts/start-dev.sh"
echo ""
echo "📋 To view logs:"
echo "  ./scripts/logs.sh [service-name]"
echo ""
echo "🛑 To stop the environment:"
echo "  ./scripts/stop.sh"
echo ""
echo "🧪 To run tests:"
echo "  ./scripts/test.sh"

