# AgencyReporter - Installationsanleitung für Mac-Nutzer

> **Hinweis:** Diese Anwendung wird speziell für einen einzelnen Kunden entwickelt und wird in der finalen Version als Docker-Container oder über ein Shellskript bereitgestellt werden. Die folgende Anleitung dient Entwicklungs- und Testzwecken.

## Schritt 1: Das Paket erhalten

1. Lade das ZIP-Archiv von [Link zum Download] herunter oder verwende die dir zugesandte ZIP-Datei.
2. Entpacke das Archiv auf deinem Mac in ein Verzeichnis deiner Wahl.

## Schritt 2: Installation und Start

1. Öffne das Terminal auf deinem Mac:
   - Drücke `Cmd + Leertaste`, tippe "Terminal" ein und drücke Enter
   
2. Navigiere zum entpackten Verzeichnis:
   ```
   cd Pfad/zum/entpackten/AgencyReporter
   ```
   Hinweis: Du kannst den Pfad auch einfach erstellen, indem du den Ordner aus dem Finder ins Terminal ziehst.

3. Mache das Setup-Skript ausführbar:
   ```
   chmod +x setup.sh
   ```

4. Führe das Setup-Skript aus:
   ```
   ./setup.sh
   ```

5. Das Skript:
   - Prüft, ob die benötigten Programme installiert sind
   - Installiert Homebrew (wenn nicht vorhanden)
   - Installiert Python und Node.js (wenn nicht vorhanden)
   - Richtet das Backend und Frontend ein
   - Startet beide Server

## Schritt 3: Die Anwendung verwenden

Nachdem das Setup-Skript erfolgreich durchgelaufen ist, kannst du die Anwendung in deinem Browser öffnen:

- **Frontend:** http://localhost:3000
- **API-Dokumentation:** http://localhost:8000/docs

Um die Anwendung zu beenden, drücke `Strg+C` im Terminal-Fenster.

## Schritt 4: Docker-Container (zukünftige Auslieferungsmethode)

Die finale Version dieser Anwendung wird als Docker-Container bereitgestellt, der alle Abhängigkeiten enthält und keine separate Installation von Python oder Node.js erfordert. Die Installation wird dann mit wenigen Befehlen möglich sein:

```
docker pull [container-name]
docker run -p 3000:3000 -p 8000:8000 [container-name]
```

Diese containerisierte Version wird in einer zukünftigen Aktualisierung verfügbar sein.

## Fehlerbehebung

Sollte das automatische Setup nicht funktionieren, folge der manuellen Installationsanleitung in der `README.md` im Projektverzeichnis.

