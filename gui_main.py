import sys
import time
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
        self.last_risky_procs = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("System Guardian 🛡️")
        self.resize(1000, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Dashboard
        dashboard_layout = QHBoxLayout()
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel("CPU Usage: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel("RAM Usage: 0%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_bar)

        dashboard_layout.addLayout(cpu_layout)
        dashboard_layout.addLayout(ram_layout)
        main_layout.addLayout(dashboard_layout)

        # Tabs
        self.tabs = QTabWidget()
        
        # Monitor Tab
        self.monitor_tab = QWidget()
        monitor_layout = QVBoxLayout(self.monitor_tab)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name...")
        self.search_input.textChanged.connect(self.update_data)
        search_layout.addWidget(self.search_input)
        monitor_layout.addLayout(search_layout)
        
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "RAM %", "Status", "Disk I/O"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.process_table.itemSelectionChanged.connect(self.on_selection_changed)
        monitor_layout.addWidget(self.process_table)

        btn_layout = QHBoxLayout()
        self.btn_kill = QPushButton("Kill Process")
        self.btn_kill.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-weight: bold;")
        self.btn_kill.clicked.connect(self.handle_kill)

        self.btn_details = QPushButton("Show Details")
        self.btn_details.setStyleSheet("background-color: #008CBA; color: white; padding: 10px; font-weight: bold;")
        self.btn_details.clicked.connect(self.handle_details)

        btn_layout.addWidget(self.btn_kill)
        btn_layout.addWidget(self.btn_details)
        monitor_layout.addLayout(btn_layout)

        # Security Audit Tab
        self.audit_tab = QWidget()
        audit_layout = QVBoxLayout(self.audit_tab)
        
        audit_header = QLabel("🛡️ Security Audit Scanner")
        audit_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        audit_layout.addWidget(audit_header)
        
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(4)
        self.audit_table.setHorizontalHeaderLabels(["PID", "Name", "Risk Score", "Reasons"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.audit_table.itemDoubleClicked.connect(self.on_audit_item_double_clicked)
        audit_layout.addWidget(self.audit_table)
        
        self.btn_run_audit = QPushButton("🚀 Run Security Scan")
        self.btn_run_audit.setStyleSheet("background-color: #673AB7; color: white; padding: 15px; font-size: 14px; font-weight: bold;")
        self.btn_run_audit.clicked.connect(self.handle_run_audit)
        audit_layout.addWidget(self.btn_run_audit)

        self.tabs.addTab(self.monitor_tab, "Monitor")
        self.tabs.addTab(self.audit_tab, "Security Audit")
        main_layout.addWidget(self.tabs)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)

        self.update_data()

    def on_selection_changed(self):
        selected_rows = self.process_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            pid_item = self.process_table.item(row, 0)
            if pid_item:
                self.selected_pid = int(pid_item.text())

    def update_data(self):
        cpu_total = psutil.cpu_percent()
        ram_total = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU Usage: {cpu_total}%")
        self.cpu_bar.setValue(int(cpu_total))
        self.ram_label.setText(f"RAM Usage: {ram_total}%")
        self.ram_bar.setValue(int(ram_total))

        search_text = self.search_input.text().lower()
        if search_text:
            all_procs = self.monitor.get_all_processes()
            processes = [p for p in all_procs if search_text in p['name'].lower()]
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        else:
            processes = self.monitor.get_top_cpu(limit=30)

        if self.selected_pid:
            if not any(p['pid'] == self.selected_pid for p in processes):
                try:
                    p = psutil.Process(self.selected_pid)
                    with p.oneshot():
                        io = p.io_counters() if hasattr(p, 'io_counters') else None
                        processes.append({
                            'pid': p.pid, 'name': p.name(), 'cpu_percent': p.cpu_percent(),
                            'memory_percent': p.memory_percent(), 'status': p.status(),
                            'read_bytes': io.read_bytes if io else 0, 'write_bytes': io.write_bytes if io else 0
                        })
                except: self.selected_pid = None

        self.process_table.blockSignals(True)
        self.process_table.setRowCount(len(processes))
        new_selected_row = -1
        for row, proc in enumerate(processes):
            pid_val = proc['pid']
            pid_item = QTableWidgetItem(str(pid_val))
            pid_item.setFlags(pid_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.process_table.setItem(row, 0, pid_item)
            self.process_table.setItem(row, 1, QTableWidgetItem(proc['name']))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{proc['cpu_percent']:.1f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{proc['memory_percent']:.1f}"))
            self.process_table.setItem(row, 4, QTableWidgetItem(proc['status']))
            rw_mb = f"R: {proc.get('read_bytes', 0)/(1024*1024):.1f} / W: {proc.get('write_bytes', 0)/(1024*1024):.1f}"
            self.process_table.setItem(row, 5, QTableWidgetItem(rw_mb))
            if self.selected_pid == pid_val:
                new_selected_row = row
                for col in range(6): self.process_table.item(row, col).setBackground(QColor("#e3f2fd"))
        if new_selected_row >= 0: self.process_table.selectRow(new_selected_row)
        self.process_table.blockSignals(False)

    def handle_run_audit(self):
        self.btn_run_audit.setText("🔄 Scanning...")
        self.btn_run_audit.setEnabled(False)
        QApplication.processEvents()
        
        risky_procs = self.monitor.run_security_audit()
        self.last_risky_procs = risky_procs
        self.audit_table.setRowCount(len(risky_procs))
        
        for row, proc in enumerate(risky_procs):
            pid_item = QTableWidgetItem(str(proc['pid']))
            pid_item.setForeground(QColor("red"))
            self.audit_table.setItem(row, 0, pid_item)
            self.audit_table.setItem(row, 1, QTableWidgetItem(proc['name']))
            
            risk_item = QTableWidgetItem(str(proc['risk_score']))
            risk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.audit_table.setItem(row, 2, risk_item)
            
            self.audit_table.setItem(row, 3, QTableWidgetItem(", ".join(proc['reasons'])))

        self.btn_run_audit.setText("🚀 Run Security Scan")
        self.btn_run_audit.setEnabled(True)
        if not risky_procs:
            QMessageBox.information(self, "Audit Result", "✅ No risky processes found!")

    def on_audit_item_double_clicked(self, item):
        row = item.row()
        pid = int(self.audit_table.item(row, 0).text())
        proc_info = next((p for p in self.last_risky_procs if p['pid'] == pid), None)
        
        if proc_info and 'audit_connections' in proc_info:
            conns = proc_info['audit_connections']
            conn_text = "\n".join([f"🔗 {c.laddr.ip}:{c.laddr.port} -> {c.raddr.ip if c.raddr else '*'}:{c.raddr.port if c.raddr else '*'}" for c in conns])
            QMessageBox.information(self, f"Network for PID {pid}", f"Process: {proc_info['name']}\n\nConnections:\n{conn_text}")
        else:
            QMessageBox.information(self, "Info", "Acest proces nu are conexiuni de rețea înregistrate.")

    def handle_kill(self):
        if not self.selected_pid: return
        reply = QMessageBox.question(self, 'Confirm', f"Kill PID {self.selected_pid}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.monitor.kill_process(self.selected_pid)
            if success: self.selected_pid = None; self.update_data()

    def handle_details(self):
        if not self.selected_pid: return
        info = self.monitor.get_detailed_info(self.selected_pid)
        if info:
            uptime = time.time() - info['create_time']
            msg = f"Name: {info['name']}\nUptime: {time.strftime('%Hh %Mm %Ss', time.gmtime(uptime))}\nPath: {info['exe']}"
            QMessageBox.information(self, "Details", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SystemGuardianGUI()
    window.show()
    sys.exit(app.exec())
