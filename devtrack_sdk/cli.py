# devtrack_sdk/cli.py
import typer

from devtrack_sdk import __version__

app = typer.Typer(help="DevTrack CLI toolkit")


@app.command()
def init():
    """Initialize a DevTrack project."""
    typer.echo("🚀 DevTrack project initialized successfully!")


@app.command()
def version():
    """Show the current version."""
    typer.echo(f"DevTrack SDK v{__version__.__version__}")


@app.command()
def generate_config():
    """Generate a default devtrack config file."""
    config = {
        "track_paths": ["/"],
        "exclude_paths": ["/__devtrack__/stats", "/docs", "/openapi.json"],
    }
    import json

    with open("devtrack.config.json", "w") as f:
        json.dump(config, f, indent=2)
    typer.echo("✅ devtrack.config.json created.")


if __name__ == "__main__":
    app()
