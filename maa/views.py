from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from .forms import WomanRegistrationForm, WomanLoginForm
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.youtube_tools import YouTubeTools
import re
import googleapiclient.discovery
import googleapiclient.errors
import os
from reports import PregnancyUltrasoundAnalyzer
import base64



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

API_KEY = os.getenv("YOUTUBE_API_KEY") 
def youtube_search_tool(query: str) -> str:
    """
    Searches YouTube for pregnancy-related videos and returns URLs only.
    Returns one URL per line or error message.
    """
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        return "Error: API key not configured."

    return _find_pregnancy_video_global_internal(query=query, api_key=API_KEY)

def _find_pregnancy_video_global_internal(query: str, api_key: str) -> str:
    """
    Internal function to search YouTube for top 3 videos.
    Returns a string with video URLs separated by newlines or an error message.
    """
    if not query:
        return "Error: No search query provided."

    try:
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=3,
            order="relevance"
        )
        response = request.execute()

        video_urls = []
        if response and 'items' in response:
            for item in response['items']:
                if 'videoId' in item.get('id', {}):
                    video_id = item['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_urls.append(video_url)

        if video_urls:
            return "\n".join(video_urls)
        else:
            return "No relevant videos found."

    except googleapiclient.errors.HttpError as e:
        error_content = e.content.decode('utf-8')
        if e.resp.status == 403:
            return "Error: YouTube API quota exceeded."
        elif e.resp.status == 400:
            return "Error: Invalid request."
        else:
            return f"Error: YouTube API error ({e.resp.status})."
    except Exception as e:
        return f"Error: {str(e)}"

@login_required
def pregnancy_video_tool(request):
    results = []
    error = None
    chat_messages = []

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            try:
                # Add user message to chat
                chat_messages.append({
                    'sender': 'user',
                    'content': query,
                    
                })

                # Initialize the agent
                agent = Agent(
                    model=Gemini(id="gemini-2.0-flash-exp", temperature=0.2),
                    tools=[youtube_search_tool, YouTubeTools()],
                    temperature=0.3,
                    instructions=[
                        "When asked to find pregnancy-related videos, use youtube_search_tool.",
                        "For each video URL found, immediately use YouTubeTools to get its details.",
                        "Return only a clean list of videos with: title, thumbnail URL, video URL, and 1-2 sentence description.",
                        "Format as: [TITLE](URL)\n[DESCRIPTION]\n[THUMBNAIL_URL]",
                        "Do not include any tool call information or raw output."
                    ],
                )

                # Get the response from the agent
                response = agent.run(query)
                raw_output = response.content if hasattr(response, "content") else str(response)

                # Parse the clean response
                video_blocks = raw_output.split('\n\n')  # Split by double newlines
                for block in video_blocks:
                    lines = block.split('\n')
                    if len(lines) >= 3:
                        title_line = lines[0]
                        description = lines[1]
                        thumbnail_url = lines[2] if len(lines) > 2 else ""
                        
                        # Extract title and URL
                        match = re.search(r'\[(.*?)\]\((.*?)\)', title_line)
                        if match:
                            title = match.group(1)
                            url = match.group(2)
                            
                            # Get video ID for thumbnail if not provided
                            if not thumbnail_url.startswith('http'):
                                video_id = url.split('v=')[-1]
                                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                            
                            results.append({
                                'title': title,
                                'url': url,
                                'thumbnail': thumbnail_url,
                                'description': description
                            })

                # Add assistant message to chat
                if results:
                    chat_messages.append({
                        'sender': 'assistant',
                        'content': f"I found {len(results)} videos about '{query}'",
                        
                        'results': results
                    })

            except Exception as e:
                error = f"Error: {str(e)}"
                chat_messages.append({
                    'sender': 'system',
                    'content': error,
                    
                })
        else:
            error = "Please enter a query."

    return render(request, 'maa/pregnancy_videos.html', {
        'chat_messages': chat_messages,
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

import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from nutrition import analyze_image_file
import markdown

@login_required
def nutrition_tool(request):
    result = None
    error = None

    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if uploaded_file:
            try:
                file_bytes = uploaded_file.read()
                extension = os.path.splitext(uploaded_file.name)[-1]
                raw_result = analyze_image_file(file_bytes, file_extension=extension)
                result = markdown.markdown(raw_result)  # <-- This line converts markdown to HTML
            except Exception as e:
                error = f"Error analyzing image: {str(e)}"


    return render(request, 'maa/nutrition_tool.html', {
        'result': result,
        'error': error
    })
# maa/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import NutritionDayForm
from .models import NutritionEntry
from collections import OrderedDict
from datetime import date, timedelta

# maa/views.py

from collections import OrderedDict
from datetime import date, timedelta

from django.utils import timezone
from markdown import markdown
from collections import OrderedDict
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import NutritionEntry
from .forms import NutritionDayForm  # make sure you're importing the correct form

@login_required
def nutrition_tracker(request):
    form = NutritionDayForm(request.POST or None)
    report_html = None

    if request.method == 'POST':
        if 'generate_report' in request.POST:
            report_md = generate_nutrition_report(request.user.id)
            print(request.user.id)
            report_html = markdown(report_md)
        elif form.is_valid():
            sel_date = form.cleaned_data['date']
            for slot in ['morning', 'noon', 'evening', 'night']:
                choice = form.cleaned_data[f'{slot}_choice']
                manual = form.cleaned_data[f'{slot}_manual']
                desc = choice or manual
                if desc:
                    NutritionEntry.objects.update_or_create(
                        user=request.user,
                        date=sel_date,
                        time_slot=slot.upper(),
                        defaults={'description': desc}
                    )
            return redirect('nutrition_tracker')

    # Build the summary for the last 7 days
    today = date.today()
    week_ago = today - timedelta(days=6)
    entries = NutritionEntry.objects.filter(
        user=request.user,
        date__range=[week_ago, today]
    )

    summary = OrderedDict()
    for i in range(7):
        d = week_ago + timedelta(days=i)
        summary[d] = {'morning': '', 'noon': '', 'evening': '', 'night': ''}

    for e in entries:
        summary[e.date][e.time_slot.lower()] = e.description

    return render(request, 'maa/nutrition_tracker.html', {
        'form': form,
        'summary': summary,
        'report_html': report_html,
    })



from phi.agent import Agent
from phi.tools.sql import SQLTools
from phi.model.google import Gemini

def generate_nutrition_report(user_id):
    agent = Agent(
        tools=[SQLTools(db_url="sqlite:///db.sqlite3")],
        model=Gemini(id="gemini-2.0-flash-exp", temperature=0.4),
    )
    
    prompt = f"""
        You are a personalized nutrition coach for a pregnant woman living in the North‑East region of India.  
        Her daily food/drink logs for the last 2 days are stored in the table `maa_nutritionentry` with columns:
        - `date`  
        - `time_slot` (MORNING/NOON/EVENING/NIGHT)  
        - `description` (free‑text of what she ate or drank, likely including rice dishes, fish curries, bamboo shoot preparations, fermented chutneys, local greens, seasonal fruits, etc.)  

        **Step 1: Data retrieval**  
        Use SQL to fetch exactly those rows for `user_id = {user_id}` where `date >= date('now','-1 days')`, sorted by `date ASC`, `time_slot ASC`.  

        **Step 2: Nutrient breakdown with regional context**  
        From each `description`, infer approximate quantities of:
        - **Macros**: protein (e.g. fish, eggs, legumes), carbohydrates (e.g. rice, black rice, sticky rice), fats (e.g. mustard oil, groundnut oil)
        - **Key micros**: iron (leafy greens like spinach, mustard greens), calcium (milk, local cheeses, tofu), folate (bamboo shoots, green leafy vegetables), vitamin D (sun‑exposed mushrooms, egg yolks), omega‑3 (freshwater fish), fiber (local vegetables, seasonal fruits), water

        Use your knowledge of North‑East Indian recipes (e.g. fish tenga, khar, smoked meats, sohnt–a fermented fish paste) to estimate servings and nutrient content.

        **Step 3: Summary of intake**  
        Produce a table showing for each nutrient:
        - **Total** consumed over the 2‑day period  
        - **Daily average**  
        - **Recommended range** per ICMR/WHO guidelines for pregnant women in India  

        Color‑code cells:  
        - 🔴 over‑consumed  
        - 🔵 under‑consumed  
        - 🟢 on target  

        **Step 4: Actionable insights**  
        For each nutrient off‑target:
        - Brief note on health implications (e.g. “Low iron can worsen anemia, fatigue”)  
        - Suggest 2–3 local foods or simple recipes (e.g. “Include a small bowl of saag tutum with mustard greens”, “Snack on boiled rice flakes with jaggery and coconut”)  

        **Step 5: Forward recommendations**  
        Based on current trends, craft a **2‑day sample meal plan** (breakfast, lunch, dinner, snacks) using North‑East staples (rice, fish, bamboo shoots, fermented chutneys, seasonal fruits) to balance nutrients.

        **Bonus features:**  
        - A daily **hydration reminder** (“Sip warm water or herbal ginger tea between meals”)  
        - A habit tip (“Keep a small jar of roasted chana for quick protein boosts”)  
        - A 3‑point “To‑Do” checklist (e.g. “Eat an extra serving of green leafy vegetables tomorrow”)

        Deliver the entire report as **Markdown**, with clear headings, tables, and color‑coded nutrient summaries.
"""
    
    response = agent.run(prompt)
    return response.content



from django.core.files.storage import FileSystemStorage
from django.utils import timezone
import markdown

@login_required
def ultrasound_analysis(request):
    report = None
    error = None
    image_data_urls = []

    if request.method == 'POST':
        # Handle file uploads
        uploaded_files = request.FILES.getlist('ultrasound_images')
        # Handle camera captures (base64 data)
        camera_images = request.POST.getlist('camera_images[]')
        
        file_paths = []
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'ultrasounds'))
        
        try:
            # Process uploaded files
            for file in uploaded_files:
                filename = fs.save(f"{timezone.now().timestamp()}_{file.name}", file)
                file_paths.append(os.path.join(fs.location, filename))
            
            # Process camera captures
            for i, image_data in enumerate(camera_images):
                if image_data.startswith('data:image'):
                    format, imgstr = image_data.split(';base64,') 
                    ext = format.split('/')[-1] 
                    filename = f"camera_capture_{timezone.now().timestamp()}_{i}.{ext}"
                    filepath = os.path.join(fs.location, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(imgstr))
                    file_paths.append(filepath)
            
            if file_paths:
                analyzer = PregnancyUltrasoundAnalyzer()
                raw_result = analyzer.analyze(file_paths)
                report = markdown.markdown(raw_result) 
            
            # Clean up files
            for path in file_paths:
                if os.path.exists(path):
                    os.remove(path)
                    
        except Exception as e:
            error = f"Error analyzing ultrasound: {str(e)}"
            # Clean up any partially processed files
            for path in file_paths:
                if os.path.exists(path):
                    os.remove(path)

    return render(request, 'maa/ultrasound_analysis.html', {
        'report': report,
        'error': error,
        'image_data_urls': image_data_urls
    })

from medicine_analyzer import analyze_image_file  # You'll need to create this file
import base64

@login_required
def medicine_analysis(request):
    analysis = None
    error = None
    image_data_urls = []

    if request.method == 'POST':
        # Handle file uploads
        uploaded_files = request.FILES.getlist('medicine_images')
        # Handle camera captures (base64 data)
        camera_images = request.POST.getlist('camera_images[]')
        
        file_paths = []
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'medicines'))
        
        try:
            # Process uploaded files
            for file in uploaded_files:
                filename = fs.save(f"{timezone.now().timestamp()}_{file.name}", file)
                file_paths.append(os.path.join(fs.location, filename))
            
            # Process camera captures
            for i, image_data in enumerate(camera_images):
                if image_data.startswith('data:image'):
                    format, imgstr = image_data.split(';base64,') 
                    ext = format.split('/')[-1] 
                    filename = f"camera_capture_{timezone.now().timestamp()}_{i}.{ext}"
                    filepath = os.path.join(fs.location, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(imgstr))
                    file_paths.append(filepath)
            
            if file_paths:
                # Analyze the first image (you could modify to handle multiple)
                with open(file_paths[0], 'rb') as f:
                    analysis = analyze_image_file(f.read(), os.path.splitext(file_paths[0])[-1])
            
            # Clean up files
            for path in file_paths:
                if os.path.exists(path):
                    os.remove(path)
                    
        except Exception as e:
            error = f"Error analyzing medicine: {str(e)}"
            # Clean up any partially processed files
            for path in file_paths:
                if os.path.exists(path):
                    os.remove(path)

    return render(request, 'maa/medicine_analysis.html', {
        'analysis': analysis,
        'error': error,
        'image_data_urls': image_data_urls
    })
    
    
