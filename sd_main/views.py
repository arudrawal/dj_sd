from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadPolicyForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    return render(request, 'sd_main/dash/notifications.html')

@login_required
def vehicles(request):
    return render(request, 'sd_main/dash/vehicles.html')

@login_required
def drivers(request):
    return render(request, 'sd_main/dash/drivers.html')

@login_required
def upload_policy(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # if the post request has a file under the input name 'policy_file', then save the file.
        request_file = request.FILES['policy_file'] if 'policy_file' in request.FILES else None
        if request_file: # save attached file
            fs = FileSystemStorage()
            file = fs.save(request_file.name, request_file)
            uploaded_file_url = fs.url(file)
            return render(request, "sd_main/dash/upload.html", {'uploded_file_url': uploaded_file_url})
    # else:
    #    policy_form = UploadPolicyForm(request.GET)
    return render(request, "sd_main/dash/upload.html")

