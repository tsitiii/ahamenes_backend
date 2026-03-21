from django.urls import path

from .views import SetPasswordView


urlpatterns = [
	path('set-password/', SetPasswordView.as_view(), name='set-password'),
]
