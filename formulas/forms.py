from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Formula, Chapter


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['name', 'explain']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Physics'}),
            'explain': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief explanation...'}),
        }

class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        fields = [
            'title', 'form', 'chapter', 'description', 'given_by',
            'example', 'answer', 'variables', 'units',  'is_saved', 'when_to_use'

            ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Newton\'s Second Law'}),
            'form': forms.TextInput(attrs={'placeholder': 'e.g. F = ma'}),
            'chapter': forms.TextInput(attrs={'placeholder': 'e.g. Laws of Motion'}),
            'description': forms.TextInput(attrs={'placeholder': 'Short description...'}),
            'given_by': forms.TextInput(attrs={'placeholder': 'e.g. Isaac Newton'}),
            'question': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Practice question...'}),
            'answer': forms.TextInput(attrs={'placeholder': 'e.g. 10 N'}),
            'variables': forms.TextInput(attrs={'placeholder': 'Extra formula info...'}),
        }
