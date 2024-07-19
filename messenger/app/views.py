import uuid

from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from .models import EmailVerification, generate_verification_code, UserProfileImage, UserProfile, Chat, Message
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def index(request):
    if request.user.is_authenticated:
        user = request.user
        chats = Chat.objects.filter(participants=user)
        chat_data = []
        for chat in chats:
            other_participants = chat.participants.exclude(id=user.id)
            chat_data.append({
                'chat': chat,
                'other_participants': other_participants
            })
        return render(request, 'app/index.html', {'chat_data': chat_data})
    return render(request, 'app/index.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user)
            code = generate_verification_code()
            EmailVerification.objects.create(user=user, code=code)
            send_mail(
                'Email Verification',
                f'Use this code to verify your email: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return redirect('verify_email')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/register.html', {'form': form})


def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            verification = EmailVerification.objects.get(code=code)
            if verification.is_expired():
                return render(request, 'app/verify_email.html', {'error': 'Verification code expired.'})
            verification.user.is_active = True
            verification.user.save()
            verification.is_verified = True
            verification.save()
            login(request, verification.user)
            return redirect('home')
        except EmailVerification.DoesNotExist:
            return render(request, 'app/verify_email.html', {'error': 'Invalid verification code.'})
    return render(request, 'app/verify_email.html')


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login_page.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    user_profile_images = UserProfileImage.objects.filter(user=user)

    context = {
        'user': user,
        'user_profile': user_profile,
        'user_profile_images': user_profile_images,
    }

    return render(request, 'app/profile.html', context)


def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    user = request.user
    other_participants = chat.participants.exclude(id=user.id)
    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    context = {
        'chat': chat,
        'participants': other_participants,
        'messages': messages,
    }
    return render(request, 'app/index.html', context)


def start_chat(request, user_id):
    user1 = request.user
    user2 = get_object_or_404(User, id=user_id)

    # Check if chat already exists
    chat = Chat.objects.filter(participants=user1).filter(participants=user2).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(user1, user2)

    return redirect('chat_view', chat_id=chat.id)


def search_users(request):
    query = request.GET.get('q')
    users = User.objects.filter(username__icontains=query) if query else []
    return render(request, 'app/search.html', {'users': users, 'query': query})