from django.contrib import messages as django_messages
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import ContactMessage
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Post
from .models import Profile
from .models import *
from .forms import PostForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

        
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})

def login(request):
    if request.method == 'POST':
        return render(request, 'home.html')

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_content = request.POST.get('message')

        ContactMessage.objects.create(
            name=name, 
            email=email, 
            message=message_content
        )
        
        try:
            send_mail(
                'New Contact Message',
                f'Name: {name}\nEmail: {email}\nMessage: {message_content}',
                settings.EMAIL_HOST_USER,
                ['adelekanf7@gmail.com'],
                fail_silently=False,
            )

            django_messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')

        except Exception as e:
            django_messages.error(request, 'There was an error sending your email.')
            
    return render(request, 'contact.html')

def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

def switch_roles(request):
    if request.method=='pOST':
        new_role = request.POST.get('role')
        Profile = request.user.profile
        Profile.role = new_role
        Profile.save()
        messages.success(request, f"Role choice updated to {new_role}!")
    return redirect('home.html')

def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'post_detail.html', {'post': post})


@login_required
def create_post(request):
    if not request.user.profile.is_author:
        raise PermissionDenied
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})