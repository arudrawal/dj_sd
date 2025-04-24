from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadPolicyForm
from django.core.files.storage import FileSystemStorage

# Create your views here.
def index(request):
    return render(request, 'sd_main/dash/notifications.html')

def vehicles(request):
    return render(request, 'sd_main/dash/vehicles.html')

def drivers(request):
    return render(request, 'sd_main/dash/drivers.html')

def upload_policy(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # if the post request has a file under the input name 'document', then save the file.
        request_file = request.FILES['policy_file'] if 'policy_file' in request.FILES else None
        if request_file: # save attached file
            fs = FileSystemStorage()
            file = fs.save(request_file.name, request_file)
            uploaded_file_url = fs.url(file)
            return render(request, "sd_main/dash/upload.html", {'uploded_file_url': uploaded_file_url})
    # else:
    #    policy_form = UploadPolicyForm(request.GET)
    return render(request, "sd_main/dash/upload.html")

