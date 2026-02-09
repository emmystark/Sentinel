#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Create directories for Tesseract binary and data
mkdir -p bin tessdata

# Download static Tesseract binary
curl -L https://github.com/DanielMYT/tesseract-static/releases/download/v5.4.1/tesseract.x86_64 -o bin/tesseract

# Make the binary executable
chmod +x bin/tesseract

# Download English trained data (add more curls for other languages if needed)
curl -L https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata -o tessdata/eng.traineddata