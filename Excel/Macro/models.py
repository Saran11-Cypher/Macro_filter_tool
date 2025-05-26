from django.db import models, connection
from django.contrib.auth import get_user_model
import json
from django.utils.timezone import now
from datetime import datetime
User = get_user_model()



class StoredExcel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    data = models.TextField(null=True, blank=True)  # Store Excel as JSON text
    folder_name = models.CharField(max_length=255)  # Folder where user wants to save
    uploaded_at = models.DateTimeField(default=now)  # Timestamp

    def save_excel_data(self, excel_data):
        """Convert Excel data to JSON before saving."""
        self.data = json.dumps(excel_data)
        self.save()

    def get_excel_data(self):
        try:
            data = json.loads(self.data)
            # Make sure we're returning the correct structure
            if isinstance(data, dict):
                return data  # multi-sheet
            else:
                return {"Sheet1": data}  # fallback to single-sheet
        except json.JSONDecodeError:
            return {"Sheet1": []}

    def __str__(self):
        return f"Excel File in {self.folder_name} by {self.user.username}"

class UploadedExcel(models.Model):
    id = models.IntegerField(primary_key=True) 
    folder_name = models.CharField(max_length=255)
    excel_file = models.FileField(upload_to='uploads/%Y/%m/%d/%H-%M-%S/', blank=True, null=True, max_length=1000)
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=datetime.now)
    timestamp = models.DateTimeField(default=now)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Processed')
    stored_excel = models.ForeignKey(StoredExcel, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM Macro_uploadedexcel ORDER BY id;")
                existing_ids = [row[0] for row in cursor.fetchall()]
                new_id = 1
                for eid in existing_ids:
                    if new_id < eid:
                        break
                    new_id += 1
                self.id = new_id  # Assign the lowest available ID
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.excel_file.name} - {self.uploaded_by.username}"

class ExcelFile(models.Model):
    file = models.FileField(upload_to="excel_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)