import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from devtrack_sdk.database import DevTrackDB


class Command(BaseCommand):
    help = "Reset DevTrack DuckDB database (delete all logs)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-path",
            type=str,
            help="Path to the database file",
            default=getattr(settings, "DEVTRACK_DB_PATH", "devtrack_logs.db"),
        )
        parser.add_argument(
            "--yes", action="store_true", help="Skip confirmation prompt"
        )

    def handle(self, *args, **options):
        db_path = options["db_path"]
        skip_confirm = options["yes"]

        if not os.path.exists(db_path):
            self.stdout.write(
                self.style.WARNING(f'Database "{db_path}" does not exist.')
            )
            return

        if not skip_confirm:
            self.stdout.write(
                self.style.WARNING(f'This will delete all logs in "{db_path}".')
            )
            if input("Are you sure? (y/N): ").lower() != "y":
                self.stdout.write(self.style.WARNING("Reset cancelled."))
                return

        try:
            db = DevTrackDB(db_path, read_only=False)
            deleted_count = db.delete_all_logs()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Database reset complete. Deleted {deleted_count} log entries."
                )
            )

        except Exception as e:
            raise CommandError(f"Failed to reset database: {e}")
