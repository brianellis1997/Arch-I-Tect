#!/bin/bash

# Arch-I-Tect Setup Script
# This script sets up the development environment for both backend and frontend

set -e

echo "🚀 Setting up Arch-I-Tect development environment..."

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then 
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
else
    echo "✅ Python $python_version found"
fi

# Check Node.js version
echo "📍 Checking Node.js version..."
node_version=$(node --version 2>&1 | cut -d'v' -f2)
required_node="18"

if [[ "$(printf '%s\n' "$required_node" "$node_version" | sort -V | head -n1)" != "$required_node" ]]; then 
    echo "❌ Node.js $required_node or higher is required. Found: $node_version"
    exit 1
else
    echo "✅ Node.js v$node_version found"
fi

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please configure your .env file with appropriate values"
fi

# Create uploads directory
mkdir -p uploads

# Deactivate virtual environment
deactivate

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd frontend

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

cd ..

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your backend/.env file with LLM provider credentials"
echo "2. Start the backend: cd backend && source venv/bin/activate && python src/main.py"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "🚀 Happy coding!"