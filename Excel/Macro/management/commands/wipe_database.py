from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = "Wipe all data from the database without dropping tables or affecting migrations."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            self.stdout.write(self.style.WARNING("Disabling foreign key checks..."))
            cursor.execute("PRAGMA foreign_keys = OFF;")  # For SQLite

            for model in apps.get_models():
                table = model._meta.db_table
                try:
                    cursor.execute(f'DELETE FROM "{table}";')
                    self.stdout.write(self.style.SUCCESS(f"✔ Cleared {table}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"⚠ Skipped {table}: {e}"))

            cursor.execute("PRAGMA foreign_keys = ON;")
            self.stdout.write(self.style.WARNING("Re-enabled foreign key checks."))
            self.stdout.write(self.style.SUCCESS("✅ Database wiped successfully."))
