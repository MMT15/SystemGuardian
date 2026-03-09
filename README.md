# System Guardian

**System Guardian** is an advanced process monitoring and management utility for Linux systems, designed to provide full visibility into hardware resources and software security. The project includes both a modern graphical user interface (GUI) and a powerful command line interface (CLI).

## Main Features

### Graphical User Interface (GUI) - PyQt6
- **Real-time Dashboard**: Live monitoring for CPU and RAM with interactive progress bars.
- **Sticky Selection**: Ability to "anchor" a selected process; it remains visible in the table even if it is no longer in the Top 30.
- **Search & Filter**: Instant filtering of processes by name.
- **One-Click Actions**: Dedicated buttons for viewing details or stopping processes (Kill).

### CLI Interface
- **Live Monitoring**: Colored and organized table in the terminal with automatic updates.
- **Advanced Sub-commands**: `monitor`, `search`, `details`, `audit`, `kill`, `suspend`, `resume`.

### Security and Diagnosis
- **Security Audit**: Automatic scanning to detect suspicious processes (run from `/tmp`, multiple connections, etc.).
- **Network Activity**: View active IP connections for each process.
- **Disk I/O Tracking**: Monitoring read and write speeds on disk (MB/s).
- **File Access**: Listing files opened by a process (Open Files).
- **Process Uptime**: Exact calculation of the running duration of each process.

---

## Installation

### 1. Cloning the repository
```bash
git clone https://github.com/MMT15/SystemGuardian.git
cd SystemGuardian
```

### 2. Virtual environment configuration
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*(If you do not have a requirements.txt file, install manually: `pip install psutil rich PyQt6`)*

### 3. System Dependencies (for Linux GUI)
```bash
sudo apt update && sudo apt install libxcb-cursor0
```

---

## Usage

### Start GUI (Recommended)
```bash
python gui_main.py
```

### CLI Usage
- **Live Monitoring**: `python main.py monitor`
- **Security Audit**: `python main.py audit`
- **Process Details**: `python main.py details <PID>`
- **Search**: `python main.py search <name>`

---

## Project Structure
- `gui_main.py`: Main Desktop application (PyQt6).
- `main.py`: Main Terminal application (Rich).
- `src/monitor.py`: Core logic - Data collection via `psutil`.
- `src/alerts.py`: Thresholds and alerts system.
- `src/logger.py`: Logging history in CSV format.

## Project Goal
Created as a demonstrative project for software systems engineering, emphasizing:
- Object-Oriented Programming (OOP)
- Resource management in operating systems
- Modern user interfaces (UX/UI)
- Cybersecurity and system diagnosis

---
