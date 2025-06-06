#!/bin/bash
# Quick Start ohne Homebrew-Check

echo "Starte Agency Reporter..."

# Backend starten
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &

# Frontend starten
cd ../frontend
npx -y serve -s build -l 3000 > ../frontend.log 2>&1 &

# Browser öffnen
sleep 5
open http://localhost:3000

echo "Agency Reporter läuft!"
echo "Zum Beenden: Ctrl+C"

# Warten
wait