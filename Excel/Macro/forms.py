# forms.py
from django import forms
from .models import UploadedExcel

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedExcel
        fields = ['excel_file', 'folder_name']
