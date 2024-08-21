
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following_view, name="following"),
    path("user/<str:username>", views.profile_view, name="profile"),
    path("edit/<str:post_id>", views.edit_post, name="edit_post"),
    path("post/<str:post_id>", views.post_view, name="post"),

    # API Routes
    path("follow_user", views.follow_user, name="follow_user"),
    path("like_post", views.like_post, name="like_post"),
    path("add_post", views.add_post, name="add_post"),
]
