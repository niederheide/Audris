#!/bin/bash

# Deployment script for Audris DORA Assessment Tool

echo "Starting deployment preparation..."

# Create necessary directories
mkdir -p logs uploads

# Initialize database schema
echo "Initializing database schema..."
python -c "from app.database.handler import DatabaseHandler; DatabaseHandler().init_schema()"

# Train ML model if needed
echo "Training ML risk assessment model..."
python train_risk_model.py

# Run basic tests
echo "Running validation tests..."
python quick_test.py

# Start the application
echo "Starting Audris application..."
if [ "$1" = "api" ]; then
    echo "Starting API server..."
    uvicorn api_server:app --host 0.0.0.0 --port 8000
else
    echo "Starting Streamlit UI..."
    streamlit run ui/streamlit_app.py --server.port 5000 --server.address 0.0.0.0
fi