#!/bin/bash

echo "🚀 Starting Ironclad Degree Auditor..."
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "Starting PostgreSQL with Docker..."
    docker-compose up -d
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
fi

echo "✓ PostgreSQL is running"
echo ""

# Start backend in background
echo "Starting backend server..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Check if database is seeded
if ! python3 -c "from app.database import SessionLocal; from app.models import Student; db = SessionLocal(); students = db.query(Student).count(); db.close(); exit(0 if students > 0 else 1)" 2>/dev/null; then
    echo "Seeding database..."
    python3 seed.py
fi

echo "✓ Backend ready"
echo ""

# Start backend server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "✓ Frontend ready"
echo ""
echo "Starting frontend server on http://localhost:3000"
echo ""
echo "=========================================="
echo "Demo Credentials:"
echo "  Email: alice@ucla.edu"
echo "  Password: password123"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start frontend (this blocks)
npm run dev

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null
