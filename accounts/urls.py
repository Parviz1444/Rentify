from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
	path("register/", views.register_view, name="register"),
	path(
		"login/",
		auth_views.LoginView.as_view(
			template_name="registration/login.html",
			redirect_authenticated_user=True,
		),
		name="login",
	),
	path(
		"logout/",
		auth_views.LogoutView.as_view(next_page="logged_out"),
		name="logout",
	),
	path(
		"logged-out/",
		TemplateView.as_view(template_name="registration/logged_out.html"),
		name="logged_out",
	),
	path("welcome/", views.welcome_view, name="welcome"),
	path("profile/", views.profile_view, name="profile"),
]
