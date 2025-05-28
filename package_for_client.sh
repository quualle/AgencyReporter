#!/bin/bash

# Agency Reporter v1.0 - Client Packaging Script
# ==============================================

set -e

echo "======================================"
echo "Agency Reporter v1.0 - Client Package"
echo "======================================"
echo ""

# Define package name
PACKAGE_NAME="AgencyReporter_v1.0"
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
cp setup_macos.sh "$PACKAGE_DIR/"
cp INSTALL_GUIDE.md "$PACKAGE_DIR/"

# Create credentials template
echo "Creating credentials template..."
cat > "$PACKAGE_DIR/credentials_template.json" << EOL
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

# Create a README for the package
cat > "$PACKAGE_DIR/README.txt" << EOL
Agency Reporter v1.0
==================

Wichtige Hinweise:
1. Bitte lesen Sie zuerst die INSTALL_GUIDE.md
2. Platzieren Sie Ihre credentials.json im Hauptordner
3. Führen Sie ./setup_macos.sh aus für die Installation

Bei Fragen wenden Sie sich an Ihren Administrator.
EOL

# Remove unnecessary files
echo "Cleaning up unnecessary files..."
find "$PACKAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
rm -rf "$PACKAGE_DIR/backend/venv" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/frontend/node_modules" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/frontend/build" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/backend/database" 2>/dev/null || true
rm -f "$PACKAGE_DIR/backend/.env" 2>/dev/null || true

# Create ZIP file
echo "Creating ZIP package..."
zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_DIR" -x "*.git*"

# Clean up temporary directory
rm -rf "$PACKAGE_DIR"

echo ""
echo "✅ Package erstellt: ${PACKAGE_NAME}.zip"
echo ""
echo "Nächste Schritte:"
echo "1. Senden Sie ${PACKAGE_NAME}.zip an Ihren Kunden"
echo "2. Senden Sie die credentials.json separat (sicher!)"
echo "3. Optional: OpenAI API Key bereitstellen"
echo ""
echo "Der Kunde muss nur:"
echo "1. ZIP entpacken"
echo "2. credentials.json hinzufügen"
echo "3. ./setup_macos.sh ausführen"