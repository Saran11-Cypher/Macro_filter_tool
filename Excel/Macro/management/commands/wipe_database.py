from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

EXCLUDE_APPS = ['auth', 'contenttypes', 'admin', 'sessions']  # Essential system tables

class Command(BaseCommand):
    help = "Wipe all non-auth app data and reset auto-increment IDs (for SQLite only)."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            self.stdout.write(self.style.WARNING("🔒 Disabling foreign key checks..."))
            cursor.execute("PRAGMA foreign_keys = OFF;")

            for model in apps.get_models():
                app_label = model._meta.app_label
                table = model._meta.db_table

                if app_label in EXCLUDE_APPS:
                    self.stdout.write(self.style.NOTICE(f"⏭ Skipping system table: {table}"))
                    continue

                try:
                    self.stdout.write(self.style.NOTICE(f"🗑 Deleting all data from: {table}"))
                    cursor.execute(f'DELETE FROM "{table}";')

                    self.stdout.write(self.style.NOTICE(f"🧹 Resetting auto-increment for: {table}"))
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")

                    self.stdout.write(self.style.SUCCESS(f"✔ Cleared and reset: {table}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"⚠ Error with {table}: {e}"))

            cursor.execute("PRAGMA foreign_keys = ON;")
            self.stdout.write(self.style.SUCCESS("✅ Database wipe and reset complete."))
