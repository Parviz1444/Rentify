from django.contrib import admin
from .models import Listing, ListingInquiry, ListingLike

admin.site.register(Listing)
admin.site.register(ListingInquiry)
admin.site.register(ListingLike)
