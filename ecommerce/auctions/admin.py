from django.contrib import admin
from django import forms
from .models import User, Listing, Bid, Comment, Watchlist, Category

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')


class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'category', 'active_status', 'creation_date')
    
    # Change the listing description's field in the admin view to a larger textarea for ease of use
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'description': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'commenter', 'creation_date')

    # Change the comment's content's field in the admin view to a larger textarea for ease of use
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'content': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


class BidAdmin(admin.ModelAdmin):
    list_display = ('lot', 'bidder', 'amount', 'creation_date')


class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('listing', 'watcher')


admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Category)