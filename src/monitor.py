import psutil
import platform
import os
import subprocess
from datetime import datetime

class ProcessMonitor:
    @staticmethod
    def get_all_processes():
        """Obține toate procesele active."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username', 'io_counters']):
            try:
                info = proc.info
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
                    "open_files": [f.path for f in proc.open_files()[:10]],
                    "connections": proc.connections(kind='inet')
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    @staticmethod
    def run_security_audit():
        """Scanează procesele pentru indicatori de risc adaptați la sistemul de operare."""
        risky_procs = []
        system = platform.system()
        
        # Definim căile suspecte în funcție de OS
        risky_paths = []
        if system == "Linux" or system == "Darwin":
            risky_paths = ['/tmp', '/var/tmp', '/dev/shm']
        elif system == "Windows":
            temp_env = os.environ.get('TEMP', '').lower()
            tmp_env = os.environ.get('TMP', '').lower()
            risky_paths = [temp_env, tmp_env, 'c:\\windows\\temp']
            risky_paths = [p for p in risky_paths if p]

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status', 'username']):
            try:
                info = proc.info
                risk_level = 0
                reasons = []

                exe_path = info.get('exe')
                if exe_path:
                    exe_path_lower = exe_path.lower()
                    if any(rp in exe_path_lower for rp in risky_paths):
                        risk_level += 2
                        reasons.append(f"⚠️ Suspect path: {os.path.dirname(exe_path)}")

                try:
                    conns = proc.connections(kind='inet')
                    if conns and len(conns) > 10:
                        risk_level += 1
                        reasons.append(f"🌐 High network activity ({len(conns)} conns)")
                        info['audit_connections'] = conns
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                if (system == "Linux" or system == "Darwin") and not info.get('username'):
                    risk_level += 1
                    reasons.append("👤 Unknown user")

                if risk_level > 0:
                    info['risk_score'] = risk_level
                    info['reasons'] = reasons
                    risky_procs.append(info)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(risky_procs, key=lambda x: x['risk_score'], reverse=True)

class HardwareMonitor:
    @staticmethod
    def get_cpu_temp():
        """Obține temperatura procesorului."""
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        
        # Căutăm 'coretemp' (Intel) sau 'k10temp' (AMD) pe Linux
        for name in ['coretemp', 'k10temp', 'cpu_thermal', 'soc_thermal']:
            if name in temps:
                return temps[name][0].current
        
        # Dacă nu găsim nume specifice, returnăm prima valoare disponibilă
        for name, entries in temps.items():
            if entries:
                return entries[0].current
        return None

    @staticmethod
    def get_gpu_temp():
        """Obține temperatura plăcii grafice (Universal: NVIDIA, AMD, Intel)."""
        # Metoda 1: Încercăm prin psutil (funcționează pentru AMD și unele Intel pe Linux)
        temps = psutil.sensors_temperatures()
        if temps:
            # Căutăm drivere cunoscute
            for name in ['amdgpu', 'radeon', 'intel_power']:
                if name in temps and temps[name]:
                    return temps[name][0].current

        # Metoda 2: Încercăm NVIDIA (nvidia-smi)
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                encoding='utf-8',
                stderr=subprocess.DEVNULL
            )
            return float(output.strip())
        except Exception:
            pass

        # Metoda 3: Căutăm în fișierele sistem Linux (Thermal Zones)
        try:
            for zone in os.listdir('/sys/class/thermal'):
                if zone.startswith('thermal_zone'):
                    with open(f'/sys/class/thermal/{zone}/type', 'r') as f:
                        if 'gpu' in f.read().lower():
                            with open(f'/sys/class/thermal/{zone}/temp', 'r') as tf:
                                return float(tf.read().strip()) / 1000.0
        except Exception:
            pass
            
        return None
