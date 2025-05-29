# forms.py
from django import forms
from .models import UploadedExcel

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedExcel
        fields = ['excel_file', 'folder_name']


class HTMLMergeForm(forms.Form):
    num_files = forms.IntegerField(label="Number of HTML files", min_value=1)
    batch_size = forms.IntegerField(label="Files per batch", min_value=1)
    run_id = forms.CharField(label="Run ID", max_length=100)
