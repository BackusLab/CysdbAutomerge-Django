from django import forms
from .models import UploadFile

TABLE_CHOICES = [
    ('cysdb', 'Cysdb'),
    ('hyperreactive', 'Hyperreactive'),
]

class UploadFileForm(forms.ModelForm):
    table = forms.ChoiceField(choices=TABLE_CHOICES, required=True)
    class Meta:
        model = UploadFile
        fields = ('upload', 'table')
