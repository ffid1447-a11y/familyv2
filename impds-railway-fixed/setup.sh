#!/bin/bash

echo "Setting up IMPDS API for Railway..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python packages in virtual environment
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
npm install

echo "✅ Setup complete!"
echo "👉 Start server: node server.js"
