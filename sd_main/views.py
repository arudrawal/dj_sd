from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import UploadPolicyForm
from .forms import AgencyForm

from .models import Agency, AgencyUser, AgencySetting, Policy, PolicyAlert, Customer

from .import_data import convert_to_dataframe, import_policy, import_customer, import_alert, extract_by_csv_map


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
            request.session['agency_name'] = db_user_agencies[0].name
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

