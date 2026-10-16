from django.contrib import messages as django_messages
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import ContactMessage
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Post, Profile, Comment, like
from django.shortcuts import get_object_or_404, redirect
from .forms import PostForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.db import transaction
from .forms import CommentForm
from django.http import JsonResponse

# Create your views here.
@transaction.atomic
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
        # no else needed — falls through to render with the invalid form
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

        
def home(request):
    posts = Post.objects.all().prefetch_related('likes', 'comments').order_by('-created_at')
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

def switch_role_view(request):
    if request.method == 'POST':
        new_role = request.POST.get('role').upper()
        profile = request.user.profile
        profile.role = new_role
        profile.save()
        messages.success(request, f"Role successfully updated to {new_role}!")
    return redirect('profile')

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().order_by('-created_at')
    like_count = post.likes.count()
    liked = False
    if request.user.is_authenticated:
        liked = post.likes.filter(id=request.user.id).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.pk)
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'likes': liked,
        'like_count': like_count 
    })
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Using .exists()
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    context = {
        'post': post,
        'likes': liked,
        'like_count': post.likes.count(),
    }
    # To ensure this template ONLY contains the heart icon and the number
    return render(request, 'partials/like_button.html', context)

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