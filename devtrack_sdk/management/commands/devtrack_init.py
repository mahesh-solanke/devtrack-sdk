import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from devtrack_sdk.database import init_db


class Command(BaseCommand):
    help = "Initialize DevTrack DuckDB database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-path",
            type=str,
            help="Path to the database file",
            default=getattr(settings, "DEVTRACK_DB_PATH", "devtrack_logs.db"),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force initialization even if database exists",
        )

    def handle(self, *args, **options):
        db_path = options["db_path"]
        force = options["force"]

        if os.path.exists(db_path) and not force:
            self.stdout.write(
                self.style.WARNING(f'Database "{db_path}" already exists.')
            )
            if input("Overwrite? (y/N): ").lower() != "y":
                self.stdout.write(self.style.WARNING("Initialization cancelled."))
                return

        try:
            self.stdout.write("Initializing DevTrack database...")
            db = init_db(db_path)

            # Show database info
            stats = db.get_stats_summary()

            self.stdout.write(
                self.style.SUCCESS(f"✅ DevTrack database initialized at: {db_path}")
            )

            self.stdout.write(f"Database Path: {db_path}")
            self.stdout.write(f'Total Requests: {stats.get("total_requests", 0)}')
            self.stdout.write(f'Unique Endpoints: {stats.get("unique_endpoints", 0)}')
            self.stdout.write(
                f'Average Duration: {stats.get("avg_duration_ms", 0):.2f} ms'
            )

        except Exception as e:
            raise CommandError(f"Failed to initialize database: {e}")
