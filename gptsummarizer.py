import os
import json
import tkinter as tk
from tkinter import messagebox
import threading
import keyboard  # Globaler Hotkey-Listener

# Pfad zum Projektverzeichnis anpassen
PROJECT_DIR = r"C:\Users\marco\Desktop\Programmierung\TradeBot_Backtester"
# Datei zum Speichern des Zustands (Reihenfolge und Auswahl)
STATE_FILE = "file_combiner_state.json"

class FileCombinerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project File Combiner")
        self.geometry("800x600")
        
        # Mapping: file_path -> {"var": BooleanVar, "frame": Frame}
        self.file_entries = {}
        # Liste zur Steuerung der Reihenfolge der Scripte
        self.user_order = []
        
        self.create_widgets()
        self.load_files()
        
        # Lokale Tastenkombinationen (funktionieren, wenn das Fenster aktiv ist)
        self.bind_all("<Control-Key-1>", self.copy_selected_files_to_clipboard)
        self.bind_all("<Control-Key-2>", self.combine_selected_files)
        
        # Bind für den globalen Hotkey, der von keyboard ausgelöst wird
        self.bind("<<GlobalCtrl1>>", self.copy_selected_files_to_clipboard)
        
        # Starte den globalen Hotkey-Listener
        self.setup_global_hotkeys()
        
        # Zustand beim Schließen speichern
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_global_hotkeys(self):
        def listen_hotkeys():
            # Registriere globalen Hotkey für STRG+1, der ein benutzerdefiniertes Event auslöst
            keyboard.add_hotkey('ctrl+1', lambda: self.event_generate("<<GlobalCtrl1>>"))
            keyboard.wait()  # Hält den Thread am Laufen
        thread = threading.Thread(target=listen_hotkeys, daemon=True)
        thread.start()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable Area für die Einträge
        self.canvas = tk.Canvas(frame)
        self.scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(fill="x", padx=10, pady=10)

        self.btn_select_all = tk.Button(self.btn_frame, text="Alle auswählen", command=self.select_all)
        self.btn_select_all.pack(side="left", padx=5)

        self.btn_deselect_all = tk.Button(self.btn_frame, text="Alle abwählen", command=self.deselect_all)
        self.btn_deselect_all.pack(side="left", padx=5)

        self.btn_copy_clipboard = tk.Button(
            self.btn_frame, 
            text="In Zwischenablage (STRG+1)", 
            command=self.copy_selected_files_to_clipboard
        )
        self.btn_copy_clipboard.pack(side="right", padx=5)

        self.btn_combine = tk.Button(
            self.btn_frame, 
            text="Ausgewählte kombinieren (STRG+2)", 
            command=self.combine_selected_files
        )
        self.btn_combine.pack(side="right", padx=5)

    def create_file_entry(self, file_path, selected=True):
        """
        Erzeugt einen Eintrag (Frame) für ein Script, inklusive Checkbutton und Up/Down-Buttons.
        """
        entry_frame = tk.Frame(self.scrollable_frame, bd=1, relief="groove", padx=5, pady=2)
        var = tk.BooleanVar(value=selected)
        
        # Checkbutton mit Dateinamen
        cb = tk.Checkbutton(entry_frame, text=os.path.basename(file_path), variable=var, anchor="w", justify="left")
        cb.pack(side="left", fill="x", expand=True)
        
        # Buttons zum Re-Ordnen
        btn_up = tk.Button(entry_frame, text="↑", command=lambda fp=file_path: self.move_up(fp), width=3)
        btn_up.pack(side="right", padx=2)
        btn_down = tk.Button(entry_frame, text="↓", command=lambda fp=file_path: self.move_down(fp), width=3)
        btn_down.pack(side="right")
        
        return {"var": var, "frame": entry_frame}

    def load_state(self):
        """Lädt den gespeicherten Zustand (Reihenfolge und Auswahl) aus STATE_FILE, falls vorhanden."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden des Zustands: {e}")
        return {}

    def save_state(self):
        """Speichert die aktuelle Reihenfolge und Auswahl in STATE_FILE."""
        state = {
            "order": self.user_order,
            "selections": {fp: self.file_entries[fp]["var"].get() for fp in self.user_order}
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern des Zustands: {e}")

    def load_files(self):
        """
        Lädt alle .py-Dateien aus PROJECT_DIR beim Programmstart und übernimmt
        gespeicherte Reihenfolge und Auswahl, sofern vorhanden.
        """
        state = self.load_state()
        # Dateien im Verzeichnis ermitteln
        all_files = []
        for entry in os.scandir(PROJECT_DIR):
            if entry.is_file() and entry.name.lower().endswith(".py"):
                all_files.append(entry.path)
                
        # Bestimme die Reihenfolge: Zuerst die aus dem gespeicherten Zustand,
        # dann alle neuen Dateien alphabetisch hinzufügen.
        ordered_files = []
        if "order" in state:
            for fp in state["order"]:
                if fp in all_files:
                    ordered_files.append(fp)
            # Hänge neue Dateien an
            for fp in sorted(all_files):
                if fp not in ordered_files:
                    ordered_files.append(fp)
        else:
            ordered_files = sorted(all_files)
        
        # Erzeuge die UI-Einträge und setze die Auswahl gemäß gespeichertem Zustand oder default True.
        for file_path in ordered_files:
            selected = state.get("selections", {}).get(file_path, True)
            entry = self.create_file_entry(file_path, selected=selected)
            self.file_entries[file_path] = entry
            self.user_order.append(file_path)
            entry["frame"].pack(fill="x", anchor="w", pady=1)

    def refresh_files(self):
        """
        Aktualisiert die Dateiliste:
         - Entfernt nicht mehr vorhandene Dateien.
         - Fügt neu hinzugekommene Dateien (am Ende) hinzu.
         - Beibehaltung der bisherigen Reihenfolge für vorhandene Dateien.
        """
        current_files = set()
        for entry in os.scandir(PROJECT_DIR):
            if entry.is_file() and entry.name.lower().endswith(".py"):
                current_files.add(entry.path)
        
        # Entferne nicht mehr existierende Dateien
        for file_path in self.user_order.copy():
            if file_path not in current_files:
                self.file_entries[file_path]["frame"].destroy()
                del self.file_entries[file_path]
                self.user_order.remove(file_path)
        
        # Füge neue Dateien hinzu
        for file_path in current_files:
            if file_path not in self.file_entries:
                entry = self.create_file_entry(file_path, selected=True)
                self.file_entries[file_path] = entry
                self.user_order.append(file_path)
        
        self.update_file_display()

    def update_file_display(self):
        """Ordnet die UI-Elemente in der scrollbaren Fläche gemäß self.user_order."""
        for file_path in self.user_order:
            self.file_entries[file_path]["frame"].pack_forget()
            self.file_entries[file_path]["frame"].pack(fill="x", anchor="w", pady=1)

    def move_up(self, file_path):
        """Verschiebt den Eintrag in der Reihenfolge um eine Position nach oben."""
        index = self.user_order.index(file_path)
        if index > 0:
            self.user_order[index], self.user_order[index - 1] = self.user_order[index - 1], self.user_order[index]
            self.update_file_display()

    def move_down(self, file_path):
        """Verschiebt den Eintrag in der Reihenfolge um eine Position nach unten."""
        index = self.user_order.index(file_path)
        if index < len(self.user_order) - 1:
            self.user_order[index], self.user_order[index + 1] = self.user_order[index + 1], self.user_order[index]
            self.update_file_display()

    def select_all(self):
        for file_path in self.user_order:
            self.file_entries[file_path]["var"].set(True)

    def deselect_all(self):
        for file_path in self.user_order:
            self.file_entries[file_path]["var"].set(False)

    def copy_selected_files_to_clipboard(self, event=None):
        # Aktualisiere die Dateiliste, um Änderungen zu berücksichtigen
        self.refresh_files()
        
        selected_files = [fp for fp in self.user_order if self.file_entries[fp]["var"].get()]
        if not selected_files:
            messagebox.showwarning("Keine Auswahl", "Es wurden keine Dateien ausgewählt.")
            return

        combined_content = []
        for file_path in selected_files:
            combined_content.append(f"----- {os.path.basename(file_path)} -----\n")
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
                    content = infile.read()
                combined_content.append(content + "\n\n")
            except Exception as e:
                combined_content.append(f"Fehler beim Lesen der Datei: {e}\n\n")

        total_text = "".join(combined_content)
        self.clipboard_clear()
        self.clipboard_append(total_text)
        messagebox.showinfo("Fertig", "Ausgewählte Dateien wurden in den Zwischenspeicher kopiert.")

    def combine_selected_files(self, event=None):
        selected_files = [fp for fp in self.user_order if self.file_entries[fp]["var"].get()]
        if not selected_files:
            messagebox.showwarning("Keine Auswahl", "Es wurden keine Dateien ausgewählt.")
            return

        summary_file = os.path.join(PROJECT_DIR, "combined_summary.txt")
        try:
            with open(summary_file, "w", encoding="utf-8") as outfile:
                for file_path in selected_files:
                    outfile.write(f"----- {os.path.basename(file_path)} -----\n")
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
                            content = infile.read()
                        outfile.write(content + "\n\n")
                    except Exception as e:
                        outfile.write(f"Fehler beim Lesen der Datei: {e}\n\n")
            messagebox.showinfo("Fertig", f"Die Dateien wurden erfolgreich in '{summary_file}' zusammengefasst.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Zusammenfassung: {e}")

    def on_closing(self):
        """Speichert den Zustand und schließt das Programm."""
        self.save_state()
        self.destroy()

if __name__ == "__main__":
    app = FileCombinerApp()
    app.mainloop()
