#!/bin/bash

echo "🚀 Setting up ProjectPilotAI environment..."

echo "📦 Installing core dependencies..."
pip install -r requirements.txt

if [ -f requirements-dev.txt ]; then
  echo "🧪 Installing dev tools..."
  pip install -r requirements-dev.txt
fi

echo "✅ Setup complete!"
echo "👉 To run the dashboard:"
echo "   make run-dashboard"
