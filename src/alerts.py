class AlertSystem:
    def __init__(self, cpu_threshold=80.0, mem_threshold=80.0):
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.alerts = []

    def check_processes(self, processes):
        """Verifică procesele împotriva pragurilor."""
        new_alerts = []
        for proc in processes:
            if proc['cpu_percent'] > self.cpu_threshold:
                new_alerts.append({
                    "type": "CPU",
                    "pid": proc['pid'],
                    "name": proc['name'],
                    "value": proc['cpu_percent']
                })
            if proc['memory_percent'] > self.mem_threshold:
                new_alerts.append({
                    "type": "Memory",
                    "pid": proc['pid'],
                    "name": proc['name'],
                    "value": proc['memory_percent']
                })
        self.alerts = new_alerts
        return new_alerts

    def get_latest_alerts_str(self):
        """Returnează o listă scurtă cu alertele active pentru afișare."""
        if not self.alerts:
            return "Nicio alertă activă."
        
        lines = []
        for alert in self.alerts[:5]:  # Primele 5 alerte
            lines.append(f"[red]⚠️ {alert['type']} Alarm: {alert['name']} ({alert['pid']}) utilizes {alert['value']:.1f}%[/red]")
        return "\n".join(lines)
