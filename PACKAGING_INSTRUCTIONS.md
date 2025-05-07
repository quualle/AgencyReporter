# Anleitung zum Verpacken des Projekts für den Kunden

Folge dieser Anleitung, um das AgencyReporter-Projekt für deinen Kunden mit dem MacBook vorzubereiten.

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

## Schritt 2: Projekt packen

1. Erstelle ein ZIP-Archiv des Projekts:
   ```
   # Ausschließen von node_modules, venv, .git und anderen unnötigen Dateien
   zip -r AgencyReporter.zip . -x "*/node_modules/*" -x "*/venv/*" -x "*.git*" -x "*.DS_Store" -x "*.pyc" -x "__pycache__/*"
   ```

   Unter Windows kannst du alternativ ein ZIP-Archiv mit 7-Zip oder dem Windows-Explorer erstellen und dabei die oben genannten Verzeichnisse ausschließen.

2. Überprüfe das ZIP-Archiv durch Entpacken in einem Testverzeichnis, um sicherzustellen, dass alle wichtigen Dateien enthalten sind.

## Schritt 3: Versand an den Kunden

1. Sende dem Kunden das ZIP-Archiv zusammen mit einem Link zur `INSTALL_GUIDE.md` oder als direkte E-Mail-Anleitung.

2. Stelle sicher, dass der Kunde weiß, wie er:
   - Das ZIP-Archiv entpackt
   - Das Terminal öffnet
   - Das Setup-Skript ausführbar macht und ausführt

3. Biete dem Kunden an, bei der ersten Installation per Videoanruf zu helfen, falls Probleme auftreten sollten.

## Schritt 4: Vorbereitung für den Support

1. Erstelle eine Kopie der Projektversion, die du dem Kunden geschickt hast
2. Notiere dir eventuelle bekannte Probleme oder Einschränkungen
3. Halte Dokumentation zu den BigQuery-Abfragen bereit, um Fragen beantworten zu können

4. Bereite einen Plan für eventuelle Remote-Support-Sitzungen vor:
   - TeamViewer oder ähnliche Tools vorbereiten
   - Terminal-Befehle für häufige Probleme dokumentieren 