# Food Quality Analyzer - Production Makefile

.PHONY: help install test lint format clean build run deploy

# Default target
help:
	@echo "Food Quality Analyzer - Production Commands"
	@echo "==========================================="
	@echo "install     - Install dependencies"
	@echo "test        - Run tests with coverage"
	@echo "lint        - Run linting checks"
	@echo "format      - Format code"
	@echo "clean       - Clean build artifacts"
	@echo "build       - Build Docker images"
	@echo "run         - Run development server"
	@echo "run-prod    - Run production server"
	@echo "deploy      - Deploy to production"
	@echo "docs        - Generate documentation"
	@echo "security    - Run security checks"

# Development setup
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-unit:
	pytest tests/ -v -m "unit" --cov=src

test-integration:
	pytest tests/ -v -m "integration"

test-api:
	pytest tests/test_api.py -v

# Code quality
lint:
	flake8 src tests
	mypy src
	black --check src tests
	isort --check-only src tests

format:
	black src tests
	isort src tests

security:
	bandit -r src/
	safety check

# Build and deployment
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

build:
	docker build -t food-analyzer:latest .
	docker build -t food-analyzer:dev --target development .

build-prod:
	docker build -t food-analyzer:prod --target production .

# Development server
run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-streamlit:
	streamlit run app_streamlit.py --server.port 8501

run-prod:
	gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Docker operations
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

# Database operations
db-migrate:
	alembic upgrade head

db-revision:
	alembic revision --autogenerate -m "$(message)"

db-reset:
	alembic downgrade base
	alembic upgrade head

# Monitoring
monitor:
	docker-compose up -d prometheus grafana

# Documentation
docs:
	@echo "Generating API documentation..."
	@echo "Visit http://localhost:8000/docs for interactive API docs"

# Production deployment
deploy-staging:
	@echo "Deploying to staging environment..."
	docker-compose -f docker-compose.staging.yml up -d

deploy-prod:
	@echo "Deploying to production environment..."
	@echo "Make sure to update environment variables!"
	docker-compose -f docker-compose.prod.yml up -d

# Health checks
health-check:
	curl -f http://localhost:8000/api/v1/health/check || exit 1

# Backup
backup-db:
	docker-compose exec db pg_dump -U postgres food_analyzer > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Load testing
load-test:
	@echo "Running load tests..."
	@echo "Install locust: pip install locust"
	@echo "Run: locust -f tests/load_test.py --host=http://localhost:8000"

# CI/CD helpers
ci-test:
	pytest tests/ --junitxml=test-results.xml --cov=src --cov-report=xml

ci-build:
	docker build -t food-analyzer:$(shell git rev-parse --short HEAD) .

# Environment setup
setup-dev:
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

setup-prod:
	cp .env.production .env
	@echo "Please edit .env file with production configuration"

# Performance profiling
profile:
	python -m cProfile -o profile.stats src/api/main.py
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"