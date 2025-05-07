#!/bin/bash

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Log-Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

log_error() {
    echo -e "${RED}[FEHLER]${NC} $1"
}

# Überprüfen, ob Homebrew installiert ist
check_homebrew() {
    log_info "Überprüfe ob Homebrew installiert ist..."
    if ! command -v brew &> /dev/null; then
        log_warn "Homebrew ist nicht installiert. Installiere jetzt..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [ $? -ne 0 ]; then
            log_error "Homebrew konnte nicht installiert werden. Bitte installiere es manuell von https://brew.sh"
            exit 1
        fi
    else
        log_info "Homebrew ist bereits installiert ✓"
    fi
}

# Überprüfen, ob Python installiert ist
check_python() {
    log_info "Überprüfe Python-Installation..."
    if ! command -v python3 &> /dev/null; then
        log_warn "Python ist nicht installiert. Installiere Python..."
        brew install python
        if [ $? -ne 0 ]; then
            log_error "Python konnte nicht installiert werden. Bitte installiere Python 3.8+ manuell."
            exit 1
        fi
    else
        python_version=$(python3 --version | cut -d' ' -f2)
        log_info "Python $python_version ist installiert ✓"
    fi
}

# Überprüfen, ob Node.js installiert ist
check_nodejs() {
    log_info "Überprüfe Node.js-Installation..."
    if ! command -v node &> /dev/null; then
        log_warn "Node.js ist nicht installiert. Installiere Node.js..."
        brew install node
        if [ $? -ne 0 ]; then
            log_error "Node.js konnte nicht installiert werden. Bitte installiere Node.js manuell."
            exit 1
        fi
    else
        node_version=$(node --version)
        log_info "Node.js $node_version ist installiert ✓"
    fi
}

# Python-Abhängigkeiten installieren
setup_backend() {
    log_info "Installiere Python-Abhängigkeiten..."
    cd backend || { log_error "Backend-Verzeichnis nicht gefunden"; exit 1; }
    
    # Virtuelle Umgebung erstellen
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        log_error "Virtuelle Umgebung konnte nicht erstellt werden."
        exit 1
    fi
    
    # Virtuelle Umgebung aktivieren
    source venv/bin/activate
    
    # Requirements installieren
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        log_error "Backend-Abhängigkeiten konnten nicht installiert werden."
        exit 1
    fi
    
    log_info "Backend-Setup abgeschlossen ✓"
    cd ..
}

# Frontend-Abhängigkeiten installieren
setup_frontend() {
    log_info "Installiere Frontend-Abhängigkeiten..."
    cd frontend || { log_error "Frontend-Verzeichnis nicht gefunden"; exit 1; }
    
    # NPM-Pakete installieren
    npm install
    if [ $? -ne 0 ]; then
        log_error "Frontend-Abhängigkeiten konnten nicht installiert werden."
        exit 1
    fi
    
    log_info "Frontend-Setup abgeschlossen ✓"
    cd ..
}

# Backend starten
start_backend() {
    log_info "Starte Backend-Server..."
    cd backend || { log_error "Backend-Verzeichnis nicht gefunden"; exit 1; }
    
    # Virtuelle Umgebung aktivieren
    source venv/bin/activate
    
    # Server im Hintergrund starten
    python -m app.main &
    BACKEND_PID=$!
    
    # Prüfen, ob der Server erfolgreich gestartet wurde
    sleep 3
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        log_error "Backend-Server konnte nicht gestartet werden."
        exit 1
    fi
    
    log_info "Backend-Server läuft unter http://localhost:8000 ✓"
    cd ..
}

# Frontend starten
start_frontend() {
    log_info "Starte Frontend-Server..."
    cd frontend || { log_error "Frontend-Verzeichnis nicht gefunden"; exit 1; }
    
    # Entwicklungsserver im Hintergrund starten
    npm run dev &
    FRONTEND_PID=$!
    
    # Prüfen, ob der Server erfolgreich gestartet wurde
    sleep 5
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        log_error "Frontend-Server konnte nicht gestartet werden."
        exit 1
    fi
    
    log_info "Frontend-Server läuft unter http://localhost:3000 ✓"
    cd ..
}

# Anweisungen anzeigen
show_instructions() {
    echo ""
    echo "=============================================="
    echo "🚀 AgencyReporter ist gestartet!"
    echo "=============================================="
    echo ""
    echo "Du kannst die Anwendung unter folgenden URLs aufrufen:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000/docs"
    echo ""
    echo "Um die Anwendung zu beenden, drücke STRG+C"
    echo ""
    echo "Viel Spaß beim Testen! 🎉"
    echo "=============================================="
}

# Anwendung sauber beenden
cleanup() {
    log_info "Beende Anwendung..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    log_info "Anwendung wurde beendet."
    exit 0
}

# Trap für CTRL+C
trap cleanup INT

# Hauptfunktion
main() {
    echo "==== AgencyReporter Setup ===="
    
    # Grundvoraussetzungen prüfen
    check_homebrew
    check_python
    check_nodejs
    
    # Anwendung einrichten
    setup_backend
    setup_frontend
    
    # Anwendung starten
    start_backend
    start_frontend
    
    # Anweisungen anzeigen
    show_instructions
    
    # Warten (damit das Skript nicht beendet wird)
    wait
}

# Starte das Skript
main 