# devtrack_sdk/cli.py
import json
import os
import re
from datetime import datetime, timedelta
from typing import Optional

import duckdb
import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from devtrack_sdk.__version__ import __version__
from devtrack_sdk.database import DevTrackDB, init_db

app = typer.Typer(
    name="devtrack",
    help="🚀 DevTrack CLI - Comprehensive request tracking and analytics toolkit",
    add_completion=False,
    rich_markup_mode="rich",
)


def parse_lock_error(error_msg: str) -> dict:
    """Extract PID and process info from DuckDB lock error."""
    pid_match = re.search(r"PID (\d+)", error_msg)
    process_match = re.search(r"held in ([^\s(]+)", error_msg)

    return {
        "pid": pid_match.group(1) if pid_match else None,
        "process": process_match.group(1) if process_match else None,
        "is_lock_error": "Conflicting lock" in error_msg
        or "Could not set lock" in error_msg,
    }


def check_db_initialized_via_api(console, db_path: str, timeout: int = 2) -> bool:
    """
    Check if database is initialized via HTTP API.
    Returns True if initialized and shows info, False otherwise.
    """
    try:
        stats_url = detect_devtrack_endpoint(timeout=timeout)
        if not stats_url:
            return False

        response = requests.get(stats_url, timeout=5)
        if response.status_code != 200:
            return False

        # Database is accessible via API - it's initialized
        data = response.json()
        console.print(
            "[bold green]✅ Database is already initialized " "(accessible via API)[/]"
        )

        # Show database info from API
        entries = data.get("entries", [])
        total_requests = len(entries)
        unique_endpoints = len(
            set(
                (
                    entry.get("path_pattern", entry.get("path", "")),
                    entry.get("method", ""),
                )
                for entry in entries
            )
        )

        table = Table(
            title="Database Information (via API)",
            border_style="green",
        )
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Database Path", db_path)
        table.add_row("Total Requests", str(total_requests))
        table.add_row("Unique Endpoints", str(unique_endpoints))
        console.print(table)

        console.print(
            "[dim]💡 Your application is running and the database "
            "is already initialized.[/]"
        )
        console.print(
            "[dim]💡 To reset the database, run: " "[cyan]devtrack reset[/][/]"
        )
        return True
    except Exception:
        return False


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
        f"Enter the host for your DevTrack stats endpoint\n\
        (e.g., {', '.join(possible_hosts)} or your domain like api.example.com) "
    ).strip()

    # Clean up host input - remove protocol and trailing slashes if present
    if "://" in host:
        protocol, host = host.split("://", 1)
    else:
        protocol = None
    host = host.rstrip("/")

    # Ask if the user wants to enter a port
    enter_port = typer.confirm("Do you want to enter a port number?", default=True)
    if enter_port:
        port = (
            typer.prompt(
                f"Enter the port number (press Enter to skip if using default port)\n\
            (Common ports: {', '.join(map(str, possible_ports))})",
                default="",
            ).strip()
            or None
        )
    else:
        port = None

    # Only ask for protocol if it wasn't in the host input
    if protocol is None:
        protocol = typer.prompt(
            "Please enter the protocol for your DevTrack stats endpoint \n\
            (http or https) "
        )

    # Construct URL
    url = f"{protocol}://{host}"
    if port:
        url = f"{url}:{port}"
    return f"{url}{devtrack_path}"


@app.command()
def version():
    """📦 Show the installed DevTrack SDK version and build information."""
    console = Console()
    console.print(f"[bold blue]DevTrack SDK[/] v[green]{__version__}[/]")

    # Show additional info
    info_table = Table(title="DevTrack Information", border_style="blue")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")

    info_table.add_row("Version", __version__)
    info_table.add_row("Framework Support", "FastAPI, Django")
    info_table.add_row("Database", "DuckDB")
    info_table.add_row("CLI Features", "8 commands")

    console.print(info_table)


@app.command()
def init(
    db_path: str = typer.Option("devtrack_logs.db", help="Path to the database file"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Reset database: delete all logs and reset sequence to 0",
    ),
):
    """🗄️ Initialize a new DevTrack database with DuckDB backend."""
    console = Console()

    # Step 1: Try read-only to check if already initialized
    try:
        db_readonly = DevTrackDB(db_path, read_only=True)
        if db_readonly.tables_exist():
            # Tables exist - check if we need to reset (--force)
            db_readonly.close()

            def force_initialize_database():
                # --force specified: delete all logs and reset sequence
                console.print("[yellow]🔄 Resetting database (--force specified)...[/]")

                # Try HTTP API first if app is running
                try:
                    stats_url = detect_devtrack_endpoint(timeout=0.5)
                    if stats_url:
                        delete_url = stats_url.replace("/stats", "/logs?all_logs=true")
                        console.print("[dim]App is running, using HTTP API...[/]")

                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console,
                        ) as progress:
                            task = progress.add_task(
                                "Resetting database via API...", total=None
                            )
                            response = requests.delete(delete_url, timeout=10)
                            progress.update(
                                task, description="✅ Database reset successfully!"
                            )

                        if response.status_code == 200:
                            result = response.json()
                            deleted_count = result.get("deleted_count", 0)
                            console.print(
                                f"[bold green]✅ Database reset complete via API. "
                                f"Deleted {deleted_count} log entries.[/]"
                            )
                            console.print(
                                "[dim]   Note: Sequence will reset automatically "
                                "on next insert[/]"
                            )
                            raise typer.Exit(0)
                        else:
                            console.print(
                                f"[yellow]API returned status {response.status_code}, "
                                f"trying direct access...[/]"
                            )
                except typer.Exit:
                    # Re-raise typer.Exit to allow proper exit
                    raise
                except requests.RequestException:
                    # App not running or API not available - continue to direct access
                    pass
                except Exception as e:
                    console.print(
                        f"[yellow]API call failed: {e}, trying direct access...[/]"
                    )
                    pass

                # Direct database access to delete logs and reset sequence
                try:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Resetting database...", total=None)
                        db_reset = DevTrackDB(db_path, read_only=False)
                        deleted_count = db_reset.delete_all_logs()
                        db_reset.reset_sequence()
                        db_reset.close()
                        progress.update(
                            task, description="✅ Database reset successfully!"
                        )

                    console.print(
                        f"[bold green]✅ Database reset complete. "
                        f"Deleted {deleted_count} log entries and reset sequence.[/]"
                    )
                    raise typer.Exit(0)
                except duckdb.IOException as e:
                    error_msg = str(e)
                    lock_info = parse_lock_error(error_msg)

                    if lock_info["is_lock_error"]:
                        console.print(
                            "[red]❌ Database is locked by another process[/]"
                        )
                        if lock_info["pid"]:
                            pid = lock_info["pid"]
                            console.print(f"[yellow]   Locked by process: PID {pid}[/]")
                        console.print(
                            "[yellow]💡 Stop your application and try again[/]"
                        )
                    else:
                        console.print(f"[red]❌ Failed to reset database:[/] {e}")
                    raise typer.Exit(1)
                except Exception as e:
                    console.print(f"[red]❌ Failed to reset database:[/] {e}")
                    raise typer.Exit(1)

            if force:
                force_initialize_database()
            else:
                # No force - just show that it's already initialized
                console.print(
                    f"[bold green]✅ Database already initialized at:[/] {db_path}, \
                        if you want to reset it, run `devtrack reset`[/]"
                )

                # Show database info
                try:
                    db_info = DevTrackDB(db_path, read_only=True)
                    stats = db_info.get_stats_summary()
                    db_info.close()

                    table = Table(title="Database Information", border_style="green")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="green")
                    table.add_row("Database Path", db_path)
                    table.add_row("Total Requests", str(stats.get("total_requests", 0)))
                    table.add_row(
                        "Unique Endpoints", str(stats.get("unique_endpoints", 0))
                    )
                    avg_duration = stats.get("avg_duration_ms", 0) or 0
                    table.add_row("Average Duration", f"{avg_duration:.2f} ms")
                    console.print(table)
                except Exception:
                    pass  # Ignore errors when showing info

                raise typer.Exit(0)
        db_readonly.close()
    except typer.Exit:
        # Re-raise typer.Exit to allow proper exit
        raise
    except duckdb.IOException:
        # Can't open read-only - might be locked, but continue to try write
        pass
    except Exception:
        # Other errors - continue to try write
        pass

    # Check if tables exist before trying to create them
    # (This handles the case where tables exist but we couldn't check
    # read-only due to lock)
    tables_already_exist = False
    try:
        db_check = DevTrackDB(db_path, read_only=True)
        tables_already_exist = db_check.tables_exist()
        db_check.close()
        if tables_already_exist and not force:
            # Tables exist and no force - already initialized
            console.print(
                f"[bold green]✅ Database already initialized at:[/] {db_path}, \
                if you want to reset it, run `devtrack reset`[/]"
            )
            raise typer.Exit(0)
    except (duckdb.IOException, Exception):
        # Can't check - might be locked, try API check before asking overwrite
        pass

    # Before asking to overwrite, check if database is initialized via API
    # (This prevents asking to overwrite when app is running and DB is initialized)
    if os.path.exists(db_path) and not force:
        # Try to check via API first if database file exists but we couldn't access it
        if check_db_initialized_via_api(console, db_path, timeout=1):
            raise typer.Exit(0)

        # Only ask overwrite if we couldn't determine initialization status via API
        if not Confirm.ask(f"Database '{db_path}' already exists. Overwrite?"):
            console.print("[yellow]Initialization cancelled.[/]")
            raise typer.Exit(0)

    # Step 2: Try write mode to create tables
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing database...", total=None)
            db = init_db(db_path, read_only=False)
            progress.update(task, description="✅ Database initialized successfully!")

        console.print(f"[bold green]✅ DevTrack database initialized at:[/] {db_path}")

        # Show database info
        stats = db.get_stats_summary()
        table = Table(title="Database Information", border_style="green")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Database Path", db_path)
        table.add_row("Total Requests", str(stats.get("total_requests", 0)))
        table.add_row("Unique Endpoints", str(stats.get("unique_endpoints", 0)))
        avg_duration = stats.get("avg_duration_ms", 0) or 0
        table.add_row("Average Duration", f"{avg_duration:.2f} ms")

        console.print(table)
        db.close()

    except duckdb.IOException as e:
        error_msg = str(e)
        lock_info = parse_lock_error(error_msg)

        if lock_info["is_lock_error"]:
            console.print("[yellow]⚠️  Cannot create tables (database is locked)[/]")
            if lock_info["pid"]:
                console.print(f"[dim]   Locked by process: PID {lock_info['pid']}[/]")

            # Try to check if database is already initialized via HTTP API
            console.print(
                "[dim]   Checking if database is already initialized via API...[/]"
            )
            if check_db_initialized_via_api(console, db_path, timeout=2):
                raise typer.Exit(0)

            console.print(
                "[dim]   Your application may auto-initialize on first request[/]"
            )
            console.print("[dim]   Or stop the app and run this command again[/]")
            # Don't fail - let app handle initialization
            raise typer.Exit(0)
        else:
            console.print(f"[red]❌ Failed to initialize database:[/] {e}")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize database:[/] {e}")
        raise typer.Exit(1)


@app.command()
def reset(
    db_path: str = typer.Option("devtrack_logs.db", help="Path to the database file"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """🗑️ Reset the DevTrack database (delete all logs)."""
    console = Console()

    if not os.path.exists(db_path):
        console.print(f"[yellow]Database '{db_path}' does not exist.[/]")
        raise typer.Exit(0)

    if not confirm:
        if not Confirm.ask(
            f"Are you sure you want to reset database '{db_path}'? "
            f"This will delete all logs."
        ):
            console.print("[yellow]Reset cancelled.[/]")
            raise typer.Exit(0)

    # Step 1: Try to use HTTP API if app is running
    try:
        stats_url = detect_devtrack_endpoint(timeout=0.5)
        if stats_url:
            # App is running - use HTTP API
            delete_url = stats_url.replace("/stats", "/logs?all_logs=true")
            console.print("[dim]App is running, using HTTP API...[/]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Resetting database via API...", total=None)
                response = requests.delete(delete_url, timeout=10)
                progress.update(task, description="✅ Database reset successfully!")

            if response.status_code == 200:
                result = response.json()
                deleted_count = result.get("deleted_count", 0)
                console.print(
                    f"[bold green]✅ Database reset complete via API. "
                    f"Deleted {deleted_count} log entries.[/]"
                )
                raise typer.Exit(0)
            else:
                status = response.status_code
                console.print(
                    f"[yellow]API returned status {status}, "
                    f"trying direct access...[/]"
                )
    except requests.RequestException:
        # App not running or API not available - continue to direct access
        pass
    except typer.Exit:
        # Re-raise typer.Exit to allow proper exit
        raise
    except Exception as e:
        console.print(f"[yellow]API call failed: {e}, trying direct access...[/]")
        pass

    # Step 2: Direct database access (app not running or API failed)
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Resetting database...", total=None)
            db = DevTrackDB(db_path, read_only=False)
            deleted_count = db.delete_all_logs()
            db.close()
            progress.update(task, description="✅ Database reset successfully!")

        console.print(
            f"[bold green]✅ Database reset complete. "
            f"Deleted {deleted_count} log entries.[/]"
        )

    except duckdb.IOException as e:
        error_msg = str(e)
        lock_info = parse_lock_error(error_msg)

        if lock_info["is_lock_error"]:
            console.print("[red]❌ Database is locked by another process[/]")
            if lock_info["pid"]:
                console.print(
                    f"[yellow]   Locked by process: PID {lock_info['pid']}[/]"
                )

            console.print("\n[bold yellow]💡 Solutions:[/]")
            console.print(
                "   1. [cyan]Stop your application[/] (the process holding the lock)"
            )
            console.print("   2. [cyan]Then run this command again[/]")
            console.print("   3. [cyan]Or use the HTTP API endpoint:[/]")
            try:
                stats_url = detect_devtrack_endpoint()
                if stats_url:
                    delete_url = stats_url.replace("/stats", "/logs?all_logs=true")
                    console.print(f"      [dim]DELETE {delete_url}[/]")
            except Exception:
                pass
        else:
            console.print(f"[red]❌ Failed to reset database:[/] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to reset database:[/] {e}")
        raise typer.Exit(1)


@app.command()
def export(
    output_file: str = typer.Option("devtrack_export.json", help="Output file path"),
    db_path: str = typer.Option("devtrack_logs.db", help="Path to the database file"),
    format: str = typer.Option("json", help="Export format: json, csv"),
    limit: Optional[int] = typer.Option(None, help="Limit number of entries to export"),
    path_pattern: Optional[str] = typer.Option(None, help="Filter by path pattern"),
    status_code: Optional[int] = typer.Option(None, help="Filter by status code"),
):
    """📤 Export DevTrack logs to JSON or CSV file with filtering options."""
    console = Console()

    if not os.path.exists(db_path):
        console.print(f"[red]Database '{db_path}' does not exist.[/]")
        raise typer.Exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Exporting logs...", total=None)

            db = DevTrackDB(db_path, read_only=True)

            # Get logs based on filters
            if path_pattern:
                entries = db.get_logs_by_path(path_pattern, limit)
            elif status_code:
                entries = db.get_logs_by_status_code(status_code, limit)
            else:
                entries = db.get_all_logs(limit)

            progress.update(task, description="Writing to file...")

            if format.lower() == "json":
                # Convert datetime objects to ISO format strings for JSON serialization
                def json_serializer(obj):
                    """JSON serializer for objects not serializable by default."""
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")

                with open(output_file, "w") as f:
                    json.dump(
                        {
                            "export_timestamp": datetime.now().isoformat(),
                            "total_entries": len(entries),
                            "filters": {
                                "limit": limit,
                                "path_pattern": path_pattern,
                                "status_code": status_code,
                            },
                            "entries": entries,
                        },
                        f,
                        indent=2,
                        default=json_serializer,
                    )
            elif format.lower() == "csv":
                import csv

                if entries:
                    with open(output_file, "w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=entries[0].keys())
                        writer.writeheader()
                        writer.writerows(entries)

            progress.update(task, description="✅ Export complete!")

        console.print(
            f"[bold green]✅ Exported {len(entries)} entries to:[/] " f"{output_file}"
        )

    except Exception as e:
        console.print(f"[red]❌ Failed to export logs:[/] {e}")
        raise typer.Exit(1)


@app.command()
def query(
    db_path: str = typer.Option("devtrack_logs.db", help="Path to the database file"),
    path_pattern: Optional[str] = typer.Option(None, help="Filter by path pattern"),
    status_code: Optional[int] = typer.Option(None, help="Filter by status code"),
    method: Optional[str] = typer.Option(None, help="Filter by HTTP method"),
    limit: Optional[int] = typer.Option(50, help="Limit number of results"),
    days: Optional[int] = typer.Option(None, help="Show logs from last N days"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
):
    """🔍 Query DevTrack logs with advanced filtering and search capabilities."""
    console = Console()

    if not os.path.exists(db_path):
        console.print(f"[red]Database '{db_path}' does not exist.[/]")
        raise typer.Exit(1)

    entries = None
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Querying logs...", total=None)

            db = DevTrackDB(db_path, read_only=True)

            # Get logs based on filters
            if path_pattern:
                entries = db.get_logs_by_path(path_pattern, limit)
            elif status_code:
                entries = db.get_logs_by_status_code(status_code, limit)
            else:
                entries = db.get_all_logs(limit)

            db.close()

            # Apply additional filters
            if method:
                entries = [
                    e for e in entries if e.get("method", "").upper() == method.upper()
                ]

            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                entries = [
                    e
                    for e in entries
                    if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                    >= cutoff_date
                ]

            progress.update(task, description="✅ Query complete!")
    except duckdb.IOException as e:
        # Database is locked - try HTTP endpoint as fallback
        error_msg = str(e)
        if "lock" in error_msg.lower() or "conflicting" in error_msg.lower():
            console.print("[yellow]⚠️  Database is locked by another process.[/]")
            console.print("[dim]   Attempting to fetch logs via HTTP endpoint...[/]")
            try:
                stats_url = detect_devtrack_endpoint(timeout=2)
                if stats_url:
                    with console.status("[bold cyan]Fetching logs from DevTrack...[/]"):
                        response = requests.get(stats_url, timeout=5)
                        response.raise_for_status()
                        data = response.json()
                        entries = data.get("entries", [])

                        # Apply filters to API data
                        if path_pattern:
                            entries = [
                                e
                                for e in entries
                                if path_pattern.lower()
                                in e.get("path_pattern", e.get("path", "")).lower()
                            ]

                        if status_code:
                            entries = [
                                e
                                for e in entries
                                if e.get("status_code") == status_code
                            ]

                        if method:
                            entries = [
                                e
                                for e in entries
                                if e.get("method", "").upper() == method.upper()
                            ]

                        if days:
                            cutoff_date = datetime.now() - timedelta(days=days)
                            entries = [
                                e
                                for e in entries
                                if datetime.fromisoformat(
                                    e["timestamp"].replace("Z", "+00:00")
                                )
                                >= cutoff_date
                            ]

                        # Apply limit after all filters
                        if limit:
                            entries = entries[:limit]

                        console.print(
                            "[green]✅ Successfully fetched logs via HTTP endpoint[/]"
                        )
            except Exception as endpoint_error:
                console.print(f"[red]❌ Failed to query database:[/] {e}")
                console.print(
                    f"[red]❌ Also failed to fetch via HTTP endpoint:[/] "
                    f"{endpoint_error}"
                )
                console.print(
                    "[yellow]💡 Tip: Ensure your application is running "
                    "and accessible[/]"
                )
                raise typer.Exit(1)
        else:
            # Other IOException - re-raise
            console.print(f"[red]❌ Failed to query database:[/] {e}")
            raise typer.Exit(1)
    except typer.Exit:
        # Re-raise typer.Exit to allow proper exit
        raise
    except Exception as e:
        console.print(f"[red]❌ Failed to query logs:[/] {e}")
        raise typer.Exit(1)

    if not entries:
        console.print("[yellow]No logs found matching the criteria.[/]")
        return

    # Display results
    console.rule("[bold green]📊 Query Results[/]", style="green")

    if verbose:
        # Detailed view
        for i, entry in enumerate(entries[:10], 1):  # Show first 10 in detail
            panel = Panel(
                f"[bold]Path:[/] {entry.get('path', 'N/A')}\n"
                f"[bold]Method:[/] {entry.get('method', 'N/A')}\n"
                f"[bold]Status:[/] {entry.get('status_code', 'N/A')}\n"
                f"[bold]Duration:[/] {entry.get('duration_ms', 0):.2f} ms\n"
                f"[bold]Timestamp:[/] {entry.get('timestamp', 'N/A')}\n"
                f"[bold]Client IP:[/] {entry.get('client_ip', 'N/A')}\n"
                f"[bold]User Agent:[/] {entry.get('user_agent', 'N/A')[:50]}...",
                title=f"Entry {i}",
                border_style="blue",
            )
            console.print(panel)
    else:
        # Table view
        table = Table(
            title=f"Query Results ({len(entries)} entries)", border_style="blue"
        )
        table.add_column("Path", style="cyan", no_wrap=True)
        table.add_column("Method", style="green")
        table.add_column("Status", justify="center", style="yellow")
        table.add_column("Duration (ms)", justify="right", style="magenta")
        table.add_column("Timestamp", style="dim")

        for entry in entries[:limit]:
            table.add_row(
                entry.get("path", "N/A"),
                entry.get("method", "N/A"),
                str(entry.get("status_code", "N/A")),
                f"{entry.get('duration_ms', 0):.2f}",
                entry.get("timestamp", "N/A")[:19],  # Show only date and time
            )

        console.print(table)

    console.print(f"[bold green]📊 Total results:[/] {len(entries)}")


@app.command()
def stat(
    top: int = typer.Option(None, help="Show top N endpoints"),
    sort_by: str = typer.Option("hits", help="Sort by 'hits' or 'latency'"),
    db_path: str = typer.Option("devtrack_logs.db", help="Path to the database file"),
    use_endpoint: bool = typer.Option(
        False, "--endpoint", "-e", help="Use HTTP endpoint instead of database"
    ),
):
    """📈 Display comprehensive API statistics and endpoint usage analytics."""
    console = Console()
    console.rule("[bold green]📊 DevTrack Stats CLI[/]", style="green")

    entries = None
    if use_endpoint:
        # Use HTTP endpoint
        stats_url = detect_devtrack_endpoint()

        with console.status("[bold cyan]Fetching stats from DevTrack...[/]"):
            try:
                response = requests.get(stats_url)
                response.raise_for_status()
                data = response.json()
                entries = data.get("entries", [])
            except Exception as e:
                console.print(f"[red]❌ Failed to fetch stats from {stats_url}[/]\n{e}")
                raise typer.Exit(1)
    else:
        # Try database first, fallback to HTTP endpoint if locked
        if not os.path.exists(db_path):
            console.print(f"[red]Database '{db_path}' does not exist.[/]")
            raise typer.Exit(1)

        try:
            db = DevTrackDB(db_path, read_only=True)
            entries = db.get_all_logs()
            db.close()
        except duckdb.IOException as e:
            # Database is locked - try HTTP endpoint as fallback
            error_msg = str(e)
            if "lock" in error_msg.lower() or "conflicting" in error_msg.lower():
                console.print("[yellow]⚠️  Database is locked by another process.[/]")
                console.print(
                    "[dim]   Attempting to fetch stats via HTTP endpoint...[/]"
                )
                try:
                    stats_url = detect_devtrack_endpoint()
                    with console.status(
                        "[bold cyan]Fetching stats from DevTrack...[/]"
                    ):
                        response = requests.get(stats_url, timeout=5)
                        response.raise_for_status()
                        data = response.json()
                        entries = data.get("entries", [])
                        console.print(
                            "[green]✅ Successfully fetched stats via HTTP endpoint[/]"
                        )
                except Exception as endpoint_error:
                    console.print(f"[red]❌ Failed to read database:[/] {e}")
                    console.print(
                        f"[red]❌ Also failed to fetch via HTTP endpoint:[/] "
                        f"{endpoint_error}"
                    )
                    console.print(
                        "[yellow]💡 Tip: Use `devtrack stat --endpoint` "
                        "when your app is running[/]"
                    )
                    raise typer.Exit(1)
            else:
                # Other IOException - re-raise
                console.print(f"[red]❌ Failed to read database:[/] {e}")
                raise typer.Exit(1)
        except typer.Exit:
            # Re-raise typer.Exit to allow proper exit
            raise
        except Exception as e:
            console.print(f"[red]❌ Failed to read database:[/] {e}")
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

    from collections import defaultdict

    average_stats = defaultdict(lambda: {"hits": 0, "total_latency": 0.0})

    for entry in entries:
        path = entry.get("path_pattern", entry.get("path", ""))
        method = entry.get("method", "")
        key = (path, method)
        average_stats[key]["hits"] += 1
        average_stats[key]["total_latency"] += entry.get("duration_ms", 0)

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
    if Confirm.ask("💾 Would you like to export these stats as JSON?", default=False):
        file_path = Prompt.ask("Enter file path", default="devtrack_stats.json")
        try:
            with open(file_path, "w") as f:
                json.dump(entries, f, indent=2)
            console.print(f"[bold green]✅ Exported to {file_path}[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed to write file: {e}[/]")


# @app.command()
# def config(
#     action: str = typer.Argument(..., help="Action: 'show', 'set', 'reset'"),
#     key: Optional[str] = typer.Option(None, help="Configuration key"),
#     value: Optional[str] = typer.Option(None, help="Configuration value"),
#     config_file: str = typer.Option("devtrack.json", help="Configuration file path")
# ):
#     """⚙️ Manage DevTrack configuration settings and preferences."""
#     console = Console()

#     config_path = Path(config_file)

#     if action == "show":
#         if config_path.exists():
#             try:
#                 with open(config_path, 'r') as f:
#                     config_data = json.load(f)

#                 table = Table(title="DevTrack Configuration", border_style="green")
#                 table.add_column("Key", style="cyan")
#                 table.add_column("Value", style="green")

#                 for k, v in config_data.items():
#                     table.add_row(k, str(v))

#                 console.print(table)
#             except Exception as e:
#                 console.print(f"[red]❌ Failed to read config:[/] {e}")
#         else:
#             console.print(
#                 f"[yellow]Configuration file '{config_file}' does not exist.[/]"
#             )

#     elif action == "set":
#         if not key or not value:
#             console.print(
#                 "[red]❌ Both key and value are required for 'set' action.[/]"
#             )
#             raise typer.Exit(1)

#         # Load existing config or create new
#         config_data = {}
#         if config_path.exists():
#             try:
#                 with open(config_path, 'r') as f:
#                     config_data = json.load(f)
#             except Exception as e:
#                 console.print(
#                     f"[yellow]Warning: Could not read existing config: {e}[/]"
#                 )

#         # Set the value
#         config_data[key] = value

#         # Save config
#         try:
#             with open(config_path, 'w') as f:
#                 json.dump(config_data, f, indent=2)
#             console.print(f"[bold green]✅ Set {key} = {value}[/]")
#         except Exception as e:
#             console.print(f"[red]❌ Failed to save config:[/] {e}")
#             raise typer.Exit(1)

#     elif action == "reset":
#         if config_path.exists():
#             if Confirm.ask(
#                 f"Are you sure you want to reset configuration file '{config_file}'?"
#             ):
#                 try:
#                     config_path.unlink()
#                     console.print(
#                         f"[bold green]✅ Configuration file "
#                         f"'{config_file}' deleted.[/]"
#                     )
#                 except Exception as e:
#                     console.print(f"[red]❌ Failed to delete config:[/] {e}")
#                     raise typer.Exit(1)
#             else:
#                 console.print("[yellow]Reset cancelled.[/]")
#         else:
#             console.print(
#                 f"[yellow]Configuration file '{config_file}' does not exist.[/]"
#             )

#     else:
#         console.print(f"[red]❌ Unknown action: {action}[/]")
#         console.print("Available actions: show, set, reset")
#         raise typer.Exit(1)


@app.command()
def health(
    db_path: str = typer.Option("devtrack_logs.db", help="Path to the database file"),
    endpoint: bool = typer.Option(
        False, "--endpoint", "-e", help="Check HTTP endpoint health"
    ),
):
    """🏥 Check DevTrack system health and component status."""
    console = Console()
    console.rule("[bold green]🏥 DevTrack Health Check[/]", style="green")

    health_status = {"status": "healthy", "checks": []}

    # Check database
    if os.path.exists(db_path):
        try:
            db = DevTrackDB(db_path, read_only=True)
            stats = db.get_stats_summary()
            health_status["checks"].append(
                {
                    "component": "Database",
                    "status": "✅ Healthy",
                    "details": f"Total requests: " f"{stats.get('total_requests', 0)}",
                }
            )
        except Exception as e:
            health_status["checks"].append(
                {
                    "component": "Database",
                    "status": "❌ Unhealthy",
                    "details": str(e),
                }
            )
            health_status["status"] = "unhealthy"
    else:
        health_status["checks"].append(
            {
                "component": "Database",
                "status": "⚠️ Not Found",
                "details": f"Database file '{db_path}' does not exist",
            }
        )

    # Check HTTP endpoint if requested
    if endpoint:
        try:
            stats_url = detect_devtrack_endpoint()
            response = requests.get(stats_url, timeout=5)
            if response.status_code == 200:
                health_status["checks"].append(
                    {
                        "component": "HTTP Endpoint",
                        "status": "✅ Healthy",
                        "details": f"Endpoint: {stats_url}",
                    }
                )
            else:
                health_status["checks"].append(
                    {
                        "component": "HTTP Endpoint",
                        "status": "❌ Unhealthy",
                        "details": f"HTTP {response.status_code}",
                    }
                )
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["checks"].append(
                {
                    "component": "HTTP Endpoint",
                    "status": "❌ Unreachable",
                    "details": str(e),
                }
            )
            health_status["status"] = "unhealthy"

    # Display results
    table = Table(
        title="Health Check Results",
        border_style="green" if health_status["status"] == "healthy" else "red",
    )
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    for check in health_status["checks"]:
        table.add_row(check["component"], check["status"], check["details"])

    console.print(table)

    # Overall status
    if health_status["status"] == "healthy":
        console.print("[bold green]🎉 All systems are healthy![/]")
    else:
        console.print(
            "[bold red]⚠️ Some issues detected. Please check the details above.[/]"
        )
        raise typer.Exit(1)


def show_help():
    """Display enhanced help information."""
    console = Console()

    # Header
    console.print(
        "[bold blue]🚀 DevTrack CLI[/] - "
        "[dim]Comprehensive request tracking and analytics toolkit[/]"
    )
    console.print()

    # Quick start
    console.print("[bold green]Quick Start:[/]")
    console.print("  [cyan]devtrack init[/]     # Initialize database")
    console.print("  [cyan]devtrack stat[/]     # View statistics")
    console.print()

    # Commands overview
    console.print("[bold green]Available Commands:[/]")

    commands_table = Table(show_header=False, box=None, padding=(0, 1))
    commands_table.add_column("Command", style="cyan", no_wrap=True)
    commands_table.add_column("Description", style="dim")

    commands_table.add_row("version", "📦 Show SDK version and build information")
    commands_table.add_row(
        "init", "🗄️ Initialize a new DevTrack database with DuckDB backend"
    )
    commands_table.add_row("reset", "🗑️ Reset the DevTrack database (delete all logs)")
    commands_table.add_row(
        "export", "📤 Export DevTrack logs to JSON or CSV file with filtering"
    )
    commands_table.add_row(
        "query", "🔍 Query DevTrack logs with advanced filtering and search"
    )
    commands_table.add_row(
        "stat", "📈 Display comprehensive API statistics and endpoint analytics"
    )
    commands_table.add_row(
        "health", "🏥 Check DevTrack system health and component status"
    )

    console.print(commands_table)
    console.print()

    # Examples
    console.print("[bold green]Examples:[/]")
    console.print("  [dim]# Initialize database[/]")
    console.print("  [cyan]devtrack init --force[/]")
    console.print()
    console.print("  [dim]# Query logs with filters[/]")
    console.print("  [cyan]devtrack query --status-code 404 --days 7 --verbose[/]")
    console.print()
    console.print("  [dim]# Export logs[/]")
    console.print("  [cyan]devtrack export --format csv --limit 1000[/]")
    console.print()
    console.print("  [dim]# Health check[/]")
    console.print("  [cyan]devtrack health --endpoint[/]")
    console.print()

    # Help info
    console.print("[bold green]Getting Help:[/]")
    console.print(
        "  [cyan]devtrack COMMAND --help[/]  "
        "[dim]Show detailed help for a specific command[/]"
    )
    console.print()

    # Links
    console.print("[bold green]Resources:[/]")
    console.print(
        "  [dim]GitHub:[/] [blue]https://github.com/mahesh-solanke/devtrack-sdk[/]"
    )


@app.command()
def help():
    """📚 Show comprehensive help and usage information."""
    show_help()


if __name__ == "__main__":
    app()
