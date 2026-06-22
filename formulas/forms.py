from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Formula, Category

class RegisterForm(UserCreationForm):
    email= forms.EmailField(required=True)

    class Meta:
        model=User
        fields={"username", "email", "password1", "password2"}




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
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
            'question', 'answer', 'solve', 'correct_answer',
            'explanation', 'form_info', 'category', 'is_saved'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Newton\'s Second Law'}),
            'form': forms.TextInput(attrs={'placeholder': 'e.g. F = ma'}),
            'chapter': forms.TextInput(attrs={'placeholder': 'e.g. Laws of Motion'}),
            'description': forms.TextInput(attrs={'placeholder': 'Short description...'}),
            'given_by': forms.TextInput(attrs={'placeholder': 'e.g. Isaac Newton'}),
            'question': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Practice question...'}),
            'answer': forms.TextInput(attrs={'placeholder': 'e.g. 10 N'}),
            'solve': forms.TextInput(attrs={'placeholder': 'Steps to solve...'}),
            'correct_answer': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Full correct answer...'}),
            'form_info': forms.TextInput(attrs={'placeholder': 'Extra formula info...'}),
        }
