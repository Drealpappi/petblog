# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from petblog.models import Post, Profile
from .models import Comment

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
    is_auth_choice = self.cleaned_data.get('is_author')
    
    if commit:
        user.save()
        from .models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = 'AUTHOR' if is_auth_choice == 'True' else 'READER'
        profile.save()
        
    return user
    
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'image'] # Add 'category' if you have it!
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet name or title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell the story...'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'glass-input', # Matching your previous styling
                'placeholder': 'Write a comment...',
                'rows': 3
            }),
        }