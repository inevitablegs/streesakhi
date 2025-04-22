from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from home.views import home_page
from maa import views as maa_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),  # Home page
    path('dashboard/', maa_views.dashboard, name='dashboard'),
    path('profile/',       maa_views.view_profile, name='view_profile'),
    path('profile/edit/',  maa_views.edit_profile, name='edit_profile'),
    path('register/', maa_views.register, name='register'),
    path('login/', maa_views.user_login, name='login'),
    path('logout/', maa_views.user_logout, name='logout'),
    path('password/change/', maa_views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('pregnancy-videos/', maa_views.pregnancy_video_tool, name='pregnancy_videos'),
    path('load-more-videos/', maa_views.load_more_videos, name='load_more_videos'),
    path('nutrition/', maa_views.nutrition_tool, name='nutrition_tool'),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)