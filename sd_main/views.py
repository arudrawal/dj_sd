import json
import tempfile
from io import StringIO
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template import Template, Context
from django.utils.safestring import mark_safe

from .forms import UploadPolicyForm, EmailTemplateForm
from .forms import AgencyForm
from . import constants

import google.oauth2.credentials
import google_auth_oauthlib.flow

from .models import Agency, AgencyUser, AgencySetting, Policy, PolicyAlert, Customer, \
    SystemSetting, EmailTemplate

from .import_data import convert_to_dataframe, import_policy, import_customer, import_alert, extract_by_csv_map

# Remove an object from the session
def remove_object_from_session(request, key):
    if key in request.session:
        del request.session[key]
        # Save the session after modification
        request.session.modified = True

def get_common_context(request, page_title: str):
    context_dict = {'page_title': page_title, 'session_data': request.session,'agency': None}
    if 'agency_name' in request.session: # session has agency
        db_agency = Agency.objects.filter(name=request.session['agency_name']).first()
        if db_agency:
            context_dict['agency'] = db_agency
    else: 
        # user_group = request.user.groups.all()[0]
        db_user_agencies = AgencyUser.objects.filter(user=request.user).all()
        if db_user_agencies:
            if db_user_agencies.count() == 1: # only one agency auto-select it
                context_dict['agency'] = db_user_agencies[0].agency
    if 'selected_alert_id' in request.session:
        db_alert = PolicyAlert.objects.get(id=int(request.session['selected_alert_id']))
        if db_alert:
            context_dict['alert'] = db_alert
    return context_dict

# Create your views here.
@login_required
def login_agency(request):
    context_dict = get_common_context(request, 'Select Agency')
    context_dict['agency_list'] = []
    if request.method == "POST":
        af = AgencyForm(request.POST)
        if af.is_valid():
            if 'agency_name' in af.cleaned_data: 
                agency_name = af.cleaned_data['agency_name']
                db_agency = Agency.objects.filter(name=agency_name).first()
                if db_agency:
                    request.session['agency_name'] = db_agency.name
                    return redirect('index')
    db_user_agencies = AgencyUser.objects.filter(user=request.user).all()
    if db_user_agencies:
        if db_user_agencies.count() == 1:
            request.session['agency_name'] = db_user_agencies[0].agency.name
            return redirect('index')
    context_dict['agency_list'] = Agency.objects.all()
    # for agency in Agency.objects.all():
    #    context_dict['agency_list'].append(agency)
    return render(request, 'registration/login_agency.html', context=context_dict)


@login_required
def index(request):
    context_dict = get_common_context(request, 'Notifications')
    context_dict['alerts']= None
    if 'agency' in context_dict.keys():
        alerts = PolicyAlert.objects.filter(agency=context_dict['agency']).all()
        context_dict['alerts'] = alerts
    else:
        return redirect('login_agency')
    return render(request, 'sd_main/dash/notifications.html', context=context_dict)

@login_required
def select_alert(request):
    if request.method == "POST":
        selected_alert_id = request.POST.get('selected_alert_id')
        if selected_alert_id:
            db_alert = PolicyAlert.objects.get(id=int(selected_alert_id))
            if db_alert:
                request.session['selected_alert_id'] = db_alert.id
    return redirect('index')


@login_required
def customers(request):
    context_dict = get_common_context(request, 'Customers')
    context_dict['customers']= None
    if 'agency' in context_dict.keys():
        customers = Customer.objects.filter(agency=context_dict['agency']).all()
    else:
        return redirect('login_agency')
    context_dict['customers'] = customers

    return render(request, 'sd_main/dash/customers.html', context_dict)

@login_required
def policies(request):
    context_dict = get_common_context(request, 'Policies')
    context_dict['policies']= None
    if 'agency' in context_dict.keys():
        policies = Policy.objects.filter(agency=context_dict['agency']).all()
    else:
        return redirect('login_agency')
    context_dict['policies'] = policies
    return render(request, 'sd_main/dash/policies.html', context_dict)

def get_google_auth_flow():
    db_gmail_client = db_gmail_redirect_url = None
    db_gmail_client = SystemSetting.objects.filter(name=SystemSetting.GMAIL_CLIENT_ID).first()
    db_gmail_redirect_url = SystemSetting.objects.filter(name=SystemSetting.GMAIL_REDIRECT_URL).first()
    if db_gmail_client and db_gmail_redirect_url:
        text_client_secret = json.dumps(db_gmail_client.json_value)
        file_client_secret = f"{tempfile.gettempdir()}/client_secret.json"
        with open(file_client_secret, "w") as file:
            file.write(text_client_secret)       
        # Required, call the from_client_secrets_file method to retrieve the client ID from a
        # client_secret.json file. The client ID (from that file) and access scopes are required. (You can
        # also use the from_client_config method, which passes the client configuration as it originally
        # appeared in a client secrets file but doesn't access the file itself.)
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(file_client_secret, scopes=constants.GMAIL_SCOPES)

        # Required, indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = db_gmail_redirect_url.text_value
        return flow

def get_google_auth_url(db_auth_email):
    flow = get_google_auth_flow()
    if flow and db_auth_email:
        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Recommended, enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Optional, enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',
            # Optional, if your application knows which user is trying to authenticate, it can use this
            # parameter to provide a hint to the Google Authentication Server.
            login_hint=db_auth_email.text_value, # 'hint@example.com',
            # Optional, set prompt to 'consent' will prompt the user for consent
            prompt='consent')
        return authorization_url, state
    return None, None

def get_gmail_credentials(db_agency: AgencySetting):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    creds = None
    db_token = AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.AGENCY_OAUTH_TOKEN).first()
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if db_token: # os.path.exists("token.json"):
        text_token = json.dumps(db_token.json_value)
        file_token = f"{tempfile.gettempdir()}/token.json"
        with open(file_token, "w") as file:
            file.write(text_token)
        creds = Credentials.from_authorized_user_file(file_token, constants.GMAIL_SCOPES)
        # If credentials expired, let the user refresh.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save the refreshed credentials for the next run
                db_token.json_value = creds.to_json()
                db_token.save()
    return creds

@login_required
def email_oauth(request):
    context_dict = get_common_context(request, 'Agency Settings')
    db_gmail_provider = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_PROVIDER).first()
    db_gmail = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_EMAIL).first()
    db_gmail_client = None
    if db_gmail_provider and db_gmail_provider.text_value == AgencySetting.AUTH_PRIVIDER_GOOGLE:
        db_gmail_client = SystemSetting.objects.filter(name=SystemSetting.GMAIL_CLIENT_ID).first()
    if request.method == "POST":
        provider = request.POST.get('provider')
        if provider:            
            if db_gmail_provider:
                db_gmail_provider.text_value = provider.lower()
                db_gmail_provider.save()
            else:
                db_gmail_provider = AgencySetting.objects.create(agency=context_dict['agency'],
                                                    name=AgencySetting.AGENCY_OAUTH_PROVIDER, text_value=provider)
        provider_email = request.POST.get('email')
        if provider_email:
            if db_gmail:
                db_gmail.text_value = provider_email.lower()
                db_gmail.save()
            else:
                db_gmail = AgencySetting.objects.create(agency=context_dict['agency'],
                                                    name=AgencySetting.AGENCY_OAUTH_EMAIL, text_value=provider_email)
    context_dict['provider'] = context_dict['email'] = context_dict['client_id'] = None
    if db_gmail_provider:
        context_dict['provider'] = db_gmail_provider.text_value
    if db_gmail:
        context_dict['email'] = db_gmail.text_value
    if db_gmail_client:
        context_dict['client_id'] = db_gmail_client.json_value

    context_dict['auth_token'] = context_dict['auth_url'] = None
    if db_gmail_provider and db_gmail:
        db_token = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_TOKEN).first()
        if db_token:
            context_dict['auth_token'] = db_token.json_value
        auth_url, state = get_google_auth_url(db_gmail)
        if auth_url and state:
            context_dict['auth_url'] = auth_url
    return render(request, 'sd_main/dash/email_oauth.html', context_dict)

@login_required
def gmail_oauth_authorize(request):
    context_dict = get_common_context(request, 'Agency Settings')
    # db_gmail_provider = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_PROVIDER).first()
    db_gmail = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_EMAIL).first()
    auth_url, state = get_google_auth_url(db_gmail)
    request.session['state'] = state
    return redirect(auth_url)

# @login_required - not required
# sample: http://localhost:8000/accounts/login/?next=/gmail_oauth_callback/%3Fstate%3DZiNxYBOuAFxlA45t7JeBMOxGxld6FY%26code%3D4/0AUJR-x4LXrMoL_3erqmJqfb9lYJytm3R7IHWYmoPiB_if0pSkyhS12DkFKRy-XX7RmpemQ%26scope%3Dhttps%3A//www.googleapis.com/auth/gmail.send
# How do we know: agency from callback ?
def gmail_oauth_callback(request):
    request_state = session_state =  None
    if 'code' not in request.GET:
        return HttpResponse("Authorization failed", status=400)
    if 'state' in request.session:
        session_state = request.session['state']
    context_dict = get_common_context(request, 'Gmail Callback')
    if 'state' in request.GET:        
        request_state = request.GET['state']
        remove_object_from_session(request, 'state')
    if session_state == request_state and context_dict['agency']:
        flow = get_google_auth_flow()
        flow.fetch_token(code=request.GET['code']) # fetch and fill token from gmail
        creds = flow.credentials
        token_json_value = json.loads(creds.to_json())
        # Store the credentials in database
        db_token = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_TOKEN).first()
        if db_token:
            db_token.json_value = token_json_value
            db_token.save()
        else:
            db_token = AgencySetting.objects.create(agency=context_dict['agency'],
                                                    name=AgencySetting.AGENCY_OAUTH_TOKEN, 
                                                    json_value=token_json_value)
    """
    gmail_credentials= {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        "universe_domain": "googleapis.com", 
        "account": "",
        "expiry": "2025-05-20T03:58:10.318793Z"
    } """
    return redirect("email_oauth")

@login_required
def gmail_oauth_revoke(request):
    import requests
    # from google.auth.transport.requests import Request
    context_dict = get_common_context(request, 'Email Auth Revoke')
    # db_gmail_provider = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_PROVIDER).first()
    # db_gmail = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_EMAIL).first()
    credentials = get_gmail_credentials(context_dict['agency'])
    revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})
    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        print('Credentials successfully revoked.')
        db_token = AgencySetting.objects.filter(agency= context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_TOKEN).first()
        if db_token:
            db_token.delete()
    return redirect("email_oauth")

@login_required
def email_oauth_test(request):
    import base64
    from email.message import EmailMessage
    from googleapiclient.discovery import build
    # from .gmail_api import create_message, send_message
    context_dict = get_common_context(request, 'Gmail Callback')
    db_gmail = AgencySetting.objects.filter(agency=context_dict['agency'], name=AgencySetting.AGENCY_OAUTH_EMAIL).first()
    creds = get_gmail_credentials(context_dict['agency'])
    try: 
        service = build('gmail', 'v1', credentials=creds)
        msg = EmailMessage()
        msg.set_content("test message from dj_sd")
        msg['To'] = "rudrawal@avconnect.ai"
        msg['From'] = db_gmail.text_value
        msg['Subject'] = 'DJ_SD: Test email'
        message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        body = {'raw': message}
        send_message = (
                service.users()
                .messages()
                .send(userId="me", body=body)
                .execute()
        )
        print(F'Message Id: {send_message["id"]}')
    except Exception as error:
        print(F'An error occurred: {error}')
    """
    service = build("gmail", "v1", credentials=creds)
    subject="Test OAUTH gmail", 
    email_text="test message from gmail oauth"
    message = create_message(sender=db_gmail.text_value, to='ajay_rudrawal@hotmail.com', subject=subject, message_text=email_text)
    send_message(service, db_gmail.text_value, message)
    """
    return redirect("email_oauth")

@login_required
def send_email(request, template_id=None):
    # get templates from db, default
    context_dict = get_common_context(request, 'Send Email')
    templates = EmailTemplate.objects.filter(agency=context_dict['agency']).order_by('name').all()
    if template_id:
        instance = get_object_or_404(EmailTemplate, agency=context_dict['agency'], name=template_id)
        form = EmailTemplateForm(request.POST or None, instance=instance)
    elif templates and len(templates) > 0:
        form = EmailTemplateForm(request.POST or None, instance=templates[0])
    else:
        form = EmailTemplateForm(request.POST or None, initial={})
    variables = {}
    if 'agency' in context_dict:
        agency = context_dict['agency']
        variables['agent_full_name'] = agency.name or ""
        variables['contact_email_address'] = agency.contact_email or ""
        variables['contact_phone_number'] = agency.contact_phone or ""
        variables['insurance_company_name'] = agency.company.name or ""
    if 'alert' in context_dict:
        policy = context_dict['alert'].policy
        customer = context_dict['alert'].customer
        variables['policy_number'] = policy.number or ""
        variables['policy_type'] = policy.lob or ""
        variables['expiration_date'] = policy.end_date or ""
        variables['customer_name'] = customer.name or ""
        variables['customer_email'] = customer.email or ""
        variables['customer_phone'] = customer.phone or ""
    context_dict['form'] = form
    template_data = {t.id: {"id": t.id,
                            "name": t.name,
                            "subject_line": t.subject_line,
                            "body": t.body,
                            "updated_at": t.updated_at.strftime("%Y-%m-%d")}
                     for t in templates
                     }

    return render(
        request,
        'sd_main/email/edit_template.html',
        {
            **context_dict,
            'variables': variables,
            'variables_data': mark_safe(json.dumps(variables)),
            'templates': templates,
            'templates_data': mark_safe(json.dumps(template_data)),
        })

@login_required
def vehicles(request):
    context_dict = get_common_context(request, 'Vehicles')
    return render(request, 'sd_main/dash/vehicles.html', context_dict)

@login_required
def drivers(request):
    context_dict = get_common_context(request, 'Drivers')
    return render(request, 'sd_main/dash/drivers.html', context_dict)

@login_required
def upload_policy(request):
    context_dict = get_common_context(request, 'Import Data')
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # if the post request has a file under the input name 'policy_file', then save the file.
        request_file = request.FILES['policy_file'] if 'policy_file' in request.FILES else None
        if request_file and context_dict['agency']: # save attached file
            db_agency = Agency.objects.filter(name=context_dict['agency'].name).first()
            # fs = FileSystemStorage()
            # file = fs.save(request_file.name, request_file)
            # uploaded_file_url = fs.url(file)
            df_agency_upload = convert_to_dataframe(request_file)
            if len(df_agency_upload.index) and db_agency:
                add_cust = update_cust = 0
                customer_map_dict = None
                customer_map = AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.CUSTOMER_CSV_MAP).first()
                if customer_map:
                    customer_map_dict = customer_map.json_value
                    df_customer = extract_by_csv_map(df_agency_upload, customer_map_dict)
                    if len(df_customer.index):
                        add_cust, update_cust = import_customer(df_customer, db_agency)
                add_policy = update_policy = 0
                policy_map_dict = None
                policy_map = AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.POLICY_CSV_MAP).first()
                if policy_map:
                    policy_map_dict = policy_map.json_value
                    combined_dict = policy_map_dict | customer_map_dict
                    df_policy = extract_by_csv_map(df_agency_upload, combined_dict)
                    if len(df_policy.index):
                        add_policy, update_policy = import_policy(df_policy, db_agency)
                add_alert = update_alert = 0
                alert_map = AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.ALER_CSV_MAP).first()
                if alert_map:
                    alert_map_dict = alert_map.json_value
                    combined_map_dict = alert_map_dict|policy_map_dict|customer_map_dict
                    df_alert = extract_by_csv_map(df_agency_upload, combined_map_dict)
                    if len(df_alert.index):
                        add_alert, update_alert = import_alert(df_alert, db_agency)
                context_dict['add_count'] = add_alert
                context_dict['update_count'] = update_alert
                # html_table = df_policy.to_html()
                # return render(request, "sd_main/dash/upload.html", context_dict)
            else: # file is rejected
                context_dict['add_count'] = context_dict['update_count'] = 0
                context_dict['error'] = f'{request_file.name}: empty or invalid file!'
                # return render(request, "sd_main/dash/upload.html", context_dict)
    return render(request, "sd_main/dash/upload.html", context=context_dict)

