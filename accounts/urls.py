from django.urls import path
#from django.conf import settings
#from django.conf.urls.static import static

from .views import SignUpView
# from . import views

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
]
