# Kopi Challenge - Tactical Empathy Debate Bot
# Makefile for project management and deployment

.PHONY: help install test run down clean docker-check docker-install

# Default target - show help
help:
	@echo "Kopi Challenge - Tactical Empathy Debate Bot"
	@echo "Available make commands:"
	@echo ""
	@echo "  make          Show this help message"
	@echo "  make install  Install all requirements to run the service"
	@echo "  make test     Run the test suite"
	@echo "  make run      Start all services with Docker Compose"
	@echo "  make down     Stop all running services"
	@echo "  make clean    Stop and remove all containers, networks, and volumes"
	@echo ""
	@echo "Environment Setup:"
	@echo "  1. Copy env.example to .env"
	@echo "  2. Configure your AI provider API keys in .env"
	@echo "  3. Run 'make install' to check dependencies"
	@echo "  4. Run 'make run' to start the services"
	@echo ""
	@echo "API Endpoint: http://localhost:8000/conversation/api/chat/"

# Check if Docker is installed
docker-check:
	@echo "Checking Docker installation..."
	@which docker > /dev/null || (echo "ERROR: Docker is not installed or not in PATH"; \
		echo "Please install Docker from: https://docs.docker.com/get-docker/"; \
		echo "For Ubuntu/Debian: sudo apt-get update && sudo apt-get install docker.io docker-compose-plugin"; \
		echo "For CentOS/RHEL: sudo yum install docker docker-compose"; \
		echo "For macOS: Install Docker Desktop from the official website"; \
		echo "For Windows: Install Docker Desktop from the official website"; \
		exit 1)
	@echo "✓ Docker is installed"

# Check if Docker Compose is available
compose-check: docker-check
	@echo "Checking Docker Compose installation..."
	@docker compose version > /dev/null 2>&1 || docker-compose --version > /dev/null 2>&1 || \
		(echo "ERROR: Docker Compose is not installed or not in PATH"; \
		echo "Please install Docker Compose:"; \
		echo "For newer Docker installations: Docker Compose is included as 'docker compose'"; \
		echo "For older installations: pip install docker-compose"; \
		echo "Or follow: https://docs.docker.com/compose/install/"; \
		exit 1)
	@echo "✓ Docker Compose is available"

# Check if Make is installed (redundant but good for completeness)
make-check:
	@echo "Checking Make installation..."
	@which make > /dev/null || (echo "ERROR: Make is not installed"; \
		echo "For Ubuntu/Debian: sudo apt-get install build-essential"; \
		echo "For CentOS/RHEL: sudo yum groupinstall 'Development Tools'"; \
		echo "For macOS: Install Xcode Command Line Tools"; \
		exit 1)
	@echo "✓ Make is installed"

# Check environment file
env-check:
	@echo "Checking environment configuration..."
	@if [ ! -f .env ]; then \
		echo "WARNING: .env file not found"; \
		if [ -f env.example ]; then \
			echo "Please copy env.example to .env and configure your settings:"; \
			echo "  cp env.example .env"; \
		else \
			echo "Please create a .env file with the required environment variables."; \
			echo "See README.md for the complete list of required variables."; \
		fi; \
		echo ""; \
		echo "Minimum required variables:"; \
		echo "  POSTGRES_USER=postgres"; \
		echo "  POSTGRES_PASSWORD=your_secure_password"; \
		echo "  POSTGRES_DB=tactical_empathy"; \
		echo "  DB_HOST=postgres"; \
		echo "  DB_PORT=5432"; \
		echo "  APP_NAME=tactical_empathy_app"; \
		echo "  APP_PORT=8000"; \
		echo "  SECRET_KEY=your_django_secret_key_here"; \
		echo "  AI_PROVIDER=openai"; \
		echo "  OPENAI_API_KEY=your_openai_api_key"; \
		echo ""; \
		exit 1; \
	fi
	@echo "✓ .env file found"

# Install all requirements and check dependencies
install: make-check docker-check compose-check env-check
	@echo "✓ All dependencies are installed and configured"
	@echo ""
	@echo "Installation complete! You can now run:"
	@echo "  make run    # Start all services"
	@echo "  make test   # Run tests"
	@echo ""
	@echo "The API will be available at: http://localhost:8000/conversation/api/chat/"

# Run tests
test: docker-check compose-check env-check
	@echo "Running test suite..."
	@if docker compose ps | grep -q "tactical_empathy_app.*Up"; then \
		echo "Running tests in existing container..."; \
		docker compose exec app python manage.py test mirror.tests --verbosity=2; \
	else \
		echo "Starting temporary containers for testing..."; \
		docker compose run --rm app python manage.py test mirror.tests --verbosity=2; \
	fi
	@echo "✓ Tests completed"

# Start all services
run: docker-check compose-check env-check
	@echo "Starting all services with Docker Compose..."
	@echo "This will start:"
	@echo "  - PostgreSQL database"
	@echo "  - Django application server"
	@echo ""
	docker compose up -d
	@echo ""
	@echo "Services started! Checking health..."
	@sleep 5
	@echo ""
	@echo "✓ Services are running:"
	@docker compose ps
	@echo ""
	@echo "API endpoint: http://localhost:8000/conversation/api/chat/"
	@echo "Admin interface: http://localhost:8000/admin/"
	@echo ""
	@echo "To view logs: docker compose logs -f"
	@echo "To stop services: make down"

# Stop all services
down: docker-check
	@echo "Stopping all services..."
	docker compose down
	@echo "✓ All services stopped"

# Clean up - stop and remove containers, networks, and volumes
clean: docker-check
	@echo "Cleaning up all containers, networks, and volumes..."
	@echo "This will remove all data including the database!"
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker compose down -v --remove-orphans; \
		docker system prune -f --volumes; \
		echo "✓ Cleanup completed"; \
	else \
		echo "Cleanup cancelled"; \
	fi

# Development helpers (not required by challenge but useful)

# Show service logs
logs: docker-check
	docker compose logs -f

# Open a shell in the app container
shell: docker-check
	docker compose exec app /bin/bash

# Run Django management commands
manage: docker-check
	@if [ -z "$(CMD)" ]; then \
		echo "Usage: make manage CMD='your_command'"; \
		echo "Example: make manage CMD='createsuperuser'"; \
		exit 1; \
	fi
	docker compose exec app python manage.py $(CMD)

# Rebuild containers (useful during development)
rebuild: docker-check
	@echo "Rebuilding containers..."
	docker compose build --no-cache
	@echo "✓ Containers rebuilt"

# Check service status
status: docker-check
	@echo "Service Status:"
	@docker compose ps
	@echo ""
	@echo "Container Health:"
	@docker compose exec postgres pg_isready -U postgres 2>/dev/null && echo "✓ Database: Healthy" || echo "✗ Database: Unhealthy"
	@curl -s -o /dev/null -w "✓ API: %{http_code}\n" http://localhost:8000/conversation/api/chat/ || echo "✗ API: Unreachable"

# Quick setup for new developers
quick-start: install
	@echo "Setting up the project for the first time..."
	@if [ ! -f .env ]; then \
		echo "Please create .env file first (see README.md)"; \
		exit 1; \
	fi
	make run
	@echo ""
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running initial setup..."
	docker compose exec app python manage.py migrate
	@echo ""
	@echo "✓ Quick start completed!"
	@echo "API is ready at: http://localhost:8000/conversation/api/chat/"
