from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadPolicyForm

# Create your views here.
def index(request):
    return render(request, 'sd_main/dash/notifications.html')

def vehicles(request):
    return render(request, 'sd_main/dash/vehicles.html')

def drivers(request):
    return render(request, 'sd_main/dash/drivers.html')

def upload(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = UploadPolicyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect("/thanks/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UploadPolicyForm()

    return render(request, "name.html", {"form": form})

def upload(request):
    return render(request, 'sd_main/dash/upload.html')
