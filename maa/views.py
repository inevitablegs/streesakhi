from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from .forms import WomanRegistrationForm, WomanLoginForm
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def register(request):
    if request.method == 'POST':
        form = WomanRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            subject = 'Welcome to Streesakhi!'
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [user.email]

            html_content = render_to_string(
                'maa/emails/welcome.html',
                {'user': user}
            )
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject, 
                text_content, 
                from_email, 
                to
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')  # You'll need to create this URL later
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
                return redirect('dashboard')  # You'll need to create this URL later
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = WomanLoginForm()
    return render(request, 'maa/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # You can pass any context you need here
    return render(request, 'maa/dashboard.html', {
        'user': request.user
    })


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm

@login_required
def view_profile(request):
    return render(request, 'maa/profile.html', {
        'user': request.user
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('view_profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'maa/edit_profile.html', {
        'form': form
    })


from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'maa/change_password.html'
    success_url = reverse_lazy('dashboard')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import subprocess


# maa/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import subprocess
import json
import re

@login_required
def pregnancy_video_tool(request):
    results = []
    error = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            try:
                result = subprocess.run(
                    ['python', 'pregnancy_video_agent.py'],
                    input=query.encode('utf-8'),
                    capture_output=True,
                    check=True
                )
                raw_output = result.stdout.decode('utf-8')

                links = re.findall(r'(https?://www\.youtube\.com/watch\?v=[\w-]+)', raw_output)

                # Add thumbnails
                for link in links:
                    video_id = link.split("v=")[-1]
                    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                    results.append({
                        'url': link,
                        'thumbnail': thumbnail_url
                    })

            except subprocess.CalledProcessError as e:
                error = "Agent failed to respond."
            except Exception as e:
                error = f"Error: {str(e)}"
        else:
            error = "Please enter a query."

    return render(request, 'maa/pregnancy_videos.html', {
        'results': results,
        'error': error
    })
 
 
from django.http import JsonResponse

@login_required
def load_more_videos(request):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 3))  # Load 3 at a time

        if not query:
            return JsonResponse({'error': 'Query required.'}, status=400)

        try:
            result = subprocess.run(
                ['python', 'pregnancy_video_agent.py'],
                input=query.encode('utf-8'),
                capture_output=True,
                check=True
            )
            raw_output = result.stdout.decode('utf-8')
            all_links = re.findall(r'(https?://www\.youtube\.com/watch\?v=[\w-]+)', raw_output)

            selected_links = all_links[offset:offset+limit]
            results = []

            for link in selected_links:
                video_id = link.split("v=")[-1]
                thumbnail = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                results.append({
                    'url': link,
                    'thumbnail': thumbnail
                })

            return JsonResponse({'videos': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
