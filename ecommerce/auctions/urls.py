from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add", views.add, name="add"),
    path("listing/<str:listing_id>", views.listing_view, name="listing"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path('bid', views.bid_view, name="bid"),
    path('comment', views.comment_view, name="comment"),
    path('categories', views.categories, name="categories"),
    path('category/<str:category_code>', views.catlist, name="category")
]
