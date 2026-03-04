import psutil
import platform
import os
import subprocess
import time
import requests
from datetime import datetime

class ProcessMonitor:
    # Cache pentru calculul vitezei (PID -> (last_read, last_write, last_time))
    _net_cache = {}
    # Cache pentru Geolocation (IP -> {country, flag})
    _geo_cache = {}

    @staticmethod
    def get_geo_info(ip):
        """Obține țara și steagul pentru un IP (cu cache)."""
        if not ip or ip.startswith(('127.', '192.168.', '10.', '172.')) or ip == '::1':
            return "Local Network", "🏠"
        
        if ip in ProcessMonitor._geo_cache:
            return ProcessMonitor._geo_cache[ip]
        
        try:
            # Folosim un API public rapid (ip-api.com)
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode", timeout=1)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    country = data['country']
                    # Convertim countryCode în steag Emoji
                    code = data['countryCode']
                    flag = chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)
                    ProcessMonitor._geo_cache[ip] = (country, flag)
                    return country, flag
        except:
            pass
        
        return "Unknown", "❓"

    @staticmethod
    def get_all_processes():
        """Obține toate procesele active cu calculul vitezei de rețea."""
        processes = []
        current_time = time.time()
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username', 'io_counters', 'net_connections']):
            try:
                info = proc.info
                io = info.get('io_counters')
                pid = info['pid']
                
                # Inițializare valori de bază
                read_bytes = io.read_bytes if io else 0
                write_bytes = io.write_bytes if io else 0
                
                # Calcul viteză (Delta Bytes / Delta Time)
                download_speed = 0
                upload_speed = 0
                
                if pid in ProcessMonitor._net_cache:
                    last_read, last_write, last_time = ProcessMonitor._net_cache[pid]
                    time_delta = current_time - last_time
                    if time_delta > 0:
                        download_speed = (read_bytes - last_read) / time_delta
                        upload_speed = (write_bytes - last_write) / time_delta
                
                # Update cache
                ProcessMonitor._net_cache[pid] = (read_bytes, write_bytes, current_time)
                
                info['read_bytes'] = read_bytes
                info['write_bytes'] = write_bytes
                info['download_speed'] = max(0, download_speed)
                info['upload_speed'] = max(0, upload_speed)
                
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError):
                pass
        
        # Curățăm cache-ul pentru procesele care nu mai există
        active_pids = {p['pid'] for p in processes}
        ProcessMonitor._net_cache = {pid: val for pid, val in ProcessMonitor._net_cache.items() if pid in active_pids}
        
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
                conns = []
                try:
                    # Folosim net_connections sau connections în funcție de versiune
                    if hasattr(proc, 'net_connections'):
                        conns = proc.net_connections(kind='inet')
                    else:
                        conns = proc.connections(kind='inet')
                except:
                    pass

                return {
                    "name": proc.name(),
                    "exe": proc.exe(),
                    "cmdline": " ".join(proc.cmdline()),
                    "status": proc.status(),
                    "username": proc.username(),
                    "create_time": proc.create_time(),
                    "memory_info": proc.memory_info(),
                    "open_files": [f.path for f in proc.open_files()[:10]],
                    "connections": conns
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

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status', 'username', 'net_connections']):
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
                    conns = info.get('net_connections')
                    if conns and len(conns) > 10:
                        risk_level += 1
                        reasons.append(f"🌐 High network activity ({len(conns)} conns)")
                        info['audit_connections'] = conns
                except:
                    pass

                if (system == "Linux" or system == "Darwin") and not info.get('username'):
                    risk_level += 1
                    reasons.append("👤 Unknown user")

                if risk_level > 0:
                    info['risk_score'] = risk_level
                    info['reasons'] = reasons
                    risky_procs.append(info)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
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
