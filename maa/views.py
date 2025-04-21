from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import WomanRegistrationForm, WomanLoginForm

def register(request):
    if request.method == 'POST':
        form = WomanRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')  # You'll need to create this URL later
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = WomanRegistrationForm()
    return render(request, 'maa/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = WomanLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')  # You'll need to create this URL later
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = WomanLoginForm()
    return render(request, 'maa/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')