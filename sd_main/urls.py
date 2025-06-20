from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login_agency/", views.login_agency, name="login_agency"),
    path("pending_alerts", views.pending_alerts, name="pending_alerts"),
    path("select_alert/", views.select_pending_alert, name="select_alert"),
    path("edit_alert/", views.edit_pending_alert, name="edit_alert"),
    path("save_alert/", views.save_pending_alert, name="save_alert"),
    path("filter_alert/", views.filter_pending_alert, name="filter_alert"),
    path("customers/", views.customers, name="customers"),
    path("policies/", views.policies, name="policies"),
    path("email_oauth/", views.email_oauth, name="email_oauth"),
    path("send_test_email/", views.send_test_email, name="send_test_email"),
    path("send_test_email/", views.send_test_email, name="send_test_email"),
    path("send_email/", views.send_email, name="send_email"),
    path("send_email/<int:template_id>/", views.send_email, name="send_email_id"),
    path("email_history/", views.email_history, name="email_history"),
    path("gmail_oauth_authorize/", views.gmail_oauth_authorize, name="gmail_oauth_authorize"),
    path("gmail_oauth_revoke/", views.gmail_oauth_revoke, name="gmail_oauth_revoke"),
    path("gmail_oauth_callback/", views.gmail_oauth_callback, name="gmail_oauth_callback"),
    path("drivers/", views.drivers, name="drivers"),
    path("drivers/", views.drivers, name="drivers"),
    path("upload_policy/", views.upload_policy, name="upload_policy"),


]
# Add MEDIA_URL route and serve the uploaded file when a user makes a GET request to MEDIA_URL/(file name). 
# Once all this is done, the files uploaded should show up in the directory specified in the MEDIA_ROOT constant.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
