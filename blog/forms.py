from django import forms
from .models import UploadFile

TABLE_CHOICES = [
    ('ligandable', 'Ligandable'),
    ('hyperreactive', 'Hyperreactive'),
    ('identified', 'Identified'),
]

class UploadFileForm(forms.ModelForm):
    table = forms.ChoiceField(choices=TABLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required= True)

    class Meta:
        model = UploadFile
        fields = ('table', 'upload')
        widgets = {
            'upload': forms.FileInput(attrs={'class': 'form-control-file'}),
        }