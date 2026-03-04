import psutil
from datetime import datetime

class ProcessMonitor:
    @staticmethod
    def get_all_processes():
        """Obține toate procesele active."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
            try:
                processes.append(proc.info)
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
    def resume_process(pid):
        """Reia un proces suspendat."""
        try:
            proc = psutil.Process(pid)
            proc.resume()
            return True, f"Procesul {pid} a fost reluat."
        except Exception as e:
            return False, str(e)
