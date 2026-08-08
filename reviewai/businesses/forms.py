from django import forms
from .models import Business

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'category', 'description', 'location', 'website', 'logo', 'tone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acme Restaurant'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your business...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'London, UK'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'tone': forms.Select(attrs={'class': 'form-select'}),
        }
