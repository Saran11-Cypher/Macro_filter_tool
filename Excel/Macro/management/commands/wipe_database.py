from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

EXCLUDE_APPS = ['auth', 'contenttypes', 'admin', 'sessions']  # Don't wipe these apps

class Command(BaseCommand):
    help = "Wipe all non-auth app data and reset auto-increment IDs (for SQLite only)."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            self.stdout.write(self.style.WARNING("Disabling foreign key checks..."))
            cursor.execute("PRAGMA foreign_keys = OFF;")

            for model in apps.get_models():
                app_label = model._meta.app_label
                table = model._meta.db_table

                if app_label in EXCLUDE_APPS:
                    self.stdout.write(self.style.NOTICE(f"⏭ Skipping {table} (app: {app_label})"))
                    continue

                try:
                    cursor.execute(f'DELETE FROM "{table}";')
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s;", [table])
                    self.stdout.write(self.style.SUCCESS(f"✔ Cleared and reset ID for {table}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"⚠ Skipped {table}: {e}"))

            cursor.execute("PRAGMA foreign_keys = ON;")
            self.stdout.write(self.style.SUCCESS("✅ Wipe complete. User data preserved."))
