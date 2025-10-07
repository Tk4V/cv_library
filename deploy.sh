#!/bin/bash

# CV Project Deployment Script for DigitalOcean
echo "🚀 Deploying CV Project to DigitalOcean..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found! Please create it first."
    echo "Copy .env.example to .env and configure it:"
    echo "cp .env.example .env"
    echo "nano .env"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down

# Pull latest changes
print_status "Pulling latest changes from Git..."
git pull origin main

# Build and start containers
print_status "Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for containers to be ready
print_status "Waiting for containers to start..."
sleep 30

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    print_error "Some containers failed to start. Check logs:"
    docker-compose logs
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_status "Checking for superuser..."
if ! docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" | grep -q "Superuser exists"; then
    print_warning "No superuser found. You may want to create one:"
    echo "docker-compose exec web python manage.py createsuperuser"
fi

# Show status
print_status "Deployment completed successfully!"
echo ""
echo "📱 Access your application:"
echo "   Web App: http://$(curl -s ifconfig.me):8000"
echo "   Celery Monitor: http://$(curl -s ifconfig.me):5555"
echo ""
echo "🛠️ Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Update: ./deploy.sh"
echo ""
print_status "Deployment finished! 🎉"
