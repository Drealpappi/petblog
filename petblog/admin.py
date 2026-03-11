# admin.py
from django.contrib import admin
from .models import Post, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_author')
    list_filter = ('is_author',)
    search_fields = ('user__username', 'user__email')

# Register your models here – outside the class!
admin.site.register(Post)
admin.site.register(Profile, ProfileAdmin)