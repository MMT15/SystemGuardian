# System Guardian 🛡️

**System Guardian** este un utilitar avansat de monitorizare și gestionare a proceselor pentru sisteme Linux, conceput pentru a oferi o vizibilitate totală asupra resurselor hardware și securității software. Proiectul include atât o interfață grafică (GUI) modernă, cât și o interfață puternică în linia de comandă (CLI).

## 🚀 Caracteristici Principale

### 🖥️ Interfață Grafică (GUI) - PyQt6
- **Real-time Dashboard**: Monitorizare live pentru CPU și RAM cu bare de progres interactive.
- **Sticky Selection**: Posibilitatea de a "ancora" un proces selectat; acesta rămâne vizibil în tabel chiar dacă nu mai este în Top 30.
- **Search & Filter**: Filtrare instantanee a proceselor după nume.
- **One-Click Actions**: Butoane dedicate pentru vizualizarea detaliilor sau oprirea proceselor (Kill).

### 💻 Interfață CLI 
- **Live Monitoring**: Tabel colorat și organizat în terminal cu actualizare automată.
- **Sub-comenzi Avansate**: `monitor`, `search`, `details`, `audit`, `kill`, `suspend`, `resume`.

### 🛡️ Securitate și Diagnoză
- **Security Audit**: Scanare automată pentru detectarea proceselor suspecte (rulate din `/tmp`, conexiuni multiple, etc.).
- **Network Activity**: Vizualizarea conexiunilor IP active pentru fiecare proces.
- **Disk I/O Tracking**: Monitorizarea vitezei de citire și scriere pe disc (MB/s).
- **File Access**: Listarea fișierelor deschise de un proces (Open Files).
- **Process Uptime**: Calculul exact al duratei de funcționare a fiecărui proces.

---

## 🛠️ Instalare

### 1. Clonarea repository-ului
```bash
git clone https://github.com/MMT15/SystemGuardian.git
cd SystemGuardian
```

### 2. Configurarea mediului virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*(Dacă nu ai un fișier requirements.txt, instalează manual: `pip install psutil rich PyQt6`)*

### 3. Dependențe Sistem (pentru Linux GUI)
```bash
sudo apt update && sudo apt install libxcb-cursor0
```

---

## 💻 Utilizare

### Pornire GUI (Recomandat)
```bash
python gui_main.py
```

### Utilizare CLI
- **Monitorizare Live**: `python main.py monitor`
- **Audit Securitate**: `python main.py audit`
- **Detalii Proces**: `python main.py details <PID>`
- **Căutare**: `python main.py search <nume>`

---

## 🔧 Structura Proiectului
- `gui_main.py`: Aplicația principală Desktop (PyQt6).
- `main.py`: Aplicația principală Terminal (Rich).
- `src/monitor.py`: Core logic - Colectarea datelor prin `psutil`.
- `src/alerts.py`: Sistemul de praguri și alerte.
- `src/logger.py`: Logarea istoricului în format CSV.

## 🎓 Scopul Proiectului
Creat ca un proiect demonstrativ pentru ingineria sistemelor software, punând accent pe:
- Programare Orientată pe Obiecte (OOP)
- Gestionarea resurselor în sisteme de operare
- Interfețe utilizator moderne (UX/UI)
- Securitate cibernetică și diagnoză de sistem

---
Developed with 🛡️ by [MMT15](https://github.com/MMT15)
