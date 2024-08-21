from django.contrib import admin
from django import forms
from .models import User, Post, Comment, Like, Follow

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "date_joined")


class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "creation_date")

    # Change the Post's content field in the admin view to textarea instead of single line
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'content': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "post", "content", "creation_date")

    # Change the Comment's content field in the admin view to textarea instead of single line
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'content': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


class LikeAdmin(admin.ModelAdmin):
    list_display = ("liked", "liker", "creation_date")


class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "creation_date")

admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Follow, FollowAdmin)