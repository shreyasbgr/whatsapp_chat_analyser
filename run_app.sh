#!/bin/bash

# WhatsApp Chat Analyzer - Launch Script
echo "🚀 Starting WhatsApp Chat Analyzer..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Run the Streamlit app
echo "🌐 Starting Streamlit app..."
echo "📱 Your WhatsApp Chat Analyzer will open in your browser"
echo "🔗 If it doesn't open automatically, go to: http://localhost:8501"
echo ""

streamlit run app.py
