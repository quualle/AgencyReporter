# Anleitung für Sie (Entwickler)

## Package erstellen und versenden

### 1. Package erstellen
```bash
cd /Users/marcoheer/Desktop/privat/Programmierung/AgencyReporter_V1.0
./package_for_client.sh
```

Falls das Script Probleme macht:
```bash
bash package_for_client.sh
```

### 2. Ergebnis
Sie erhalten: **AgencyReporter_v1.0_Complete.zip** (ca. 2,6 MB)

### 3. An Chef senden
- Die ZIP-Datei per E-Mail, WeTransfer oder USB-Stick übergeben
- KEINE weiteren Dateien nötig (credentials.json ist bereits enthalten!)

## Bei Updates

### Code ändern
1. Änderungen im Code vornehmen
2. Frontend neu bauen: `cd frontend && npm run build`
3. Neues Package erstellen: `./package_for_client.sh`

### GitHub
```bash
git add .
git commit -m "Beschreibung der Änderungen"
git push origin master
```

## Wichtige Pfade
- Projekt: `/Users/marcoheer/Desktop/privat/Programmierung/AgencyReporter_V1.0`
- Package-Script: `package_for_client.sh`
- Fertiges Package: `AgencyReporter_v1.0_Complete.zip`

## Support für Chef
Falls Ihr Chef Probleme hat:
1. Prüfen ob macOS 10.15 oder neuer
2. Prüfen ob Internetverbindung vorhanden
3. Terminal-Output prüfen lassen
4. Notfalls TeamViewer/Screensharing