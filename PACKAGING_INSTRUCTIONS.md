# Anleitung zum Verpacken des Projekts für den Kunden

Folge dieser Anleitung, um das AgencyReporter-Projekt für deinen Kunden mit dem MacBook vorzubereiten.

> **Wichtig:** Diese Anwendung wird speziell für einen einzelnen Kunden entwickelt und soll in der finalen Version als Docker-Container oder über ein Shellskript bereitgestellt werden.

## Schritt 1: Vorbereitung des Projekts

1. Stelle sicher, dass die neueste Version des Codes committed ist.
2. Überprüfe, dass alle erforderlichen Abhängigkeiten in den Package-Dateien aufgeführt sind:
   - `backend/requirements.txt`
   - `frontend/package.json`

3. Überprüfe und aktualisiere die Kontaktdaten in:
   - `README.md`
   - `INSTALL_GUIDE.md`

4. Stelle sicher, dass das `setup.sh`-Skript mit LF-Zeilenenden gespeichert ist (nicht CRLF), da der Kunde es auf macOS ausführen wird:
   ```
   # Bei Verwendung von Git
   git config --local core.autocrlf false
   # Oder direkt in deinem Editor die Zeilenenden auf LF umstellen
   ```

## Schritt 2: Projekt packen - Entwicklungsversion

1. Erstelle ein ZIP-Archiv des Projekts:
   ```
   # Ausschließen von node_modules, venv, .git und anderen unnötigen Dateien
   zip -r AgencyReporter.zip . -x "*/node_modules/*" -x "*/venv/*" -x "*.git*" -x "*.DS_Store" -x "*.pyc" -x "__pycache__/*"
   ```

   Unter Windows kannst du alternativ ein ZIP-Archiv mit 7-Zip oder dem Windows-Explorer erstellen und dabei die oben genannten Verzeichnisse ausschließen.

2. Überprüfe das ZIP-Archiv durch Entpacken in einem Testverzeichnis, um sicherzustellen, dass alle wichtigen Dateien enthalten sind.

## Schritt 3: Docker-Container für die Auslieferung (finale Version)

Da die Anwendung für einen einzelnen Kunden entwickelt wird und keine Skalierbarkeit erfordert, ist ein Docker-Container die ideale Auslieferungsmethode:

1. Überprüfe, dass die Docker-Konfiguration in `docker-compose.yml` und `Dockerfile` aktuell ist

2. Baue den Docker-Container:
   ```
   docker build -t agencyreporter:latest .
   ```

3. Teste den Container lokal:
   ```
   docker run -p 3000:3000 -p 8000:8000 agencyreporter:latest
   ```

4. Exportiere den Container für den Kunden:
   ```
   docker save agencyreporter:latest | gzip > agencyreporter-container.tar.gz
   ```

5. Bereite eine einfache Installations-README für den Container vor:
   ```
   # Container installieren:
   docker load < agencyreporter-container.tar.gz
   
   # Container starten:
   docker run -p 3000:3000 -p 8000:8000 agencyreporter:latest
   ```

## Schritt 4: Versand an den Kunden

Je nach Auslieferungsmethode:

**Für die Entwicklungsversion (ZIP-Archiv):**
1. Sende dem Kunden das ZIP-Archiv zusammen mit einem Link zur `INSTALL_GUIDE.md` oder als direkte E-Mail-Anleitung.
2. Stelle sicher, dass der Kunde weiß, wie er:
   - Das ZIP-Archiv entpackt
   - Das Terminal öffnet
   - Das Setup-Skript ausführbar macht und ausführt

**Für die finale Version (Docker-Container):**
1. Sende dem Kunden die Container-Datei (`agencyreporter-container.tar.gz`) zusammen mit der vereinfachten README
2. Stelle sicher, dass auf dem System des Kunden Docker installiert ist
3. Biete an, bei der ersten Installation per Videoanruf zu helfen

## Schritt 5: Vorbereitung für den Support

1. Erstelle eine Kopie der Projektversion, die du dem Kunden geschickt hast
2. Notiere dir eventuelle bekannte Probleme oder Einschränkungen
3. Halte Dokumentation zu den BigQuery-Abfragen bereit, um Fragen beantworten zu können
4. Für Docker-Support:
   - Bereite Docker-spezifische Diagnosebefehle vor
   - Dokumentiere, wie Container-Logs abgerufen werden können

5. Bereite einen Plan für eventuelle Remote-Support-Sitzungen vor:
   - TeamViewer oder ähnliche Tools vorbereiten
   - Terminal-Befehle für häufige Probleme dokumentieren