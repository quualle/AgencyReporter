#!/bin/bash

# Option 1: Kein Watching (keine automatische Neustarts)
# python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 2: Standard-Logging Level erhöhen, um Watch-Meldungen zu unterdrücken
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level error

# Option 3: Watching mit Ausschluss bestimmter Verzeichnisse
# python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-include="*.py" --reload-include="*.html" --reload-include="*.css" --reload-include="*.js" 