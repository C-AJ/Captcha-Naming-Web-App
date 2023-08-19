from django import forms
from django.core.exceptions import ValidationError

class SolveCaptcha(forms.Form):
    solution = forms.CharField(label="Solution", max_length=5, min_length=5)

