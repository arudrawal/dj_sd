from django.contrib import admin
from .models import Company, Customer, Agency, AgencySetting, AgencyUser
from .models import Driver, Vehicle, Policy, PolicyDocument

# Register your models here.
# admin.site.register(Policy)
# Define the admin class
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'contact')

class AgencySettingAdmin(admin.ModelAdmin):
    list_display = ('agency', 'name', 'text_value', 'json_value')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'agency')

class PolicyAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'start_date', 'end_date', 'lob')

# Register the admin class with the associated model
admin.site.register(Company, CompanyAdmin)
admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyUser)
admin.site.register(AgencySetting, AgencySettingAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(PolicyDocument)
