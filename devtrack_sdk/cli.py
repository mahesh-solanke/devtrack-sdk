# devtrack_sdk/cli.py
import sys

import requests
import typer
from rich.console import Console

from devtrack_sdk.__version__ import __version__

app = typer.Typer(help="DevTrack CLI toolkit", add_completion=False)


def detect_devtrack_endpoint(timeout=0.5) -> str:
    possible_hosts = ["localhost", "127.0.0.1", "0.0.0.0"]
    possible_ports = [8000, 8888, 9000, 8080]
    devtrack_path = "/__devtrack__/stats"

    for host in possible_hosts:
        for port in possible_ports:
            url = f"http://{host}:{port}{devtrack_path}"
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    return url
            except requests.RequestException:
                continue

    typer.echo("⚠️  DevTrack stats endpoint not reachable on common ports.")
    host = typer.prompt(
        f"Please enter the host for your DevTrack stats endpoint\n\
        (e.g., {', '.join(possible_hosts)}) "
    ).strip()
    port = typer.prompt(
        f"Please enter the port for your DevTrack stats endpoint \n\
        (e.g., {', '.join(map(str, possible_ports))}) "
    ).strip()
    protocol = typer.prompt(
        "Please enter the protocol for your DevTrack stats endpoint \n\
        (http or https) "
    )
    return f"{protocol}://{host}:{port}{devtrack_path}"


@app.command()
def version():
    """Show the installed DevTrack SDK version."""
    typer.echo(f"DevTrack SDK v{__version__}")


# TODO: Add a command to generate a default devtrack config file
# @app.command()
# def generate_config():
#     """Generate a default devtrack config file."""
#     config = {
#         "track_paths": ["/"],
#         "exclude_paths": ["/__devtrack__/stats", "/docs", "/openapi.json"],
#     }
#     import json

#     with open("devtrack.config.json", "w") as f:
#         json.dump(config, f, indent=2)
#     typer.echo("✅ devtrack.config.json created.")


@app.command()
def stat(
    top: int = typer.Option(None, help="Show top N endpoints"),
    sort_by: str = typer.Option("hits", help="Sort by 'hits' or 'latency'"),
):
    """Display collected statistics."""
    import json
    from collections import defaultdict

    import requests
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    console.rule("[bold green]📊 DevTrack Stats CLI[/]", style="green")

    stats_url = detect_devtrack_endpoint()

    # Spinner while fetching
    with console.status("[bold cyan]Fetching stats from DevTrack...[/]"):
        try:
            response = requests.get(stats_url)
            response.raise_for_status()
            data = response.json()
            entries = data.get("entries", [])
        except Exception as e:
            console.print(f"[red]❌ Failed to fetch stats from {stats_url}[/]\n{e}")
            raise typer.Exit(1)

    # 🟡 No entries case
    if not entries:
        panel = Panel.fit(
            "[yellow bold]No request stats found yet.[/]\n"
            "[dim]Try hitting your API and re-run `devtrack stat`[/]",
            title="🚧 Empty",
            border_style="yellow",
        )
        console.print(panel)
        return

    average_stats = defaultdict(lambda: {"hits": 0, "total_latency": 0.0})

    for entry in entries:
        path = entry["path"]
        method = entry["method"]
        key = (path, method)
        average_stats[key]["hits"] += 1
        average_stats[key]["total_latency"] += entry["duration_ms"]

    # Sort by the specified criterion
    if sort_by == "latency":
        sorted_stats = sorted(
            average_stats.items(),
            key=lambda item: item[1]["total_latency"] / item[1]["hits"],
            reverse=True,
        )
    else:
        sorted_stats = sorted(
            average_stats.items(), key=lambda item: item[1]["hits"], reverse=True
        )

    # Apply top N filter
    if top:
        sorted_stats = sorted_stats[:top]

    # 📋 Display Table
    console.rule("[bold cyan]📈 Endpoint Usage Summary[/]")
    table = Table(title="DevTrack Stats Summary", border_style="blue")
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Method", style="green")
    table.add_column("Hits", justify="right", style="magenta")
    table.add_column("Avg Latency (ms)", justify="right", style="yellow")

    for (path, method), info in sorted_stats:
        hits = info["hits"]
        avg_latency = info["total_latency"] / hits
        table.add_row(path, method, str(hits), f"{avg_latency:.2f}")

    console.print(table)

    # 🧮 Totals
    console.print(f"[bold green]📊 Total unique endpoints:[/] {len(sorted_stats)}")
    console.print(f"[bold blue]📦 Total requests analyzed:[/] {len(entries)}\n")

    # 💾 Ask for export
    if typer.confirm("💾 Would you like to export these stats as JSON?", default=False):
        file_path = typer.prompt("Enter file path", default="devtrack_stats.json")
        try:
            with open(file_path, "w") as f:
                json.dump(entries, f, indent=2)
            console.print(f"[bold green]✅ Exported to {file_path}[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed to write file: {e}[/]")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        console = Console()
        console.print("[bold blue]🚀 DevTrack CLI[/]")
        console.print("Usage:")
        console.print("  devtrack stat     [green]Show API stats[/]")
        console.print("  devtrack version  [green]Show SDK version[/]")
        console.print(
            "\nRun [yellow]devtrack COMMAND --help[/] for command-specific options."
        )
        raise typer.Exit()

    app()
