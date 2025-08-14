#!/bin/bash

echo "🚀 Setting up Ummah United Zakat Calculator Backend"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Create backend directory if it doesn't exist
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please ensure the backend files are in place."
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "⚠️  Please edit the .env file and add your OpenAI API key"
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Activate the virtual environment: source backend/venv/bin/activate"
echo "3. Start the backend: python backend/main.py"
echo "4. Start the frontend: npm run dev"
echo ""
echo "🌐 The backend will run on http://localhost:8000"
echo "📖 API documentation will be available at http://localhost:8000/docs" 