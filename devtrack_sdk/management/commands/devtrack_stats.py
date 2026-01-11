import json

from django.conf import settings
from django.core.management.base import BaseCommand

from devtrack_sdk.database import DevTrackDB


class Command(BaseCommand):
    help = "Show DevTrack statistics from DuckDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-path",
            type=str,
            help="Path to the database file",
            default=getattr(settings, "DEVTRACK_DB_PATH", "devtrack_logs.db"),
        )
        parser.add_argument(
            "--limit", type=int, help="Limit number of entries to show", default=10
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["table", "json"],
            help="Output format",
            default="table",
        )

    def handle(self, *args, **options):
        db_path = options["db_path"]
        limit = options["limit"]
        output_format = options["format"]

        try:
            db = DevTrackDB(db_path, read_only=True)
            stats = db.get_stats_summary()
            recent_logs = db.get_all_logs(limit=limit)

            if output_format == "json":
                self.stdout.write(
                    json.dumps({"summary": stats, "recent_logs": recent_logs}, indent=2)
                )
            else:
                # Table format
                self.stdout.write("\n📊 DevTrack Statistics")
                self.stdout.write("=" * 50)
                self.stdout.write(f"Database Path: {db_path}")
                self.stdout.write(f'Total Requests: {stats.get("total_requests", 0)}')
                self.stdout.write(
                    f'Unique Endpoints: {stats.get("unique_endpoints", 0)}'
                )
                avg_duration = stats.get("avg_duration_ms", 0) or 0
                self.stdout.write(f"Average Duration: {avg_duration:.2f} ms")
                success_rate = (
                    stats.get("success_count", 0)
                    / max(stats.get("total_requests", 1), 1)
                    * 100
                )
                self.stdout.write(f"Success Rate: {success_rate:.1f}%")

                if recent_logs:
                    self.stdout.write("\n📋 Recent Logs")
                    self.stdout.write("-" * 50)
                    for log in recent_logs:
                        self.stdout.write(
                            f'{log["timestamp"][:19]} | '
                            f'{log["method"]} {log["path"]} | '
                            f'{log["status_code"]} | '
                            f'{log["duration_ms"]:.2f}ms'
                        )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading database: {e}"))
