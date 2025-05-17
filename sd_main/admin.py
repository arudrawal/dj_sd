from django.contrib import admin
from .models import Company, Customer, Agency, AgencySetting, AgencyUser, PolicyAlert
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

class PolicyAlertAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'policy_number', 'alert_level', 'due_date', 'created_date', 'work_status', 'alert_category','alert_sub_category', 'agency_name')
    def customer_name(self, obj):
        return obj.customer.name
    
    def policy_number(self, obj):
        return obj.policy.number
    
    def agency_name(self, obj):
        return obj.agency.name


# Register the admin class with the associated model
admin.site.register(Company, CompanyAdmin)
admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyUser)
admin.site.register(AgencySetting, AgencySettingAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(PolicyAlert, PolicyAlertAdmin)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(PolicyDocument)
