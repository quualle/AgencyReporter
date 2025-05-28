#!/bin/bash

# Agency Reporter v1.0 - macOS Setup Script
# ==========================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "Agency Reporter v1.0 - Setup für macOS"
echo "======================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Fehler: Dieses Script ist nur für macOS gedacht!${NC}"
    exit 1
fi

# Check for Homebrew
echo "Prüfe Homebrew Installation..."
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Homebrew nicht gefunden. Installiere Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo -e "${GREEN}✓ Homebrew gefunden${NC}"
fi

# Install Python 3.11 if needed
echo ""
echo "Prüfe Python Installation..."
if ! command -v python3.11 &> /dev/null; then
    echo -e "${YELLOW}Python 3.11 wird installiert...${NC}"
    brew install python@3.11
else
    echo -e "${GREEN}✓ Python 3.11 gefunden${NC}"
fi

# Install Node.js if needed
echo ""
echo "Prüfe Node.js Installation..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js wird installiert...${NC}"
    brew install node
else
    echo -e "${GREEN}✓ Node.js gefunden${NC}"
fi

# Create Python virtual environment
echo ""
echo "Erstelle Python Virtual Environment..."
cd backend
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installiere Python-Abhängigkeiten..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
echo ""
echo "Installiere Frontend-Abhängigkeiten..."
cd ../frontend
npm install

# Build frontend
echo ""
echo "Baue Frontend-Anwendung..."
npm run build

# Create necessary directories
echo ""
echo "Erstelle notwendige Verzeichnisse..."
cd ..
mkdir -p backend/database
mkdir -p logs

# Setup environment file
echo ""
echo "Erstelle Umgebungskonfiguration..."
if [ ! -f .env ]; then
    cat > .env << EOL
# Agency Reporter Environment Configuration
# =========================================

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
BIGQUERY_PROJECT_ID=gcpxbixpflegehilfesenioren
BIGQUERY_DATASET=AgencyReporter

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Server Configuration
HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=3000
EOL
    echo -e "${YELLOW}Bitte bearbeiten Sie die .env Datei und fügen Sie Ihren OpenAI API Key ein (falls gewünscht)${NC}"
fi

# Check for Google Cloud credentials
echo ""
if [ ! -f credentials.json ]; then
    echo -e "${YELLOW}WICHTIG: Google Cloud Credentials fehlen!${NC}"
    echo "Bitte platzieren Sie Ihre credentials.json Datei im Hauptverzeichnis."
    echo ""
    
    # Create template
    cat > credentials_template.json << EOL
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your-cert-url"
}
EOL
    echo "Eine Vorlage wurde als credentials_template.json erstellt."
else
    echo -e "${GREEN}✓ Google Cloud Credentials gefunden${NC}"
fi

# Create start script
echo ""
echo "Erstelle Start-Script..."
cat > start_app.sh << 'EOL'
#!/bin/bash

# Agency Reporter - Start Script
# ==============================

echo "Starte Agency Reporter..."

# Check for credentials
if [ ! -f credentials.json ]; then
    echo "FEHLER: credentials.json nicht gefunden!"
    echo "Bitte platzieren Sie Ihre Google Cloud Credentials im Hauptverzeichnis."
    exit 1
fi

# Start backend
echo "Starte Backend-Server..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend läuft mit PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Start frontend
echo "Starte Frontend-Server..."
cd ../frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend läuft mit PID: $FRONTEND_PID"

# Save PIDs
cd ..
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "=========================================="
echo "Agency Reporter wurde erfolgreich gestartet!"
echo "Öffnen Sie http://localhost:3000 in Ihrem Browser"
echo "=========================================="
echo ""
echo "Zum Stoppen verwenden Sie: ./stop_app.sh"
EOL

chmod +x start_app.sh

# Create stop script
cat > stop_app.sh << 'EOL'
#!/bin/bash

# Agency Reporter - Stop Script
# =============================

echo "Stoppe Agency Reporter..."

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "Backend gestoppt"
    fi
    rm .backend.pid
fi

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "Frontend gestoppt"
    fi
    rm .frontend.pid
fi

echo "Agency Reporter wurde gestoppt"
EOL

chmod +x stop_app.sh

# Create update script
cat > update_app.sh << 'EOL'
#!/bin/bash

# Agency Reporter - Update Script
# ===============================

echo "Update Agency Reporter..."

# Stop running application
if [ -f .backend.pid ] || [ -f .frontend.pid ]; then
    echo "Stoppe laufende Anwendung..."
    ./stop_app.sh
    sleep 2
fi

# Pull latest changes
echo "Hole neueste Version..."
git pull origin master

# Update backend dependencies
echo "Aktualisiere Backend-Abhängigkeiten..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
echo "Aktualisiere Frontend-Abhängigkeiten..."
cd ../frontend
npm install
npm run build

cd ..
echo ""
echo "Update abgeschlossen!"
echo "Starten Sie die Anwendung mit: ./start_app.sh"
EOL

chmod +x update_app.sh

# Final message
echo ""
echo -e "${GREEN}=========================================="
echo -e "Installation erfolgreich abgeschlossen!"
echo -e "==========================================${NC}"
echo ""
echo "Nächste Schritte:"
echo "1. Platzieren Sie Ihre credentials.json im Hauptverzeichnis"
echo "2. Bearbeiten Sie die .env Datei (optional für OpenAI)"
echo "3. Starten Sie die Anwendung mit: ./start_app.sh"
echo "4. Öffnen Sie http://localhost:3000 in Ihrem Browser"
echo ""
echo -e "${YELLOW}Hinweis: Beim ersten Start kann das Laden der Daten einige Minuten dauern.${NC}"