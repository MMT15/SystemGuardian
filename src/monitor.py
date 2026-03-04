import psutil
from datetime import datetime

class ProcessMonitor:
    @staticmethod
    def get_all_processes():
        """Obține toate procesele active."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username', 'io_counters']):
            try:
                info = proc.info
                # Convertim io_counters în citiri MB/s pentru a fi mai ușor de înțeles
                io = info.get('io_counters')
                info['read_bytes'] = io.read_bytes if io else 0
                info['write_bytes'] = io.write_bytes if io else 0
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    @staticmethod
    def get_top_cpu(limit=15):
        """Top procese sortate după consumul CPU."""
        procs = ProcessMonitor.get_all_processes()
        # Primul apel cpu_percent returnează 0 de cele mai multe ori, așa că psutil recomandă un scurt interval sau apeluri multiple
        return sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

    @staticmethod
    def kill_process(pid):
        """Oprește un proces după PID."""
        try:
            proc = psutil.Process(pid)
            proc.kill()
            return True, f"Procesul {pid} a fost oprit."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def suspend_process(pid):
        """Suspendă (pauză) un proces."""
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            return True, f"Procesul {pid} a fost suspendat."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_process_connections(pid):
        """Obține conexiunile de rețea active pentru un PID."""
        try:
            proc = psutil.Process(pid)
            connections = proc.connections(kind='inet')
            return connections
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []

    @staticmethod
    def search_processes(query):
        """Caută procese după nume."""
        procs = ProcessMonitor.get_all_processes()
        return [p for p in procs if query.lower() in p['name'].lower()]
