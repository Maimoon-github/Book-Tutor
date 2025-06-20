from django import forms
from .models import Book

class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['pdf']
