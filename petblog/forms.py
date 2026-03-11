# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from petblog.models import Post, Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    # Choices Defined as tuples of (value, display)
    USER_ROLES = [
        (False, 'Reader - I want to read and comment'),
        (True, 'Author - I want to write pet stories'),
    ]
    
    is_author = forms.ChoiceField(
        choices=USER_ROLES, 
        widget=forms.RadioSelect, # Radio buttons blend nicely in lists
        label="I want to join as a:"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            is_auth_choice = self.cleaned_data['is_author'] == 'True'
            user.profile.is_author = is_auth_choice
            user.profile.save()
        return user
    
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'image'] # Add 'category' if you have it!
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet name or title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell the story...'}),
        }