from django.contrib import admin
from .models import StoredExcel, UploadedExcel

@admin.register(StoredExcel)
class StoredExcelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "folder_name", "uploaded_at")
    search_fields = ("folder_name", "user__username")
    list_filter = ("uploaded_at",)
    ordering = ("-uploaded_at",)
    readonly_fields = ("uploaded_at",)

@admin.register(UploadedExcel)
class UploadedExcelAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "uploaded_by", "status", "uploaded_at", "folder_name")
    search_fields = ("file_name", "uploaded_by__username", "folder_name")
    list_filter = ("status", "uploaded_at")
    ordering = ("-uploaded_at",)
    readonly_fields = ("uploaded_at", "timestamp")
admin.site.site_header = "DMT Admin Panel"
admin.site.site_title = "DMT Admin"
admin.site.index_title = "Welcome to the Data Management System"
