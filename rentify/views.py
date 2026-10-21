from urllib.parse import urlencode
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ListingForm, ListingInquiryForm
from .models import Listing, ListingLike


def home_view(request):
    return render(request, "rentify/home.html")


def search_view(request):
    destination = "rent" if request.GET.get("intent") == "rent" else "buy"
    query = urlencode(request.GET)
    url = reverse(destination)
    return redirect(f"{url}?{query}" if query else url)


def rent_view(request):
    return _browse_view(request, "rent")


def buy_view(request):
    return _browse_view(request, "buy")


def listing_detail_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    inquiry_form = ListingInquiryForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle_like":
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={reverse('listing_detail', args=[listing.pk])}")
            if listing.owner_id == request.user.id:
                liked = False
                notice = "You cannot like your own listing."
            else:
                like, created = ListingLike.objects.get_or_create(
                    listing=listing,
                    user=request.user,
                )
                if created:
                    liked = True
                    notice = "Added to your liked homes."
                else:
                    like.delete()
                    liked = False
                    notice = "Removed from your likes."
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"liked": liked, "message": notice})
            messages.info(request, notice)
            return redirect("listing_detail", pk=listing.pk)

        inquiry_form = ListingInquiryForm(request.POST)
        if inquiry_form.is_valid():
            inquiry_form.save(
                listing=listing,
                user=request.user if request.user.is_authenticated else None,
            )
            messages.success(request, "Your message has been sent to the seller.")
            return redirect("listing_detail", pk=listing.pk)

    return render(
        request,
        "rentify/detail.html",
        {
            "listing": listing,
            "inquiry_form": inquiry_form,
            "is_liked": request.user.is_authenticated
            and listing.likes.filter(user=request.user).exists(),
        },
    )


@login_required
def liked_homes_view(request):
    liked_listings = Listing.objects.filter(
        likes__user=request.user,
        is_active=True,
    ).select_related("owner")
    return render(
        request,
        "rentify/liked_homes.html",
        {
            "listings": liked_listings,
            "liked_count": liked_listings.count(),
        },
    )


@login_required
def seller_inbox_view(request):
	listings = request.user.listings.filter(is_active=True).prefetch_related(
		"likes__user",
		"inquiries__sender",
	)
	return render(request, "rentify/inbox.html", {"listings": listings})


def _browse_view(request, purpose):
    location = request.GET.get("location", "Bukhara").strip()
    listings = Listing.objects.filter(purpose=purpose, is_active=True)
    if location:
        listings = listings.filter(city__icontains=location)

    property_type = request.GET.get("property_type")
    if property_type in Listing.PropertyType.values:
        listings = listings.filter(property_type=property_type)

    bedrooms = request.GET.get("bedrooms", "")
    if bedrooms.isdigit():
        listings = listings.filter(bedrooms__gte=int(bedrooms))

    price_range = request.GET.get("price_range", "")
    try:
        if price_range.startswith("under-"):
            listings = listings.filter(price__lt=Decimal(price_range[6:]))
        elif price_range.startswith("over-"):
            listings = listings.filter(price__gte=Decimal(price_range[5:]))
        elif "-" in price_range:
            minimum, maximum = price_range.split("-", 1)
            listings = listings.filter(
                price__gte=Decimal(minimum),
                price__lte=Decimal(maximum),
            )
    except InvalidOperation:
        pass

    return render(
        request,
        "rentify/browse.html",
        {
            "purpose": purpose,
            "location": location or "All areas",
            "listings": listings.select_related("owner"),
        },
    )


@login_required
def sell_view(request):
    form = ListingForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        listing = form.save(commit=False)
        listing.owner = request.user
        listing.save()
        messages.success(request, "Your home has been posted.")
        return redirect("profile")
    return render(request, "rentify/sell.html", {
        "form": form,
        "page_eyebrow": "SHARE YOUR PLACE",
        "page_title": "Post your home",
        "page_description": "Add a few details so renters and buyers can find the right fit.",
        "submit_label": "Post home",
    })


@login_required
def listing_edit_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user, is_active=True)
    form = ListingForm(
        request.POST or None,
        request.FILES or None,
        instance=listing,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your listing has been updated.")
        return redirect("listing_detail", pk=listing.pk)
    return render(request, "rentify/sell.html", {
        "form": form,
        "page_eyebrow": "MANAGE YOUR LISTING",
        "page_title": "Edit your listing",
        "page_description": "Update the details of your home.",
        "submit_label": "Save changes",
    })


@login_required
@require_POST
def listing_delete_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user, is_active=True)
    listing.is_active = False
    listing.save(update_fields=("is_active",))
    messages.success(request, "Your listing has been deleted.")
    return redirect("profile")
