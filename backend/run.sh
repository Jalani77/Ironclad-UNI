#!/bin/bash

# Start the FastAPI backend
cd /workspace/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
