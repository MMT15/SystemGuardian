import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QProgressBar, QTabWidget, 
                             QMessageBox, QHeaderView, QLineEdit)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QFont, QColor

from src.monitor import ProcessMonitor

class SystemGuardianGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.monitor = ProcessMonitor()
        self.selected_pid = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("System Guardian 🛡️")
        self.resize(1000, 700)

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Dashboard (CPU & RAM) ---
        dashboard_layout = QHBoxLayout()
        
        # CPU Info
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel("CPU Usage: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        
        # RAM Info
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel("RAM Usage: 0%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_bar)

        dashboard_layout.addLayout(cpu_layout)
        dashboard_layout.addLayout(ram_layout)
        main_layout.addLayout(dashboard_layout)

        # --- Tabs ---
        self.tabs = QTabWidget()
        
        # Monitor Tab
        self.monitor_tab = QWidget()
        monitor_layout = QVBoxLayout(self.monitor_tab)
        
        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name...")
        self.search_input.textChanged.connect(self.update_data)
        search_layout.addWidget(self.search_input)
        monitor_layout.addLayout(search_layout)
        
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "RAM %", "Status", "Read/Write"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        monitor_layout.addWidget(self.process_table)

        # Buttons Control
        btn_layout = QHBoxLayout()
        self.btn_kill = QPushButton("Kill Process")
        self.btn_kill.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.btn_kill.clicked.connect(self.handle_kill)

        self.btn_details = QPushButton("Show Details")
        self.btn_details.setStyleSheet("background-color: #008CBA; color: white; padding: 10px;")
        self.btn_details.clicked.connect(self.handle_details)

        btn_layout.addWidget(self.btn_kill)
        btn_layout.addWidget(self.btn_details)
        monitor_layout.addLayout(btn_layout)

        self.tabs.addTab(self.monitor_tab, "Monitor")
        main_layout.addWidget(self.tabs)

        # --- Timer for Auto-update ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)

        self.update_data()

    def update_data(self):
        # Capture current selection by PID
        current_row = self.process_table.currentRow()
        if current_row >= 0:
            try:
                item = self.process_table.item(current_row, 0)
                if item:
                    self.selected_pid = int(item.text())
            except:
                pass

        # Update Dashboard
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU Usage: {cpu}%")
        self.cpu_bar.setValue(int(cpu))
        self.ram_label.setText(f"RAM Usage: {ram}%")
        self.ram_bar.setValue(int(ram))

        # Filter Logic
        search_text = self.search_input.text().lower()
        if search_text:
            all_procs = self.monitor.get_all_processes()
            processes = [p for p in all_procs if search_text in p['name'].lower()]
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        else:
            processes = self.monitor.get_top_cpu(limit=30)
            
        self.process_table.setRowCount(len(processes))

        new_selected_row = -1
        for row, proc in enumerate(processes):
            pid_str = str(proc['pid'])
            self.process_table.setItem(row, 0, QTableWidgetItem(pid_str))
            self.process_table.setItem(row, 1, QTableWidgetItem(proc['name']))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{proc['cpu_percent']:.1f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{proc['memory_percent']:.1f}"))
            self.process_table.setItem(row, 4, QTableWidgetItem(proc['status']))
            
            rw_mb = f"R: {proc.get('read_bytes', 0)/(1024*1024):.1f} / W: {proc.get('write_bytes', 0)/(1024*1024):.1f}"
            self.process_table.setItem(row, 5, QTableWidgetItem(rw_mb))

            if self.selected_pid == proc['pid']:
                new_selected_row = row

        # Restore selection
        if new_selected_row >= 0:
            self.process_table.setCurrentCell(new_selected_row, 0)
            self.process_table.selectRow(new_selected_row)

    def handle_kill(self):
        current_row = self.process_table.currentRow()
        if current_row < 0:
            return
        pid = int(self.process_table.item(current_row, 0).text())
        name = self.process_table.item(current_row, 1).text()
        reply = QMessageBox.question(self, 'Confirmation', f"Kill {name} ({pid})?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.monitor.kill_process(pid)
            if success: QMessageBox.information(self, "Success", msg)
            else: QMessageBox.warning(self, "Error", msg)

    def handle_details(self):
        current_row = self.process_table.currentRow()
        if current_row < 0: return
        pid = int(self.process_table.item(current_row, 0).text())
        info = self.monitor.get_detailed_info(pid)
        if info:
            uptime_seconds = psutil.time.time() - info['create_time']
            uptime_str = psutil.time.strftime('%Hh %Mm %Ss', psutil.time.gmtime(uptime_seconds))
            details = (f"Name: {info['name']}\nStatus: {info['status']}\nUptime: {uptime_str}\n"
                       f"Memory: {info['memory_info'].rss / (1024*1024):.1f} MB\n"
                       f"Files: {', '.join(info['open_files'][:3])}...")
            QMessageBox.information(self, f"Details PID {pid}", details)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SystemGuardianGUI()
    window.show()
    sys.exit(app.exec())
