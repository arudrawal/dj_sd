from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import UploadPolicyForm
from .import_data import convert_to_dataframe, import_policy
from .models import Agency, AgencySetting, Policy

def get_common_context(request, page_title: str):
    context_dict = {'page_title': page_title, 'agency_name': ''}
    if request.user.groups.all():
        user_group = request.user.groups.all()[0]
        if user_group:
            context_dict['group'] = user_group
            agency = Agency.objects.filter(group=user_group).first()
            if agency:
                context_dict['agency'] = agency
    return context_dict

# Create your views here.
@login_required
def index(request):
    context_dict = get_common_context(request, 'Notifications')
    context_dict['policies']= None
    if 'group' in context_dict.keys():
        policies = Policy.objects.filter(group=context_dict['group'])
    else:
        policies = Policy.objects.all()
    context_dict['policies'] = policies
    return render(request, 'sd_main/dash/notifications.html', context=context_dict)

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
        if request_file and context_dict['agency_name']: # save attached file
            # fs = FileSystemStorage()
            # file = fs.save(request_file.name, request_file)
            # uploaded_file_url = fs.url(file)
            customer_map = AgencySetting.objects.filter(group=context_dict['group'], name=AgencySetting.CUSTOMER_CSV_MAP).first()
            policy_map = AgencySetting.objects.filter(group=context_dict['group'], name=AgencySetting.POLICY_CSV_MAP).first()
            alert_map = AgencySetting.objects.filter(group=context_dict['group'], name=AgencySetting.ALER_CSV_MAP).first()
            df_policy = convert_to_dataframe(request_file)
            if len(df_policy.index):
                add_count, update_count = import_policy(df_policy, context_dict['agency_name'])
                context_dict['add_count'] = add_count
                context_dict['update_count'] = update_count
                # html_table = df_policy.to_html()
                return render(request, "sd_main/dash/upload.html", context_dict)
            else: # file is rejected
                context_dict['add_count'] = context_dict['update_count'] = 0
                context_dict['error'] = f'{request_file.name}: empty or invalid file!'
                return render(request, "sd_main/dash/upload.html", context_dict)

    # else:
    #    policy_form = UploadPolicyForm(request.GET)
    return render(request, "sd_main/dash/upload.html")

