from django.contrib import admin
from .models import Driver, Vehicle, Policy, PolicyDocument

# Register your models here.
# admin.site.register(Policy)
# Define the admin class
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'policy_owner', 'start_date', 'end_date', 'policy_type')

# Register the admin class with the associated model
admin.site.register(Policy, PolicyAdmin)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(PolicyDocument)
