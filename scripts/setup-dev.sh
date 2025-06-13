#!/bin/bash

# ATE Development Environment Setup Script
# Sets up the complete development environment for all services

set -e

echo "🚀 Setting up ATE Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating directory structure..."
mkdir -p monitoring/grafana/{dashboards,datasources}
mkdir -p scripts
mkdir -p logs

# Create database initialization script
print_status "Creating database initialization script..."
cat > scripts/init-databases.sql << 'EOF'
-- Create databases for different services
CREATE DATABASE ate_auth;
CREATE DATABASE ate_storage;
CREATE DATABASE ate_analysis;
CREATE DATABASE ate_business;
CREATE DATABASE ate_opportunity;
CREATE DATABASE ate_architecture;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ate_auth TO ate_user;
GRANT ALL PRIVILEGES ON DATABASE ate_storage TO ate_user;
GRANT ALL PRIVILEGES ON DATABASE ate_analysis TO ate_user;
GRANT ALL PRIVILEGES ON DATABASE ate_business TO ate_user;
GRANT ALL PRIVILEGES ON DATABASE ate_opportunity TO ate_user;
GRANT ALL PRIVILEGES ON DATABASE ate_architecture TO ate_user;
EOF

# Create Prometheus configuration
print_status "Creating Prometheus configuration..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ate-gateway'
    static_configs:
      - targets: ['ate-gateway:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'ate-auth'
    static_configs:
      - targets: ['ate-auth:5001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'ate-storage'
    static_configs:
      - targets: ['ate-storage:5002']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

# Create Grafana datasource configuration
print_status "Creating Grafana datasource configuration..."
cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create Dockerfiles for services
print_status "Creating Dockerfiles for services..."

# Auth service Dockerfile
cat > auth-service/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "src/main.py"]
EOF

# Storage service Dockerfile
cat > storage-service/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage

EXPOSE 5002

CMD ["python", "src/main.py"]
EOF

# API Gateway Dockerfile
cat > api-gateway/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "src/main.py"]
EOF

# Create environment file template
print_status "Creating environment file template..."
cat > .env.template << 'EOF'
# ATE Platform Environment Configuration

# Database Configuration
DATABASE_URL=postgresql://ate_user:ate_password@localhost:5432/ate_platform
POSTGRES_DB=ate_platform
POSTGRES_USER=ate_user
POSTGRES_PASSWORD=ate_password

# Security Configuration
SECRET_KEY=ate-secret-key-change-in-production
JWT_SECRET_KEY=ate-jwt-secret-change-in-production
MASTER_KEY=ate-master-encryption-key-change-in-production

# Service URLs
AUTH_SERVICE_URL=http://localhost:5001
STORAGE_SERVICE_URL=http://localhost:5002
ANALYSIS_SERVICE_URL=http://localhost:5003
BUSINESS_SERVICE_URL=http://localhost:5004
OPPORTUNITY_SERVICE_URL=http://localhost:5005
ARCHITECTURE_SERVICE_URL=http://localhost:5006

# Storage Configuration
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=/tmp/ate-storage
STORAGE_BUCKET=ate-codebases

# Development Configuration
FLASK_ENV=development
LOG_LEVEL=INFO
LOG_REQUESTS=true

# Monitoring Configuration
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
EOF

# Copy template to actual .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    print_success "Created .env file from template"
else
    print_warning ".env file already exists, skipping creation"
fi

# Create development scripts
print_status "Creating development scripts..."

# Start script
cat > scripts/start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ATE Development Environment..."
docker-compose up -d
echo "✅ Services started. Access points:"
echo "   - API Gateway: http://localhost:5000"
echo "   - Auth Service: http://localhost:5001"
echo "   - Storage Service: http://localhost:5002"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo "   - Prometheus: http://localhost:9090"
echo "   - PgAdmin: http://localhost:8080 (admin@ate.local/admin)"
EOF

# Stop script
cat > scripts/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping ATE Development Environment..."
docker-compose down
echo "✅ All services stopped"
EOF

# Logs script
cat > scripts/logs.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "📋 Showing logs for all services..."
    docker-compose logs -f
else
    echo "📋 Showing logs for service: $1"
    docker-compose logs -f "$1"
fi
EOF

# Test script
cat > scripts/test.sh << 'EOF'
#!/bin/bash
echo "🧪 Running ATE Platform Tests..."

# Test API Gateway
echo "Testing API Gateway..."
curl -s http://localhost:5000/health | jq .

# Test Auth Service
echo "Testing Auth Service..."
curl -s http://localhost:5001/health | jq .

# Test Storage Service
echo "Testing Storage Service..."
curl -s http://localhost:5002/health | jq .

# Test service health check
echo "Testing Service Health Check..."
curl -s http://localhost:5000/health/services | jq .

echo "✅ Tests completed"
EOF

# Make scripts executable
chmod +x scripts/*.sh

# Create README for development
print_status "Creating development README..."
cat > DEV_README.md << 'EOF'
# ATE Development Environment

## Quick Start

1. **Setup Environment**
   ```bash
   ./scripts/setup-dev.sh
   ```

2. **Start Services**
   ```bash
   ./scripts/start-dev.sh
   ```

3. **View Logs**
   ```bash
   ./scripts/logs.sh [service-name]
   ```

4. **Run Tests**
   ```bash
   ./scripts/test.sh
   ```

5. **Stop Services**
   ```bash
   ./scripts/stop.sh
   ```

## Service Endpoints

- **API Gateway**: http://localhost:5000
- **Auth Service**: http://localhost:5001
- **Storage Service**: http://localhost:5002
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **PgAdmin**: http://localhost:8080 (admin@ate.local/admin)

## Development Workflow

1. Make changes to service code
2. Restart specific service: `docker-compose restart <service-name>`
3. View logs: `./scripts/logs.sh <service-name>`
4. Test changes: `./scripts/test.sh`

## Database Access

- **Host**: localhost
- **Port**: 5432
- **Username**: ate_user
- **Password**: ate_password
- **Databases**: ate_auth, ate_storage, ate_analysis, etc.

## Monitoring

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

## Troubleshooting

1. **Services won't start**: Check Docker is running
2. **Port conflicts**: Modify ports in docker-compose.yml
3. **Database issues**: Reset with `docker-compose down -v`
4. **Permission issues**: Check file permissions and Docker access
EOF

print_success "ATE Development Environment setup completed!"
print_status "Next steps:"
echo "  1. Review and modify .env file if needed"
echo "  2. Run './scripts/start-dev.sh' to start all services"
echo "  3. Run './scripts/test.sh' to verify everything is working"
echo "  4. Check DEV_README.md for detailed usage instructions"

