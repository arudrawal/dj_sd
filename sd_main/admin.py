from django.contrib import admin
from .models import Company, Customer, Agency, AgencySetting, AgencyUser, PolicyAlert
from .models import Driver, Vehicle, Policy, PolicyDocument, SystemSetting

# Register your models here.
# admin.site.register(Policy)
# Define the admin class
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'text_value', 'json_value')

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'contact')

class AgencyUserAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'user_name')
    def agency_name(self, obj):
        return obj.agency.name
    def user_name(self, obj):
        return obj.user.username

class AgencySettingAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'name', 'text_value', 'json_value')
    def agency_name(self, obj):
        return obj.agency.name

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
admin.site.register(SystemSetting, SystemSettingAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyUser, AgencyUserAdmin)
admin.site.register(AgencySetting, AgencySettingAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(PolicyAlert, PolicyAlertAdmin)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(PolicyDocument)
