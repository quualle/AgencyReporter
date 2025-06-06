#!/bin/bash

echo "Erstelle finales Docker-Package mit Launcher..."

# Create directory
rm -rf AgencyReporter_Docker_Final
mkdir -p AgencyReporter_Docker_Final

# Copy files
cp -r backend frontend credentials.json AgencyReporter_Docker_Final/

# Create docker-compose.yml
printf 'version: "3.8"\n\nservices:\n  backend:\n    build: ./backend\n    ports:\n      - "8000:8000"\n    environment:\n      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json\n      - BIGQUERY_PROJECT_ID=gcpxbixpflegehilfesenioren\n      - BIGQUERY_DATASET=AgencyReporter\n    volumes:\n      - ./credentials.json:/app/credentials.json:ro\n      - ./backend/database:/app/database\n    restart: unless-stopped\n\n  frontend:\n    build: ./frontend\n    ports:\n      - "3000:80"\n    depends_on:\n      - backend\n    restart: unless-stopped\n' > AgencyReporter_Docker_Final/docker-compose.yml

# Create launcher script
printf '#!/bin/bash\n\necho "Agency Reporter Docker Launcher"\necho "================================"\necho ""\n\ncd "$(dirname "$0")"\n\nif ! docker info > /dev/null 2>&1; then\n    echo "Docker Desktop ist nicht gestartet!"\n    echo "Bitte starten Sie Docker Desktop und versuchen Sie es erneut."\n    exit 1\nfi\n\necho "Starte Agency Reporter..."\ndocker-compose up -d --build\n\necho ""\necho "Warte auf Start (10 Sekunden)..."\nsleep 10\n\necho "Oeffne Browser..."\nopen http://localhost:3000\n\necho ""\necho "Agency Reporter laeuft!"\necho "Zum Stoppen: docker-compose down"\n' > AgencyReporter_Docker_Final/start.sh

# Create stop script
printf '#!/bin/bash\necho "Stoppe Agency Reporter..."\ncd "$(dirname "$0")"\ndocker-compose down\necho "Gestoppt!"\n' > AgencyReporter_Docker_Final/stop.sh

# Create README
printf 'Agency Reporter Docker\n======================\n\nVoraussetzung: Docker Desktop\n\nStarten:\nbash start.sh\n\nStoppen:\nbash stop.sh\n\nURL: http://localhost:3000\n' > AgencyReporter_Docker_Final/README.txt

# Make executable
chmod +x AgencyReporter_Docker_Final/*.sh

# Clean up
find AgencyReporter_Docker_Final -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find AgencyReporter_Docker_Final -name "*.pyc" -delete 2>/dev/null || true
find AgencyReporter_Docker_Final -name ".DS_Store" -delete 2>/dev/null || true
find AgencyReporter_Docker_Final -name "*.log" -delete 2>/dev/null || true
rm -rf AgencyReporter_Docker_Final/backend/venv 2>/dev/null || true
rm -rf AgencyReporter_Docker_Final/backend/database 2>/dev/null || true
rm -rf AgencyReporter_Docker_Final/frontend/node_modules 2>/dev/null || true
rm -f AgencyReporter_Docker_Final/backend/.env 2>/dev/null || true

# Create ZIP
zip -r AgencyReporter_Docker_FINAL.zip AgencyReporter_Docker_Final -x "*.git*"

# Clean up
rm -rf AgencyReporter_Docker_Final

echo "Fertig! AgencyReporter_Docker_FINAL.zip erstellt"