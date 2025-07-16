from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'mobile_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username


from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class EditProfileForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'profile_picture', 'bio', 'resume', 'mobile_number', 
              'intro_video', 
            'career_growth', 'tagline'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write something about yourself...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),  
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}),
            'intro_video': forms.FileInput(attrs={'class': 'form-control'}),
            'career_growth': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your career growth...'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your tagline'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance
        if email != user.email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email






class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'tagline']


from django import forms
from .models import SocialMediaLink

class SocialMediaLinkForm(forms.ModelForm):
    custom_platform = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter custom platform name'
        }),
    )

    class Meta:
        model = SocialMediaLink
        fields = ['platform', 'url', 'is_private']  # Added 'is_private'
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        platform = cleaned_data.get('platform')
        custom_platform = cleaned_data.get('custom_platform')

        if platform == 'Other' and not custom_platform:
            raise forms.ValidationError("Please specify a custom platform name if 'Other' is selected.")
        elif platform != 'Other':
            cleaned_data['custom_platform'] = None  # Clear custom platform if not Other.

        return cleaned_data



class VerifyEmail(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }

