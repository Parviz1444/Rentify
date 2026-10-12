from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def register_view(request):
	form = UserCreationForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.save()
		login(request, user)
		return redirect("welcome")
	return render(request, "registration/register.html", {"form": form})


@login_required
def welcome_view(request):
	return render(request, "registration/welcome.html")


@login_required
def profile_view(request):
	return render(
		request,
		"registration/profile.html",
		{"listings": request.user.listings.all()},
	)
