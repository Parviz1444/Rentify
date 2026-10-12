from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models


class Listing(models.Model):
	class Purpose(models.TextChoices):
		RENT = "rent", "For rent"
		BUY = "buy", "For sale"

	class PropertyType(models.TextChoices):
		APARTMENT = "apartment", "Apartment"
		HOUSE = "house", "House"
		TOWNHOUSE = "townhouse", "Townhouse"
		STUDIO = "studio", "Studio"

	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="listings",
	)
	purpose = models.CharField(max_length=8, choices=Purpose.choices)
	property_type = models.CharField(max_length=12, choices=PropertyType.choices)
	title = models.CharField(max_length=120)
	description = models.TextField(max_length=3000)
	city = models.CharField(max_length=100, default="Bukhara")
	address = models.CharField(max_length=200)
	price = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		validators=[MinValueValidator(1)],
	)
	bedrooms = models.PositiveSmallIntegerField(default=1)
	bathrooms = models.PositiveSmallIntegerField(default=1)
	area_sqm = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	image = models.FileField(
		upload_to="listings/",
		blank=True,
		validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
	)
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ("-created_at",)

	def __str__(self):
		return self.title

	@property
	def price_period(self):
		return " / month" if self.purpose == self.Purpose.RENT else ""


class ListingInquiry(models.Model):
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="inquiries")
	sender = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="listing_inquiries",
	)
	sender_name = models.CharField(max_length=120)
	sender_email = models.EmailField()
	message = models.TextField(max_length=2000)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-created_at",)

	def __str__(self):
		return f"Inquiry for {self.listing.title} from {self.sender_name}"


class ListingLike(models.Model):
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="likes")
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="liked_listings",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-created_at",)
		constraints = [
			models.UniqueConstraint(fields=("listing", "user"), name="unique_listing_like")
		]

	def __str__(self):
		return f"{self.user} liked {self.listing.title}"
