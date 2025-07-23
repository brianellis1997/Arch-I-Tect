# Arch-I-Tect Makefile

.PHONY: help setup install-backend install-frontend run-backend run-frontend run test clean docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make setup          - Set up the entire development environment"
	@echo "  make install        - Install all dependencies"
	@echo "  make run            - Run both backend and frontend"
	@echo "  make run-backend    - Run backend only"
	@echo "  make run-frontend   - Run frontend only"
	@echo "  make test           - Run all tests"
	@echo "  make clean          - Clean up generated files"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start Docker Compose services"
	@echo "  make docker-down    - Stop Docker Compose services"

setup:
	@echo "Setting up development environment..."
	@chmod +x setup.sh
	@conda run -n arch-i-tect ./setup.sh

install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

run-backend:
	@echo "Starting backend server..."
	@cd backend && . venv/bin/activate && python src/main.py

run-frontend:
	@echo "Starting frontend development server..."
	@cd frontend && npm run dev

run:
	@echo "Starting both backend and frontend..."
	@make -j 2 run-backend run-frontend

test:
	@echo "Running backend tests..."
	@cd backend && . venv/bin/activate && pytest
	@echo "Running frontend tests..."
	@cd frontend && npm test

clean:
	@echo "Cleaning up..."
	@rm -rf backend/__pycache__ backend/src/__pycache__ backend/venv
	@rm -rf frontend/node_modules frontend/dist
	@rm -rf uploads/* logs/*
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete

docker-build:
	@echo "Building Docker images..."
	@docker-compose build

docker-up:
	@echo "Starting Docker services..."
	@docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	@docker-compose down

# Development shortcuts
dev: run
build: docker-build
up: docker-up
down: docker-down