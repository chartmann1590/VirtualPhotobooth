#!/bin/bash

# Virtual Photobooth Deployment Script
# This script sets up a complete Docker-based photobooth application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to detect system IP
detect_ip() {
    if command -v ip >/dev/null 2>&1; then
        ip route get 1.1.1.1 | awk '{print $7; exit}' 2>/dev/null || echo "127.0.0.1"
    else
        ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1 || echo "127.0.0.1"
    fi
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the VirtualPhotobooth directory"
    exit 1
fi

# Check if git is available and this is a git repo
if command -v git >/dev/null 2>&1 && [ -d ".git" ]; then
    print_status "Updating repository..."
    git pull origin main || print_warning "Could not pull latest changes"
else
    print_warning "Git not available or not a git repository - skipping update"
fi

# Check if this script has been updated
if [ -f ".deploy_script_updated" ]; then
    print_warning "Deploy script was updated. Please run 'git pull' manually and restart."
    exit 1
fi

print_status "Starting Virtual Photobooth deployment..."

# Check Docker and Docker Compose
if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set Docker Compose command
if command -v docker compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

print_success "Docker and Docker Compose found"

# Environment file handling
if [ -f ".env" ]; then
    print_status "Found existing .env file"
    read -p "Use existing .env? (y/n): " use_existing
    if [ "$use_existing" = "y" ] || [ "$use_existing" = "Y" ]; then
        print_status "Using existing .env file"
        source .env
    else
        read -p "Backup existing .env? (y/n): " backup_env
        if [ "$backup_env" = "y" ] || [ "$backup_env" = "Y" ]; then
            cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            print_success "Backed up existing .env"
        fi
        rm .env
        print_status "Removed existing .env file"
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    
    # Generate random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Get admin password
    read -s -p "Enter admin password for settings page: " ADMIN_PASSWORD
    echo
    
    # Create .env file
    cat > .env << EOF
# Virtual Photobooth Configuration
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
ADMIN_PASSWORD=$ADMIN_PASSWORD

# SMTP Settings (optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# SMS Gateway Settings (optional)
SMS_GATE_USERNAME=
SMS_GATE_PASSWORD=

# TTS Settings (optional)
ELEVENLABS_API_KEY=

# Logging
LOG_LEVEL=INFO
EOF
    
    print_success "Created .env file"
fi

# Load environment variables
source .env

# Create necessary directories
print_status "Creating directories..."
mkdir -p static/frames photos config docker/ssl

# Generate SSL certificate
print_status "Generating self-signed SSL certificate..."
if [ ! -f "docker/ssl/cert.pem" ] || [ ! -f "docker/ssl/key.pem" ]; then
    openssl req -x509 -newkey rsa:4096 -keyout docker/ssl/key.pem -out docker/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    print_success "Generated SSL certificate"
else
    print_status "Using existing SSL certificate"
fi

# Build and start containers
print_status "Building and starting containers..."
$DOCKER_COMPOSE down --remove-orphans 2>/dev/null || true
$DOCKER_COMPOSE build --no-cache
$DOCKER_COMPOSE up -d

# Wait for containers to be ready
print_status "Waiting for containers to be ready..."
sleep 10

# Check container status
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    print_success "Containers are running"
else
    print_error "Containers failed to start"
    $DOCKER_COMPOSE logs
    exit 1
fi

# Get system IP
SYSTEM_IP=$(detect_ip)

# Final status
print_success "Virtual Photobooth deployment complete!"
echo
echo "Your photobooth is now running at:"
echo "  • Local: https://localhost/"
echo "  • Network: https://$SYSTEM_IP/"
echo
echo "Settings page: https://$SYSTEM_IP/settings"
echo "  • Username: admin"
echo "  • Password: $ADMIN_PASSWORD"
echo
echo "To stop the application:"
echo "  $DOCKER_COMPOSE down"
echo
echo "To view logs:"
echo "  $DOCKER_COMPOSE logs -f"
echo
echo "To update the application:"
echo "  git pull && $DOCKER_COMPOSE up -d --build"
echo
echo "Documentation:"
echo "  • Overview: https://$SYSTEM_IP/docs/overview"
echo "  • Configuration: https://$SYSTEM_IP/docs/configuration"
echo "  • TTS Setup: https://$SYSTEM_IP/docs/tts"
echo
print_success "Enjoy your Virtual Photobooth!"
