from django import forms
from .models import CV


class CVForm(forms.ModelForm):
    """Form for creating and updating CVs."""
    
    class Meta:
        model = CV
        fields = ['firstname', 'lastname', 'bio', 'skills', 'projects', 'contacts']
        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First Name'
            }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last Name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'List your skills...',
                'rows': 3
            }),
            'projects': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Describe your projects...',
                'rows': 4
            }),
            'contacts': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Your contact information...',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required attribute to all fields
        for field in self.fields.values():
            field.required = False


class CVDeleteForm(forms.Form):
    """Form for confirming CV deletion."""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label="I confirm I want to delete this CV"
    )







