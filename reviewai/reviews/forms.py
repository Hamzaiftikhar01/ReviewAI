from django import forms
from .models import Review

class ReviewManualForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['customer_name', 'customer_email', 'rating', 'review_text', 'source']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ali Khan'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ali@example.com (optional)'}),
            'rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)], attrs={'class': 'form-select'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write the review content here...'}),
            'source': forms.Select(choices=[('Manual', 'Manual'), ('Google', 'Google'), ('Other', 'Other')], attrs={'class': 'form-select'}),
        }

class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="Select CSV File",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
