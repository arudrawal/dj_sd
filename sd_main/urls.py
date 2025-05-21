from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login_agency/", views.login_agency, name="login_agency"),
    path("select_alert/", views.select_alert, name="select_alert"),
    path("customers/", views.customers, name="customers"),
    path("policies/", views.policies, name="policies"),
    path("settings/", views.settings, name="settings"),
    path("gmail_oauth_redirect/", views.gmail_oauth_redirect, name="gmail_oauth_redirect"),
    path("gmail_oauth_callback/", views.gmail_oauth_callback, name="gmail_oauth_callback"),
    path("vehicles/", views.vehicles, name="vehicles"),
    path("drivers/", views.drivers, name="drivers"),
    path("upload_policy/", views.upload_policy, name="upload_policy"),
]
# Add MEDIA_URL route and serve the uploaded file when a user makes a GET request to MEDIA_URL/(file name). 
# Once all this is done, the files uploaded should show up in the directory specified in the MEDIA_ROOT constant.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
