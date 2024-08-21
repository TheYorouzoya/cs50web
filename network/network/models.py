from django.contrib.auth.models import AbstractUser
from django.db import models

import django.utils.timezone
import uuid


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        db_index=True,
        primary_key=True
    )
    username = models.CharField(
        max_length=50,
        unique=True
    )
    password = models.CharField(
        max_length=128
    )
    date_joined = models.DateTimeField(
        default=django.utils.timezone.now
    )
    followers = models.IntegerField(
        default=0
    )
    following = models.IntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.username}"


class Post(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name="Post UUID"
    )
    author = models.ForeignKey(
        'User',
        related_name='Poster',
        on_delete=models.CASCADE,
        db_index=True
    )
    content = models.CharField(
        max_length=280,
    )
    creation_date = models.DateTimeField(
        default=django.utils.timezone.now,
        db_index=True
    )
    likes = models.IntegerField(
        default=0
    )
    comments = models.IntegerField(
        default=0
    )

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs) 
        return self

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "likes": self.likes,
            "comments": self.comments,
            "timestamp": self.creation_date.strftime("%b %d %Y, %I:%M %p")
        }

    def __str__(self):
        return f"{self.author} posted {self.content}"


class Comment(models.Model):
    commenter = models.ForeignKey(
        'User',
        related_name="Commenter",
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        'Post',
        related_name="Post",
        on_delete=models.CASCADE,
        db_index=True
    )
    content = models.CharField(
        max_length=280
    )
    creation_date = models.DateTimeField(
        default=django.utils.timezone.now
    )

    def __str__(self):
        return f"{self.commenter} commented on {self.post}"
    

class Like(models.Model):
    liked = models.ForeignKey(
        'Post',
        related_name="Liked",
        on_delete=models.CASCADE,
        db_index=True
    )
    liker = models.ForeignKey(
        'User',
        related_name="Liker",
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(
        default=django.utils.timezone.now
    )

    def __str__(self):
        return f"{self.liker} liked {self.liked}"


class Follow(models.Model):
    follower = models.ForeignKey(
        'User',
        related_name="Follower",
        on_delete=models.CASCADE,
        db_index=True
    )
    followed = models.ForeignKey(
        'User',
        related_name="Followed",
        on_delete=models.CASCADE,
        db_index=True
    )
    creation_date = models.DateTimeField(
        default=django.utils.timezone.now,
        db_index=True
    )

    def __str__(self):
        return f"{self.follower} followed {self.followed}"
