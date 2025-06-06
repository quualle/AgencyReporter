#!/bin/bash

echo "Erstelle finales Docker-Package..."

# Clean up
rm -rf AgencyReporter_Docker_Clean
mkdir AgencyReporter_Docker_Clean

# Copy files
cp -r backend frontend credentials.json AgencyReporter_Docker_Clean/

# Create docker-compose.yml
cat > AgencyReporter_Docker_Clean/docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
      - BIGQUERY_PROJECT_ID=gcpxbixpflegehilfesenioren
      - BIGQUERY_DATASET=AgencyReporter
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./backend/database:/app/database
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
EOF

# Create start script
cat > AgencyReporter_Docker_Clean/start.command << 'EOF'
#!/bin/bash

echo "======================================"
echo "Agency Reporter - Docker Start"
echo "======================================"
echo ""

cd "$(dirname "$0")"

if ! docker info > /dev/null 2>&1; then
    echo "Docker Desktop ist nicht gestartet!"
    echo "Bitte starten Sie Docker Desktop und versuchen Sie es erneut."
    echo ""
    echo "Druecken Sie eine Taste zum Beenden..."
    read -n 1
    exit 1
fi

echo "Docker laeuft"
echo ""
echo "Starte Agency Reporter (kann beim ersten Mal 5 Minuten dauern)..."

docker-compose up -d --build

sleep 10

echo "Oeffne Browser..."
open http://localhost:3000

echo ""
echo "=========================================="
echo "Agency Reporter laeuft!"
echo "=========================================="
echo ""
echo "URL: http://localhost:3000"
echo ""
echo "Druecken Sie eine Taste zum Beenden..."
read -n 1
EOF

# Create stop script
cat > AgencyReporter_Docker_Clean/stop.command << 'EOF'
#!/bin/bash

echo "Stoppe Agency Reporter..."
cd "$(dirname "$0")"
docker-compose down
echo "Agency Reporter wurde gestoppt"
echo ""
echo "Druecken Sie eine Taste zum Beenden..."
read -n 1
EOF

# Create README
cat > AgencyReporter_Docker_Clean/README.txt << 'EOF'
Agency Reporter v1.0 - Docker Edition
=====================================

VORAUSSETZUNG:
- Docker Desktop: https://www.docker.com/products/docker-desktop/

STARTEN:
1. Docker Desktop starten (Wal-Symbol)
2. Doppelklick auf "start.command"
3. Beim ersten Start: 5 Minuten warten
4. Browser oeffnet sich automatisch

STOPPEN:
- Doppelklick auf "stop.command"

Bei Problemen: 
- Ist Docker Desktop gestartet?
- Ports 3000 und 8000 muessen frei sein
EOF

# Make executable
chmod +x AgencyReporter_Docker_Clean/*.command

# Clean up
find AgencyReporter_Docker_Clean -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find AgencyReporter_Docker_Clean -name "*.pyc" -delete 2>/dev/null || true
find AgencyReporter_Docker_Clean -name ".DS_Store" -delete 2>/dev/null || true
find AgencyReporter_Docker_Clean -name "*.log" -delete 2>/dev/null || true
rm -rf AgencyReporter_Docker_Clean/backend/venv 2>/dev/null || true
rm -rf AgencyReporter_Docker_Clean/backend/database 2>/dev/null || true
rm -rf AgencyReporter_Docker_Clean/frontend/node_modules 2>/dev/null || true
rm -f AgencyReporter_Docker_Clean/backend/.env 2>/dev/null || true

# Create ZIP
zip -r AgencyReporter_Docker_CLEAN.zip AgencyReporter_Docker_Clean -x "*.git*"

# Clean up
rm -rf AgencyReporter_Docker_Clean

echo "Fertig! AgencyReporter_Docker_CLEAN.zip erstellt"