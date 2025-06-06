Agency Reporter - Einfache Installation
  =======================================

  1. ZIP-Datei auf den Desktop entpacken

  2. Terminal öffnen (CMD + Leertaste → "Terminal")

  3. Diese Befehle der Reihe nach eingeben:

  cd ~/Desktop/AgencyReporter_Docker_FERTIG
  perl -pi -e 's/\r\n|\r/\n/g' start.sh stop.sh
  chmod +x start.sh stop.sh
  bash start.sh

  4. Browser öffnet sich automatisch

  FERTIG!

  Tägliche Nutzung:
  - Docker Desktop starten
  - Terminal: cd ~/Desktop/AgencyReporter_Docker_FERTIG
  - Terminal: bash start.sh

  Stoppen:
  - Terminal: bash stop.sh

  Hinweise:
  - Beim ersten Start dauert es ca. 5 Minuten (Docker baut die Container)
  - Danach startet die Anwendung in wenigen Sekunden
  - URL ist immer: http://localhost:3000
