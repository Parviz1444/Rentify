from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("search/", views.search_view, name="search"),
    path("rent/", views.rent_view, name="rent"),
    path("buy/", views.buy_view, name="buy"),
    path("liked/", views.liked_homes_view, name="liked_homes"),
    path("inbox/", views.seller_inbox_view, name="seller_inbox"),
    path("sell/", views.sell_view, name="sell"),
    path("listing/<int:pk>/", views.listing_detail_view, name="listing_detail"),
    path("listing/<int:pk>/edit/", views.listing_edit_view, name="listing_edit"),
    path("listing/<int:pk>/delete/", views.listing_delete_view, name="listing_delete"),
]