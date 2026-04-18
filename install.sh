#!/bin/bash
# Installation script for AI Content System

echo "=================================="
echo "AI Content System - Installation"
echo "=================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Installation failed"
    exit 1
fi

# Make scripts executable
chmod +x run_pipeline.py
chmod +x content_scraper.py
chmod +x content_validator.py
chmod +x voice_writer.py
chmod +x hook_generator.py

echo ""
echo "=================================="
echo "✅ Installation complete!"
echo "=================================="
echo ""
echo "To run the pipeline:"
echo "  python run_pipeline.py"
echo ""
echo "For help:"
echo "  python run_pipeline.py --help"
echo ""
