from django.urls import path
from .views import upload_excel
from .models import StoredExcel
from django.contrib import admin
urlpatterns = [
    path("upload_excel_format/", upload_excel, name="upload_excel"),
]

@admin.register(StoredExcel)
class StoredExcelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "folder_name", "uploaded_at")

