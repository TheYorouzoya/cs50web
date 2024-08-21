from decimal import Decimal
from logging import WARNING
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *
from .forms import *


def index(request):
    # Get the first ten active listings sorted by date
    listings = Listing.objects.all().exclude(active_status=False).order_by('-creation_date')
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def add(request):
    if request.method == 'POST':
        # Get the modelform
        form = ListingForm(request.POST)

        if form.is_valid():
            # Add user to model instance
            form.instance.author = request.user
            new_list = form.save()
            messages.success(request, "Successfully added listing!")
        return redirect('listing', listing_id=new_list.id)

    else:
        # Pass modelform to template
        form = ListingForm()
        return render(request, "auctions/newlisting.html", {
            'form': form
        })


def listing_view(request, listing_id):
    # Attempt to fetch listing from database
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html")
    
    # Fetch listing's highest bid, comments, and watchlist status
    bids = Bid.objects.filter(lot=listing_id).order_by('-creation_date')
    count = bids.count()
    comments = Comment.objects.filter(post=listing_id)
    try:
        watchlist = Watchlist.objects.filter(watcher=request.user).filter(listing=listing_id)
    except TypeError:
        watchlist = []
    commentform = CommentForm()

    if listing.author == request.user:
        author = True
    else:
        author = False

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'bids': bids,
        'bidcount': count,
        'comments': comments,
        'watchlist': watchlist,
        'author': author,
        'commentform': commentform
    })


@login_required
def watchlist_view(request):
    if request.method == 'POST':
        # If user adds to watchlist
        if 'addwatch' in request.POST:
            entry = Watchlist(listing_id=request.POST["listing_id"], watcher=request.user)
            entry.save()
            messages.success(request, "Added to watchlist!")
            return redirect('listing', listing_id=request.POST["listing_id"])
        
        # If user removes from watchlist
        elif 'removewatch' in request.POST:
            entry = Watchlist.objects.filter(watcher=request.user).filter(listing=request.POST["listing_id"])
            entry.delete()
            messages.success(request, "Removed from watchlist!")
            return redirect('listing', listing_id=request.POST["listing_id"])

    else:
        watchlist = Watchlist.objects.filter(watcher=request.user)
        return render(request, 'auctions/watchlist.html', {
            'watchlist': watchlist
        })


@login_required
def bid_view(request):
    if request.method == 'POST':
        listing_id = request.POST["listing_id"]
        
        # If user is not listing author
        if "add_bid" in request.POST:
            bid = Decimal(request.POST["bid"])
            
            # If it is the first bid on a listing
            if "starting_bid" in request.POST:
                original_bid = Listing.objects.get(id=listing_id)
                
                # If bid is invalid, show error
                if original_bid.price > bid:
                    messages.error(request, "Invalid bid! Your bid must be greater than or equal to the starting bid.")
                    return redirect('listing', listing_id=listing_id)

            # For subsequent bids
            else:
                original_bid = Bid.objects.filter(lot_id=listing_id).order_by('-creation_date')[:1]
    
                # If bid is invalid, show error
                if original_bid[0].amount >= bid:
                    messages.error(request, "Invalid bid! Your bid must be greater than the current bid.")
                    return redirect('listing', listing_id=listing_id)
            
            # Add valid bid to database
            current_bid = Bid(lot_id=listing_id, bidder=request.user, amount=bid)
            current_bid.save()

            # Update listing's current price
            current_list = Listing.objects.get(id=listing_id)
            current_list.price = bid
            current_list.save()
            
            messages.success(request, "Successfully placed bid!")
            return redirect('listing', listing_id=listing_id)
        
        # If user is listing author and decides to close auction
        elif "close_auc" in request.POST:
            lot = Listing.objects.get(id=listing_id)
            lot.active_status = False
            lot.save()
            return redirect('listing', listing_id=listing_id)
    
    return redirect('index')


@login_required
def comment_view(request):
    if request.method == 'POST':
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            commentform.instance.commenter = request.user
            commentform.instance.post_id = request.POST["listing_id"]
            commentform.save()
            return redirect('listing', listing_id=request.POST["listing_id"])
    return redirect('index')


def categories(request):
    cat_list = Category.objects.all().order_by('code')
    return render(request, 'auctions/categories.html', {
        'categories': cat_list
    })


def catlist(request, category_code):
    listings = Listing.objects.filter(category=category_code).exclude(active_status=False).order_by('creation_date')
    category = Category.objects.get(code=category_code)
    return render(request, 'auctions/catlist.html', {
        'listings': listings,
        'category': category
    })