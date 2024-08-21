from sqlite3 import DatabaseError
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Exists, OuterRef

from .models import User, Post, Comment, Like, Follow
import json


# View for the default page
def index(request):
    try:
        if request.user.is_authenticated:
            posts = Post.objects.all().order_by('-creation_date').annotate(
                is_liked=Exists(
                    Like.objects.filter(liker=request.user, liked=OuterRef('pk'))
                )
            )
        else:
            posts = Post.objects.all().order_by('-creation_date')

    except DatabaseError:
        return render(request, 'network/index.html', {
            "page_error": "Database error occurred!"
        })

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        return render(request, 'network/index.html', {
            "page_error": "Invalid page number!"
        })

    return render(request, 'network/index.html', {
        "page_obj": page_obj
    })   


# View for a user's profile
def profile_view(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'network/apology.html', {
            "error": "User does not exist"
        })

    try:
        if request.user.is_authenticated:
            posts = Post.objects.filter(author=profile_user).order_by('-creation_date').annotate(
                    is_liked=Exists(
                        Like.objects.filter(liker=request.user, liked=OuterRef('pk'))
                    )
                ) 
        else:
            posts = Post.objects.filter(author=profile_user)
            
    except DatabaseError:
        return render(request, 'network/apology.html', {
            "error": "Database error occurred!"
        })
    
    if request.user.is_authenticated:
        # Check if the request user is following the profile user
        is_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()
    else:
        is_following = False

    

    paginator = Paginator(posts, 10)
    # If there's a page number in request, use it, else, default to first page
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        return render(request, 'network/profile.html', {
            'profile': profile_user,
            'is_following': is_following,
            'page_error': "Invalid page number!"
        })

    return render(request, 'network/profile.html', {
        'profile': profile_user,
        'is_following': is_following,
        'page_obj': page_obj
    })


@login_required
def following_view(request):
    try:
        following_group = User.objects.filter(Followed__in=Follow.objects.filter(follower=request.user))
    except DatabaseError:
        return render(request, 'network/apology.html', {
            "error": "Database error occurred!"
        })

    try:
        posts = Post.objects.filter(author__in=following_group).order_by('-creation_date').annotate(
            is_liked=Exists(
                Like.objects.filter(liker=request.user, liked=OuterRef('pk'))
            )
        )  
    except DatabaseError:
        return render(request, 'network/apology.html', {
            "error": "Database error occurred!"
        })

    paginator = Paginator(posts, 10)
    # If there's a page number in request, use it, else, default to first page
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        return render(request, 'network/following.html', {
            "page_error": "Invalid page number!"
        })

    return render(request, 'network/following.html', {
        "page_obj": page_obj
    })


def post_view(request, post_id):
    try:
        if request.user.is_authenticated:
            post = Post.objects.annotate(
                is_liked=Exists(
                    Like.objects.filter(liker=request.user, liked=OuterRef('pk'))
                )
            ).get(id=post_id)
        else:
            post = Post.objects.get(id=post_id)

    except Post.DoesNotExist:
        return render(request, 'network/post.html', {
            "page_error": "Requested post does not exist."
        })
    
    if request.method == 'GET':    
        try:
            comments = Comment.objects.filter(post=post_id)
        except DatabaseError:
            return render(request, 'network/post.html', {
                "page_error": "Database error occurred!",
                "post": post
            })
        
        comment_paginator = Paginator(comments, 10)
        page_number = request.GET.get('page', 1)
        
        try:
            comment_obj = comment_paginator.page(page_number)
        except InvalidPage:
            return render(request, 'network/post.html', {
                "page_error": "Invalid Page Number!",
                "post": post
            })

        return render(request, 'network/post.html', {
            "post": post,
            "comments": comment_obj
        })

    elif request.method == 'POST':
        if request.POST["comment_content"] is not None:
            comment = Comment(
                commenter=request.user,
                post=post,
                content=request.POST["comment_content"] 
            )
            comment.save()
            post.comments += 1
            post.save()
            return redirect('post', post_id=post_id)


@login_required
def add_post(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required!"}, status=400)
    
    data = json.loads(request.body)
    content = data.get("content")
    post = Post(
        author=request.user,
        content=content
    )
    new_post = post.save()
    return JsonResponse({"message": "Post created successfully", "post": new_post.serialize()}, status=201)  


@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(author=request.user, id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found!"}, status=404)

    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get("post_content") is not None:
            post.content = data["post_content"]
        post.save()
        return JsonResponse({"message": "Successfully edited post."}, status=203)
    
    else:
        return JsonResponse({"error": "POST request required!"}, status=403)


@login_required
def like_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "Post request required."}, status=400)
    
    data = json.loads(request.body)
    liked = False

    if data.get("post_id") is not None:
        try:
            post = Post.objects.get(id=data.get("post_id"))
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
    else:
        return JsonResponse({"error": "Post id missing"}, status=400)
    
    try:
        like_entry = Like.objects.get(liked=post, liker=request.user)
    except Like.DoesNotExist:
        like_entry = Like(liked=post, liker=request.user)
        like_entry.save()
        post.likes += 1
        post.save()
        liked = True
        return JsonResponse({"message": "Liked post successfully", "likes": post.likes, "liked": liked}, status=201)

    like_entry.delete()
    post.likes -= 1
    post.save()
    return JsonResponse({"message": "Unliked post successfully", "likes": post.likes, "liked": liked}, status=201)


@login_required
def follow_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        follower = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return JsonResponse({"error": "Request user does not exist"}, status=404)
    
    data = json.loads(request.body)

    if data.get("followed") is not None:
        try:
            followed = User.objects.get(username=data.get("followed"))
        except User.DoesNotExist:
            return JsonResponse({"error": "The followed user does not exist"}, status=404)
    else:
        return JsonResponse({"error": "Followed user field cannot be empty"}, status=403)

    if (follower.username == followed.username):
        return JsonResponse({"error": "User cannot follow themselves."}, status=403)

    try:
        # Try to fetch the entry from the database
        follow_entry = Follow.objects.get(follower=follower, followed=followed)
    except Follow.DoesNotExist:
        # If entry does not exist, create it
        follow_entry = Follow(follower=follower, followed=followed)
        follow_entry.save()
        follower.following += 1
        followed.followers += 1
        follower.save()
        followed.save()
        return JsonResponse({"message": "Follow successfull.", "followers": followed.followers}, status=201)
    
    # If entry exists, delete it
    follow_entry.delete()
    follower.following -= 1
    followed.followers -= 1
    follower.save()
    followed.save()
    return JsonResponse({"message": "Unfollow successfull.", "followers": followed.followers}, status=201)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")