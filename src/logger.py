import csv
import os
from datetime import datetime

class HistoryLogger:
    def __init__(self, filename="history_log.csv"):
        self.filename = filename
        self._init_file()

    def _init_file(self):
        """Inițializează header-ul fișierului dacă acesta nu există."""
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "PID", "Name", "CPU %", "Memory %", "Status"])

    def log_processes(self, processes):
        """Salvează datele proceselor curente."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for proc in processes[:10]: # Logăm doar primele 10 (cele mai consumatoare)
                writer.writerow([
                    timestamp,
                    proc['pid'],
                    proc['name'],
                    f"{proc['cpu_percent']:.1f}",
                    f"{proc['memory_percent']:.1f}",
                    proc['status']
                ])
