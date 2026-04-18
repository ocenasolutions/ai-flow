#!/bin/bash
# Start the web application

echo "=================================="
echo "🚀 Starting AI Content Generator"
echo "=================================="

# Activate virtual environment
source venv/bin/activate

# Install Flask if not installed
pip install flask --quiet

# Start the app
python app.py
