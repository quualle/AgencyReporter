#!/bin/bash

# AgencyReporter Docker-Deployment-Skript
# Dieses Skript richtet die AgencyReporter-Anwendung ein und startet sie

echo "🚀 AgencyReporter Docker-Deployment wird gestartet..."

# Prüfen, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo "❌ Docker ist nicht installiert."
    echo "Bitte installieren Sie Docker: https://docs.docker.com/get-docker/"
    exit 1
else
    echo "✅ Docker ist bereits installiert."
fi

# Prüfen, ob Docker Compose installiert ist
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose ist nicht installiert."
    echo "Bitte installieren Sie Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
else
    echo "✅ Docker Compose ist bereits installiert."
fi

# Prüfen, ob credentials.json existiert
if [ ! -f "credentials.json" ]; then
    echo "⚠️ WARNUNG: credentials.json wurde nicht gefunden!"
    echo "Diese Datei wird für die BigQuery-Verbindung benötigt."
    read -p "Möchten Sie trotzdem fortfahren? (j/n): " continue_without_credentials
    if [ "$continue_without_credentials" != "j" ]; then
        echo "🛑 Deployment abgebrochen."
        exit 1
    fi
fi

# Prüfen, ob .env existiert oder erstellt werden muss
if [ ! -f ".env" ]; then
    echo "⚠️ Keine .env-Datei gefunden. Eine einfache .env-Datei wird erstellt."
    
    cat > .env << EOF
# BigQuery settings
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
BIGQUERY_PROJECT_ID=gcpxbixpflegehilfesenioren
BIGQUERY_DATASET=AgencyReporter

# OpenAI settings (Falls benötigt)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
EOF
    
    echo "✅ .env-Datei wurde erstellt. Bitte überprüfen und anpassen, falls nötig."
    echo "   Insbesondere den OPENAI_API_KEY, falls dieser benötigt wird."
fi

# Container stoppen, falls sie bereits laufen
echo "🛑 Stoppe eventuell laufende Container..."
docker-compose down

# Container bauen und starten
echo "🔨 Docker-Container werden gebaut und gestartet..."
docker-compose build
docker-compose up -d

# Status prüfen
if docker-compose ps | grep -q "Up"; then
    echo "✅ Container wurden erfolgreich gestartet!"
    echo ""
    echo "📊 Zugriff auf die Anwendung:"
    echo "- Frontend: http://localhost"
    echo "- Backend API: http://localhost:8000"
    echo ""
    echo "💻 Container-Verwaltungsbefehle:"
    echo "- Logs anzeigen: docker-compose logs"
    echo "- Container stoppen: docker-compose down"
    echo "- Container neustarten: docker-compose restart"
    echo "- Shell-Zugriff: docker exec -it agency-reporter-backend sh"
else
    echo "❌ Es gab ein Problem beim Starten der Container."
    echo "Bitte überprüfen Sie die Logs mit 'docker-compose logs'."
fi 