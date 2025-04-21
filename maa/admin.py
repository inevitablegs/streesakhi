from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import WomanUser

admin.site.register(WomanUser, UserAdmin)