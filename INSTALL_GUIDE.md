# Agency Reporter v1.0 - Installationsanleitung

## Willkommen bei Agency Reporter!

Diese Anleitung führt Sie Schritt für Schritt durch die Installation von Agency Reporter auf Ihrem Mac.

## Voraussetzungen

- **macOS** 10.15 (Catalina) oder neuer
- **Internetverbindung** für die Installation
- **Google Cloud Credentials** (erhalten Sie von Ihrem Administrator)
- **2 GB freier Speicherplatz**
- **Chrome, Safari oder Firefox** Browser (aktuellste Version)

## Schritt 1: Vorbereitung

1. **Entpacken Sie die ZIP-Datei**
   - Doppelklicken Sie auf die heruntergeladene `AgencyReporter_v1.0.zip`
   - Ein neuer Ordner `AgencyReporter` wird erstellt

2. **Google Cloud Credentials platzieren**
   - Sie haben eine Datei namens `credentials.json` erhalten
   - Kopieren Sie diese Datei in den `AgencyReporter` Ordner
   - ⚠️ **WICHTIG**: Diese Datei enthält sensible Zugangsdaten - geben Sie sie niemals weiter!

## Schritt 2: Installation

1. **Terminal öffnen**
   - Drücken Sie `CMD + Leertaste`
   - Tippen Sie "Terminal" und drücken Sie Enter

2. **Zum Projektordner navigieren**
   ```bash
   cd ~/Downloads/AgencyReporter
   ```
   (Passen Sie den Pfad an, falls Sie den Ordner woanders entpackt haben)

3. **Installationsskript ausführen**
   ```bash
   ./setup_macos.sh
   ```
   
   Das Skript wird automatisch:
   - Alle notwendigen Programme installieren (Python, Node.js)
   - Die Anwendung einrichten
   - Alle Abhängigkeiten installieren
   
   **Hinweis**: Die Installation kann 10-15 Minuten dauern. Sie werden eventuell nach Ihrem Mac-Passwort gefragt.

4. **OpenAI API Key eintragen (Optional)**
   
   Wenn Sie die KI-Analyse nutzen möchten:
   - Öffnen Sie die Datei `.env` im AgencyReporter-Ordner mit TextEdit
   - Suchen Sie die Zeile `OPENAI_API_KEY=your-openai-api-key-here`
   - Ersetzen Sie `your-openai-api-key-here` mit Ihrem tatsächlichen API Key
   - Speichern und schließen Sie die Datei

## Schritt 3: Anwendung starten

1. **Im Terminal eingeben:**
   ```bash
   ./start_app.sh
   ```

2. **Warten Sie, bis beide Server gestartet sind**
   - Sie sehen Meldungen wie "Backend läuft..." und "Frontend läuft..."
   - Nach etwa 10 Sekunden ist die Anwendung bereit

3. **Browser öffnen**
   - Öffnen Sie Chrome, Safari oder Firefox
   - Gehen Sie zu: **http://localhost:3000**

## Schritt 4: Erste Schritte in der Anwendung

1. **Dashboard öffnen**
   - Die Anwendung startet automatisch auf dem Dashboard
   - Klicken Sie auf "Alle Agenturen laden" um die Daten zu laden
   - Das erste Laden kann 2-3 Minuten dauern

2. **Navigation**
   - Links finden Sie das Hauptmenü
   - Oben rechts können Sie Zeiträume auswählen
   - Alle Widgets sind interaktiv - klicken Sie darauf für Details

## Anwendung beenden

Wenn Sie die Anwendung beenden möchten:

1. **Terminal öffnen** (falls geschlossen)
2. **Zum Projektordner navigieren**
3. **Eingeben:**
   ```bash
   ./stop_app.sh
   ```

## Anwendung erneut starten

Um die Anwendung später wieder zu starten:

1. **Terminal öffnen**
2. **Zum Projektordner navigieren**
3. **Eingeben:**
   ```bash
   ./start_app.sh
   ```
4. **Browser öffnen:** http://localhost:3000

## Updates installieren

Wenn Sie ein Update erhalten:

1. **Terminal öffnen**
2. **Zum Projektordner navigieren**
3. **Eingeben:**
   ```bash
   ./update_app.sh
   ```

## Häufige Probleme

### "Permission denied" Fehler
```bash
chmod +x setup_macos.sh start_app.sh stop_app.sh update_app.sh
```

### Browser zeigt "Seite nicht gefunden"
- Warten Sie 30 Sekunden nach dem Start
- Prüfen Sie, ob beide Server laufen (siehe Terminal-Ausgabe)
- Versuchen Sie http://localhost:3000 (nicht https!)

### "credentials.json nicht gefunden"
- Stellen Sie sicher, dass die Datei im AgencyReporter-Hauptordner liegt
- Der Dateiname muss exakt `credentials.json` sein (Kleinschreibung!)

### Daten werden nicht geladen
- Prüfen Sie Ihre Internetverbindung
- Stellen Sie sicher, dass die credentials.json gültig ist
- Schauen Sie in die Log-Dateien im `logs` Ordner

## Support

Bei Problemen oder Fragen wenden Sie sich bitte an Ihren Administrator oder technischen Ansprechpartner.

## Sicherheitshinweise

- **Teilen Sie niemals Ihre credentials.json Datei**
- **Geben Sie niemals Ihren OpenAI API Key weiter**
- Die Anwendung läuft nur lokal auf Ihrem Computer
- Keine Daten werden nach außen übertragen (außer BigQuery-Abfragen)

---

**Version**: 1.0  
**Stand**: Januar 2025

