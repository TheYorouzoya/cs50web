from django.contrib.auth.models import AbstractUser
from django.db import models

import django.utils.timezone
import uuid


class User(AbstractUser):
    username = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True, 
        primary_key=True
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return f"{self.username}"


class Listing(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        editable=False, 
        default=uuid.uuid4, 
        verbose_name='Listing UUID'
    )
    author = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='Auctioneer', 
        db_index=True
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    image_link = models.URLField(
        max_length=200, 
        help_text="Stores the listing product's image link",
        blank=True,
        null=True
    )
    image_alt_text = models.CharField(
        max_length=200,
        help_text="Alt text for the image for accessibility",
        blank=True
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2
    )
    category = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE, 
        related_name='Category_Code', 
        db_index=True
    )
    active_status = models.BooleanField(
        help_text="Denotes whether a listing is on-sale(true) or sold(false)", 
        default=True
    )
    creation_date = models.DateTimeField(
        default=django.utils.timezone.now, 
        db_index=True
    )

    def __str__(self):
        return f"{self.title} - listed by {self.author}"

    # Custom save() function to replace image's alt text with listing's title if field is empty
    def save(self, *args, **kwargs):
        if not self.image_alt_text:
            self.image_alt_text = self.title
        super().save( *args, **kwargs)


class Bid(models.Model):
    lot = models.ForeignKey(
        'Listing', 
        on_delete=models.CASCADE, 
        related_name='Lot', 
        db_index=True
    )
    bidder = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='Bidder'
    )
    amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        help_text="Bid amount on the listing"
    )
    creation_date = models.DateTimeField(
        default=django.utils.timezone.now
    )

    def __str__(self):
        return f"{self.bidder} placed a ${self.amount} bid on {self.lot}"


class Comment(models.Model):
    commenter = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='Commenter'
    )
    post = models.ForeignKey(
        'Listing', 
        on_delete=models.CASCADE, 
        related_name='Post', 
        db_index=True
    )
    content = models.CharField(max_length=2000)
    creation_date = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return f"{self.commenter} commented on {self.post}"


class Watchlist(models.Model):
    listing = models.ForeignKey(
        'Listing', 
        on_delete=models.CASCADE, 
        related_name='Watched'
    )
    watcher = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name="Watcher"
    )

    def __str__(self):
        return f"{self.watcher} added {self.listing} to watchlist"


class Category(models.Model):
    code = models.CharField(
        max_length=3, 
        primary_key=True, 
        unique=True
    )
    description = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.description}"