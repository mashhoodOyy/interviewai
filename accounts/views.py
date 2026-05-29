from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        target_role = request.POST['target_role']
        experience_level = request.POST['experience_level']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return render(request, 'accounts/signup.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            target_role=target_role,
            experience_level=experience_level
        )
        login(request, user)
        messages.success(request, f'Welcome, {username}! 🎉')
        return redirect('dashboard')

    return render(request, 'accounts/signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {username}! 👋')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.target_role = request.POST.get('target_role', '')
        user.target_company = request.POST.get('target_company', '')
        user.experience_level = request.POST.get('experience_level', 'entry')
        if 'resume' in request.FILES:
            user.resume = request.FILES['resume']
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html')