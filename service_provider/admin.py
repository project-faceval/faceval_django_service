from django.contrib import admin
from .models import Profile, PhotoBlog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'display_name', 'gender', 'status']
    list_display = ['user', 'display_name', 'gender', 'status']
    search_fields = ['user__username']
    date_hierarchy = 'user__date_joined'


@admin.register(PhotoBlog)
class PhotoBlogAdmin(admin.ModelAdmin):
    fields = ['trained', 'path', 'title', 'description', 'tag', 'date_added']
    readonly_fields = ['view_auth_user', 'score', 'face_positions']
    search_fields = ['user__user__username']
    list_display = ['path', 'view_auth_user', 'score', 'title', 'date_added', 'tag']
    date_hierarchy = 'date_added'

    @admin.display(description='User name')
    def view_auth_user(self, obj):
        return obj.user.user
