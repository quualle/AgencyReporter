# Agency Reporter - Docker Installation

## Einmalige Vorbereitung

1. **Docker Desktop installieren**
   - Download: https://www.docker.com/products/docker-desktop/
   - DMG-Datei öffnen und Docker in Applications ziehen
   - Docker Desktop starten (Wal-Icon in der Menüleiste)

2. **Agency Reporter entpacken**
   - ZIP-Datei entpacken
   - credentials.json ist bereits enthalten

## Tägliche Nutzung

### Starten
1. Docker Desktop starten (falls nicht läuft)
2. Doppelklick auf `START_MIT_DOCKER.sh`
   
   ODER im Terminal:
   ```bash
   cd ~/Desktop/AgencyReporter_Docker
   ./START_MIT_DOCKER.sh
   ```

### Stoppen
- Doppelklick auf `STOP_MIT_DOCKER.sh`

## Vorteile der Docker-Version

✅ Keine Python/Node.js Installation nötig
✅ Keine Homebrew-Probleme
✅ Immer die richtige Umgebung
✅ Einfaches Update durch neues Image
✅ Läuft isoliert vom System

## Bei Problemen

- Docker Desktop muss laufen (Wal in Menüleiste)
- Ports 3000 und 8000 müssen frei sein
- Bei "Cannot connect to Docker daemon": Docker Desktop starten