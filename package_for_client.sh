#!/bin/bash

# Agency Reporter v1.0 - All-in-One Client Packaging Script
# =========================================================

set -e

echo "======================================"
echo "Agency Reporter v1.0 - Client Package"
echo "======================================"
echo ""

# Define package name
PACKAGE_NAME="AgencyReporter_v1.0_Complete"
PACKAGE_DIR="./${PACKAGE_NAME}"

# Clean up old package if exists
if [ -d "$PACKAGE_DIR" ]; then
    echo "Removing old package directory..."
    rm -rf "$PACKAGE_DIR"
fi

# Create package directory
echo "Creating package directory..."
mkdir -p "$PACKAGE_DIR"

# Copy necessary files
echo "Copying application files..."
cp -r backend "$PACKAGE_DIR/"
cp -r frontend "$PACKAGE_DIR/"

# Copy credentials if exists
if [ -f "credentials.json" ]; then
    echo "Including credentials.json..."
    cp credentials.json "$PACKAGE_DIR/"
else
    echo "WARNING: credentials.json not found!"
    echo "Please ensure credentials.json exists before packaging."
    exit 1
fi

# Pre-build frontend for faster startup
echo "Pre-building frontend..."
cd frontend
npm install
npm run build
cd ..
cp -r frontend/build "$PACKAGE_DIR/frontend/"

# Create optimized setup script
echo "Creating optimized setup script..."
cat > "$PACKAGE_DIR/setup_and_run.sh" << 'EOL'
#!/bin/bash

# Agency Reporter v1.0 - One-Click Setup & Run
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "Agency Reporter v1.0 - Setup & Start"
echo "======================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Fehler: Dieses Script ist nur für macOS gedacht!${NC}"
    exit 1
fi

# Check for Homebrew (silently install if needed)
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Installiere Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" < /dev/null
fi

# Install Python 3.11 if needed (silently)
if ! command -v python3.11 &> /dev/null; then
    echo -e "${YELLOW}Installiere Python 3.11...${NC}"
    brew install python@3.11 > /dev/null 2>&1
fi

# Create Python virtual environment
echo "Konfiguriere Python-Umgebung..."
cd backend
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installiere Backend-Abhängigkeiten..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Create necessary directories
cd ..
mkdir -p backend/database
mkdir -p logs

# Setup environment file
if [ ! -f .env ]; then
    cat > .env << EOF
# Agency Reporter Environment Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
BIGQUERY_PROJECT_ID=gcpxbixpflegehilfesenioren
BIGQUERY_DATASET=AgencyReporter
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=3000
EOF
fi

# Start backend
echo ""
echo "Starte Backend-Server..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend (using pre-built version)
echo "Starte Frontend-Server..."
cd ../frontend
npx serve -s build -l 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Save PIDs
cd ..
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait a moment
sleep 3

# Open browser automatically
echo ""
echo -e "${GREEN}=========================================="
echo -e "Agency Reporter wurde erfolgreich gestartet!"
echo -e "==========================================${NC}"
echo ""

# Try to open browser
if command -v open &> /dev/null; then
    open http://localhost:3000
    echo "Browser wird automatisch geöffnet..."
else
    echo "Öffnen Sie http://localhost:3000 in Ihrem Browser"
fi

echo ""
echo "Die Anwendung läuft im Hintergrund."
echo "Zum Beenden drücken Sie Ctrl+C oder schließen Sie dieses Fenster."
echo ""

# Keep script running
trap 'echo "Beende Agency Reporter..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT TERM
wait
EOL

chmod +x "$PACKAGE_DIR/setup_and_run.sh"

# Create simple stop script
cat > "$PACKAGE_DIR/stop.sh" << 'EOL'
#!/bin/bash
echo "Stoppe Agency Reporter..."
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null
    rm .backend.pid
fi
if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null
    rm .frontend.pid
fi
echo "Agency Reporter wurde gestoppt."
EOL

chmod +x "$PACKAGE_DIR/stop.sh"

# Create minimal README
cat > "$PACKAGE_DIR/README.txt" << EOL
Agency Reporter v1.0
==================

SCHNELLSTART:
1. Doppelklicken Sie auf "setup_and_run.sh"
   ODER
   Terminal öffnen und eingeben: ./setup_and_run.sh

Das war's! Die Anwendung startet automatisch.

Zum Beenden: Fenster schließen oder ./stop.sh ausführen

Bei Problemen: Kontaktieren Sie Ihren Administrator.
EOL

# Remove unnecessary files
echo "Cleaning up..."
find "$PACKAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
rm -rf "$PACKAGE_DIR/backend/venv" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/backend/database" 2>/dev/null || true
rm -f "$PACKAGE_DIR/backend/.env" 2>/dev/null || true

# Create ZIP file
echo "Creating ZIP package..."
zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_DIR" -x "*.git*" "*/node_modules/*"

# Clean up temporary directory
rm -rf "$PACKAGE_DIR"

echo ""
echo "✅ All-in-One Package erstellt: ${PACKAGE_NAME}.zip"
echo ""
echo "Dieses Package enthält:"
echo "- Die komplette Anwendung"
echo "- Alle Credentials"
echo "- Pre-built Frontend"
echo "- One-Click Setup & Start"
echo ""
echo "Der Nutzer muss nur:"
echo "1. ZIP entpacken"
echo "2. setup_and_run.sh ausführen"
echo ""
echo "Fertig! 🎉"