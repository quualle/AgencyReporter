#!/bin/bash

# Create Docker Package
echo "Erstelle Docker-Package..."

PACKAGE_NAME="AgencyReporter_Docker"
rm -rf $PACKAGE_NAME

mkdir -p $PACKAGE_NAME
cp -r backend frontend $PACKAGE_NAME/
cp credentials.json $PACKAGE_NAME/
cp docker-compose.simple.yml $PACKAGE_NAME/docker-compose.simple.yml
cp START_MIT_DOCKER.sh STOP_MIT_DOCKER.sh DOCKER_ANLEITUNG.md $PACKAGE_NAME/

# Clean up
find $PACKAGE_NAME -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find $PACKAGE_NAME -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
find $PACKAGE_NAME -name ".env" -delete 2>/dev/null || true

# Create ZIP
zip -r ${PACKAGE_NAME}.zip $PACKAGE_NAME -x "*.git*"
rm -rf $PACKAGE_NAME

echo "✅ Docker-Package erstellt: ${PACKAGE_NAME}.zip"
echo ""
echo "Der Kunde muss nur:"
echo "1. Docker Desktop installieren"
echo "2. ZIP entpacken"
echo "3. START_MIT_DOCKER.sh ausführen"