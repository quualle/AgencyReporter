#!/bin/bash

# Agency Reporter - Docker Start
# ==============================

echo "======================================"
echo "Agency Reporter v1.0 - Docker Edition"
echo "======================================"
echo ""

# Prüfe ob Docker läuft
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker Desktop ist nicht gestartet!"
    echo ""
    echo "Bitte starten Sie Docker Desktop und versuchen Sie es erneut."
    echo "Falls Docker nicht installiert ist: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo "✅ Docker läuft"
echo ""
echo "Starte Agency Reporter..."

# Container starten
docker-compose -f docker-compose.simple.yml up -d --build

# Warte kurz
sleep 10

# Browser öffnen
echo ""
echo "Öffne Browser..."
open http://localhost:3000

echo ""
echo "=========================================="
echo "✅ Agency Reporter läuft!"
echo "=========================================="
echo ""
echo "Zugriff unter: http://localhost:3000"
echo ""
echo "Zum Stoppen: ./STOP_MIT_DOCKER.sh"