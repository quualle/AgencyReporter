# Agency Reporter - Docker Schnellstart

## Für Sie (zum Testen):

```bash
cd ~/Desktop/AgencyReporter_Docker_Ready

# Zeilenenden fixen
perl -pi -e 's/\r\n|\r/\n/g' start.command stop.command
chmod +x start.command stop.command

# Starten
./start.command
```

## Für Ihren Chef (funktioniert IMMER):

### Option 1: Terminal-Befehle
```bash
cd ~/Desktop/AgencyReporter_Docker_Ready
bash start.command
```

### Option 2: Docker direkt
```bash
cd ~/Desktop/AgencyReporter_Docker_Ready
docker-compose up -d --build
open http://localhost:3000
```

### Stoppen:
```bash
docker-compose down
```

## Warum das Problem auftritt:
Die .command Dateien haben Windows-Zeilenenden (CRLF) statt Unix-Zeilenenden (LF).

## Dauerhafte Lösung:
Ich erstelle ein finales Package mit einem Shell-Script, das diese Probleme automatisch behebt.