from django.contrib import admin
from .models import Driver, Vehicle, Policy, PolicyDocument

# Register your models here.
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(Policy)
admin.site.register(PolicyDocument)
