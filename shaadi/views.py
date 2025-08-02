from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, ProfileForm
from .models import CustomUser ,Conversation, Message
from django.db.models import Q
from django.utils import timezone


def home(request):
    return render(request, 'shaadi/index.html')

def about(request):
    return render(request, 'shaadi/about.html')

def contact(request):
    return render(request, 'shaadi/contact.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'registration/profile.html', {'form': form})

@login_required
def browse_profiles(request):
    # Exclude current user
    profiles = CustomUser.objects.filter(is_active=True).exclude(id=request.user.id)
    
    # Apply basic filtering based on user preferences
    min_age = request.user.preferred_age_min or 18
    max_age = request.user.preferred_age_max or 99
    
    # Calculate date range for age filtering
    today = date.today()
    min_dob = date(today.year - max_age - 1, today.month, today.day)
    max_dob = date(today.year - min_age, today.month, today.day)
    
    profiles = profiles.filter(
        Q(date_of_birth__gte=min_dob) & 
        Q(date_of_birth__lte=max_dob)
    )
    
    if request.user.preferred_religion:
        profiles = profiles.filter(religion=request.user.preferred_religion)
    
    # Gender filtering (opposite gender)
    if request.user.gender == 'M':
        profiles = profiles.filter(gender='F')
    elif request.user.gender == 'F':
        profiles = profiles.filter(gender='M')
    
    return render(request, 'shaadi/browse_profiles.html', {'profiles': profiles})

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    # Prepare conversation data
    conversation_data = []
    for conversation in conversations:
        other_user = conversation.get_other_participant(request.user)
        unread_count = Message.objects.filter(
            conversation=conversation,
            sender=other_user,
            is_read=False
        ).count()
        
        conversation_data.append({
            'conversation': conversation,
            'other_user': other_user,
            'unread_count': unread_count
        })
    
    return render(request, 'shaadi/inbox.html', {'conversations': conversation_data})

@login_required
def chat(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    # Get or create conversation
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).distinct()
    if conversation.exists():
        conversation = conversation.first()
    else:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('chat', user_id=user_id)
    
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    # Mark messages as read
    messages.filter(sender=other_user, is_read=False).update(is_read=True)
    
    return render(request, 'shaadi/chat.html', {
        'other_user': other_user,
        'messages': messages,
        'conversation': conversation
    })
