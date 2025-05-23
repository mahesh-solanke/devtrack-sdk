from typer.testing import CliRunner

from devtrack_sdk.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DevTrack SDK v" in result.output


def test_stat_help():
    result = runner.invoke(app, ["stat", "--help"])
    assert result.exit_code == 0
    assert "Show top N endpoints" in result.output
