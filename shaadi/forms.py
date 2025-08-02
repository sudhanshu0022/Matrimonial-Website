# shaadi/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class DateInput(forms.DateInput):
    input_type = 'date'

class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'gender', 'date_of_birth', 
            'religion', 'phone', 'address', 'bio', 'profession', 'education',
            'profile_picture', 'preferred_age_min', 'preferred_age_max', 
            'preferred_religion'
        ]
        widgets = {
            'date_of_birth': DateInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'religion': forms.Select(attrs={'class': 'form-select'}),
            'preferred_religion': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['gender', 'religion', 'preferred_religion']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

                