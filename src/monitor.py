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
    def get_detailed_info(pid):
        """Obține informații complete despre un proces."""
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    "name": proc.name(),
                    "exe": proc.exe(),
                    "cmdline": " ".join(proc.cmdline()),
                    "status": proc.status(),
                    "username": proc.username(),
                    "create_time": proc.create_time(),
                    "memory_info": proc.memory_info(),
                    "open_files": [f.path for f in proc.open_files()[:10]], # Primele 10 fișiere
                    "connections": proc.connections(kind='inet')
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    @staticmethod
    def run_security_audit():
        """Scanează procesele pentru indicatori de risc."""
        risky_procs = []
        # Eliminăm 'connections' din lista de atribute pentru a evita ValueError
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status', 'username']):
            try:
                info = proc.info
                risk_level = 0
                reasons = []

                # Criteriu 1: Locație suspectă
                exe_path = info.get('exe')
                if exe_path and any(p in exe_path for p in ['/tmp', '/var/tmp', '/dev/shm']):
                    risk_level += 2
                    reasons.append("⚠️ Rulează din folder temporar (/tmp)")

                # Criteriu 2: Conexiuni multiple (Apelăm metoda manual)
                try:
                    conns = proc.connections(kind='inet')
                    if conns and len(conns) > 5:
                        risk_level += 1
                        reasons.append(f"🌐 Multe conexiuni active ({len(conns)})")
                        info['audit_connections'] = conns # Salvăm conexiunile pentru detalii
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                # Criteriu 3: Fără username
                if not info.get('username'):
                    risk_level += 1
                    reasons.append("👤 Utilizator necunoscut")

                if risk_level > 0:
                    info['risk_score'] = risk_level
                    info['reasons'] = reasons
                    risky_procs.append(info)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(risky_procs, key=lambda x: x['risk_score'], reverse=True)
