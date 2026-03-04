# System Guardian 🛡️

Advanced Process Monitor and System Guardian for Linux/macOS/Windows.

## 🚀 Caracteristici
- **Real-time Tracking**: Monitorizare live a proceselor (PID, CPU, RAM).
- **Smart Alerts**: Notificări când un proces depășește pragurile setate.
- **History Logging**: Salvarea consumului de resurse în fișiere CSV/JSON.
- **Process Control**: Kill, Suspend, Resume direct din interfață.

## 🛠️ Instalare
1. Clonează repository-ul:
   ```bash
   git clone https://github.com/USER/SystemGuardian.git
   cd SystemGuardian
   ```
2. Creează un mediu virtual și instalează dependențele:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Pe Windows: .venv\Scripts\activate
   pip install psutil rich
   ```

## 💻 Utilizare
```bash
python main.py
```

## 🔧 Structura Proiectului
- `main.py`: Punctul de intrare în aplicație.
- `src/`: Codul sursă modularizat.
  - `monitor.py`: Logica de colectare a datelor.
  - `alerts.py`: Sistemul de monitorizare a pragurilor.
  - `logger.py`: Logica de salvare a datelor.
