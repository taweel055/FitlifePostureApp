#!/bin/bash

# Fitlife Posture - Professional Posture Assessment System
# Launch Script for macOS

echo "🏋️‍♂️ FITLIFE POSTURE - PROFESSIONAL POSTURE ASSESSMENT SYSTEM"
echo "================================================================"
echo "🚀 Starting Fitlife Posture..."
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "import flask, cv2, mediapipe, reportlab, flask_socketio, numpy" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️ Dependencies not found. Installing..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please run manually:"
        echo "   pip3 install -r requirements.txt"
        exit 1
    fi
fi

echo "✅ Dependencies verified"
echo ""

# Launch application
echo "🚀 Launching Fitlife Posture..."
echo "📱 Access at: http://localhost:8081"
echo "🎯 Optimized for Insta360 Link 2 camera"
echo "🔄 Dynamic camera switching available"
echo ""
echo "Press Ctrl+C to stop the application"
echo "================================================================"

python3 fitlife_posture_assessment.py
