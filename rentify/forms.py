from django import forms

from .models import Listing, ListingInquiry


class ListingForm(forms.ModelForm):
    purpose = forms.ChoiceField(
        choices=Listing.Purpose.choices,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Listing
        fields = (
            "purpose",
            "property_type",
            "title",
            "description",
            "city",
            "address",
            "price",
            "bedrooms",
            "bathrooms",
            "area_sqm",
            "image",
        )
        labels = {
            "property_type": "Property type",
            "title": "Listing title",
            "description": "About this home",
            "city": "City",
            "address": "Street address",
            "price": "Price (USD)",
            "bedrooms": "Bedrooms",
            "bathrooms": "Bathrooms",
            "area_sqm": "Floor area (m²)",
            "image": "Home photo (optional)",
        }
        help_texts = {
            "image": "JPG, PNG, or WebP, up to 8 MB.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "A bright home near the old town"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Share what makes this home special."}),
            "city": forms.TextInput(attrs={"placeholder": "Bukhara"}),
            "address": forms.TextInput(attrs={"placeholder": "Street and neighborhood"}),
            "price": forms.NumberInput(attrs={"min": "1", "step": "0.01"}),
            "bedrooms": forms.NumberInput(attrs={"min": "0", "max": "99"}),
            "bathrooms": forms.NumberInput(attrs={"min": "0", "max": "99"}),
            "area_sqm": forms.NumberInput(attrs={"min": "1"}),
            "image": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image

        if image.size > 8 * 1024 * 1024:
            raise forms.ValidationError("Choose an image smaller than 8 MB.")

        signature = image.read(12)
        image.seek(0)
        is_jpeg = signature.startswith(b"\xff\xd8\xff")
        is_png = signature.startswith(b"\x89PNG\r\n\x1a\n")
        is_webp = signature.startswith(b"RIFF") and signature[8:12] == b"WEBP"
        if not (is_jpeg or is_png or is_webp):
            raise forms.ValidationError("Upload a valid JPG, PNG, or WebP image.")
        return image


class ListingInquiryForm(forms.Form):
    name = forms.CharField(max_length=120, label="Your name")
    email = forms.EmailField(label="Email address")
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "Tell the seller what you'd like to know."}),
        label="Message",
    )

    def save(self, listing=None, user=None):
        inquiry = ListingInquiry.objects.create(
            listing=listing,
            sender=user,
            sender_name=self.cleaned_data["name"],
            sender_email=self.cleaned_data["email"],
            message=self.cleaned_data["message"],
        )
        return inquiry