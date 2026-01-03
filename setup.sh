#!/bin/bash

echo "=========================================="
echo "Ironclad Degree Auditor - Setup Script"
echo "=========================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check for PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is required but not installed."
    exit 1
fi

echo "✓ All prerequisites found"
echo ""

# Create PostgreSQL database
echo "Creating PostgreSQL database..."
psql -U postgres -c "CREATE DATABASE degree_audit;" 2>/dev/null || echo "Database may already exist, continuing..."

# Backend setup
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

echo "✓ Backend dependencies installed"

# Seed database
echo ""
echo "Seeding database with mock data..."
python seed.py

echo "✓ Database seeded"

# Frontend setup
echo ""
echo "Setting up frontend..."
cd ../frontend

npm install

echo "✓ Frontend dependencies installed"
echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit: http://localhost:3000"
echo ""
echo "Demo credentials:"
echo "  Email: alice@ucla.edu"
echo "  Password: password123"
echo ""
