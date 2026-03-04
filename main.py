import os
import sys
import time
import argparse
import psutil
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from src.monitor import ProcessMonitor
from src.alerts import AlertSystem
from src.logger import HistoryLogger

console = Console()

def create_layout():
    """Creează layout-ul pentru interfața Live."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=5)
    )
    return layout

def get_header():
    cpu_percent = psutil.cpu_percent()
    mem_percent = psutil.virtual_memory().percent
    
    # Culori dinamice în funcție de încărcare
    cpu_color = "red" if cpu_percent > 80 else "yellow" if cpu_percent > 50 else "green"
    mem_color = "red" if mem_percent > 80 else "yellow" if mem_percent > 50 else "green"

    header_text = f"[bold cyan]🛡️ SYSTEM GUARDIAN [/bold cyan] | [bold]CPU:[/bold] [{cpu_color}]{cpu_percent}%[/{cpu_color}] | [bold]RAM:[/bold] [{mem_color}]{mem_percent}%[/{mem_color}]"
    
    return Panel(
        header_text,
        style="white",
        box=box.ROUNDED
    )

def get_process_table(monitor, limit=15):
    processes = monitor.get_top_cpu(limit=limit)
    
    table = Table(box=box.SIMPLE)
    table.add_column("PID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("CPU %", justify="right", style="green")
    table.add_column("Memory %", justify="right", style="yellow")
    table.add_column("Read (MB)", justify="right", style="blue")
    table.add_column("Write (MB)", justify="right", style="blue")
    table.add_column("Status", style="blue")

    for proc in processes:
        read_mb = proc.get('read_bytes', 0) / (1024 * 1024)
        write_mb = proc.get('write_bytes', 0) / (1024 * 1024)
        
        table.add_row(
            str(proc['pid']),
            proc['name'][:25],
            f"{proc['cpu_percent']:.1f}",
            f"{proc['memory_percent']:.1f}",
            f"{read_mb:.1f}",
            f"{write_mb:.1f}",
            proc['status']
        )
    return table

def main():
    parser = argparse.ArgumentParser(description="System Guardian - Advanced Process Monitor")
    subparsers = parser.add_subparsers(dest="command", help="Comenzi disponibile")

    # Comanda Monitor
    monitor_parser = subparsers.add_parser("monitor", help="Pornește monitorizarea live")
    monitor_parser.add_argument("--interval", type=int, default=2, help="Update interval (secunde)")
    monitor_parser.add_argument("--cpu-limit", type=float, default=80.0, help="CPU limită alertă (%)")
    monitor_parser.add_argument("--mem-limit", type=float, default=80.0, help="Memorie limită alertă (%)")

    # Comenzi de Control
    kill_parser = subparsers.add_parser("kill", help="Oprește un proces")
    kill_parser.add_argument("pid", type=int, help="PID-ul procesului")

    suspend_parser = subparsers.add_parser("suspend", help="Suspendă un proces")
    suspend_parser.add_argument("pid", type=int, help="PID-ul procesului")

    resume_parser = subparsers.add_parser("resume", help="Reia un proces")
    resume_parser.add_argument("pid", type=int, help="PID-ul procesului")

    # Comanda Search
    search_parser = subparsers.add_parser("search", help="Caută un proces după nume")
    search_parser.add_argument("query", type=str, help="Numele căutat (ex: chrome)")

    # Comanda Details
    details_parser = subparsers.add_parser("details", help="Informații detaliate proces")
    details_parser.add_argument("pid", type=int, help="PID-ul procesului")

    # Comanda Audit
    audit_parser = subparsers.add_parser("audit", help="Scanează procesele suspecte")

    args = parser.parse_args()

    monitor = ProcessMonitor()

    if args.command == "monitor":
        alerts = AlertSystem(cpu_threshold=args.cpu_limit, mem_threshold=args.mem_limit)
        logger = HistoryLogger()
        layout = create_layout()
        layout["header"].update(get_header())

        try:
            with Live(layout, refresh_per_second=1, screen=True) as live:
                while True:
                    # Date proaspete
                    all_procs = monitor.get_top_cpu(limit=20)
                    
                    # Verifică alerte
                    alerts.check_processes(all_procs)
                    
                    # Loghează
                    logger.log_processes(all_procs)

                    # Update UI
                    layout["main"].update(Panel(get_process_table(monitor), title="Active Processes", border_style="green"))
                    layout["footer"].update(Panel(alerts.get_latest_alerts_str(), title="Active Alerts", border_style="red"))
                    
                    time.sleep(args.interval)
        except KeyboardInterrupt:
            console.print("\n[bold red]System Guardian oprit.[/bold red]")

    elif args.command == "search":
        results = monitor.search_processes(args.query)
        if results:
            search_table = Table(title=f"Search Results for: '{args.query}'", box=box.DOUBLE)
            search_table.add_column("PID", style="cyan")
            search_table.add_column("Name", style="magenta")
            search_table.add_column("CPU %", justify="right", style="green")
            search_table.add_column("Memory %", justify="right", style="yellow")
            search_table.add_column("Status", style="blue")
            
            for p in results:
                search_table.add_row(str(p['pid']), p['name'][:25], f"{p['cpu_percent']:.1f}", f"{p['memory_percent']:.1f}", p['status'])
            console.print(search_table)
        else:
            console.print(f"[red]Niciun proces găsit pentru '{args.query}'.[/red]")

    elif args.command == "details":
        info = monitor.get_detailed_info(args.pid)
        if not info:
            console.print(f"[bold red]❌ Eroare: Nu s-au putut obține detalii pentru PID {args.pid} (posibil acces respins).[/bold red]")
        else:
            detail_text = f"[bold cyan]Name:[/bold cyan] {info['name']}\n"
            detail_text += f"[bold cyan]Status:[/bold cyan] {info['status']}\n"
            detail_text += f"[bold cyan]Command:[/bold cyan] {info['cmdline'][:100]}...\n"
            detail_text += f"[bold cyan]Memory:[/bold cyan] {info['memory_info'].rss / (1024*1024):.1f} MB (RSS)\n\n"
            
            detail_text += "[bold yellow]📂 OPEN FILES (First 10):[/bold yellow]\n"
            if info['open_files']:
                detail_text += "\n".join([f"  📄 {f}" for f in info['open_files']])
            else:
                detail_text += "  (No open files detected or access denied)\n"

            detail_text += "\n\n[bold yellow]🌐 NETWORK CONNECTIONS:[/bold yellow]\n"
            if info['connections']:
                for c in info['connections']:
                    remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "*"
                    detail_text += f"  🔗 {c.laddr.ip}:{c.laddr.port} -> {remote}\n"
            else:
                detail_text += "  (No active network connections)"

            console.print(Panel(detail_text, title=f"Detaill View: PID {args.pid}", border_style="magenta", expand=False))

    elif args.command == "audit":
        risky = monitor.run_security_audit()
        if not risky:
            console.print("[bold green]✅ Scanare completă: Niciun proces suspect găsit.[/bold green]")
        else:
            table = Table(title="⚠️ SECURITY AUDIT REPORT", box=box.HEAVY)
            table.add_column("PID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Risk Score", justify="center", style="bold red")
            table.add_column("Reasons", style="yellow")

            for p in risky:
                table.add_row(
                    str(p['pid']),
                    p['name'][:25],
                    str(p['risk_score']),
                    ", ".join(p['reasons'])
                )
            console.print(table)

    elif args.command in ["kill", "suspend", "resume"]:
        func = getattr(monitor, f"{args.command}_process")
        success, msg = func(args.pid)
        if success:
            console.print(f"[bold green]Succes:[/bold green] {msg}")
        else:
            console.print(f"[bold red]Eroare:[/bold red] {msg}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
