import uuid
from django.db import models
from django.urls import reverse
from django.conf import settings
from . import constants

class SystemSetting(models.Model):
    GMAIL_CLIENT_ID = 'gmail_client_id'
    GMAIL_REDIRECT_URL = 'gmail_redirect_url'
    name = models.TextField(primary_key=True, max_length=256, null=False, blank=False)
    text_value = models.TextField(
        max_length=1024, # Length in the forms
        null=True,  # Allows the field to be empty
        blank=True, # Makes the field optional in forms
        default=None)
    json_value = models.JSONField(null=True, blank=True, default=None)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_system_setting')
        ]
    def __str__(self):
        return f"{self.name}"

""" Insurance Carrier. """
class Company(models.Model):
    name = models.CharField(max_length=128, unique=True)
    # Other fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name}"


""" Insurance Agency - between customer and carrier. """
class Agency(models.Model):
    name = models.CharField(max_length=128, unique=True)
    number = models.CharField(max_length=128)
    contact = models.CharField(max_length=128)
    contact_email = models.CharField(max_length=128)
    contact_phone = models.CharField(max_length=128)
    timezone = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    # Other fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # many-rows=>one-company [one company for many agencies]
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    # users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='AgencyUser')

""" Insurance Agency - users assigned. """
class AgencyUser(models.Model):
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='id')
    is_active = models.BooleanField(default=True)
    # Other fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AgencySetting(models.Model):
    POLICY_CSV_MAP = 'policy_csv_map'
    CUSTOMER_CSV_MAP = 'customer_csv_map'
    ALER_CSV_MAP = 'alert_csv_map'
    AGENCY_OAUTH_PROVIDER = 'oauth_provider' # Google, Office, AWS
    AGENCY_OAUTH_TOKEN = 'oauth_token'   # Granted Token
    AGENCY_OAUTH_EMAIL = 'oauth_email'   # Email account - used to send emails
    
    NAME_CHOICES = {
        POLICY_CSV_MAP: POLICY_CSV_MAP,
        CUSTOMER_CSV_MAP: CUSTOMER_CSV_MAP,
        ALER_CSV_MAP: ALER_CSV_MAP,
        AGENCY_OAUTH_PROVIDER: AGENCY_OAUTH_PROVIDER,
        AGENCY_OAUTH_TOKEN: AGENCY_OAUTH_TOKEN,
        AGENCY_OAUTH_EMAIL: AGENCY_OAUTH_EMAIL,
    }
    # This goes to name for
    AUTH_PRIVIDER_GOOGLE = 'google'

    name = models.TextField(max_length=256, blank=False, null=False)
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE)
    text_value =  models.TextField(max_length=1024, blank=True, null=True)
    json_value = models.JSONField(null=True, blank=True)
    # Other fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['agency', 'name'], name='unique_agency_setting')
        ]
    def __str__(self):
        return f"{self.agency} {self.name}"

""" Customers are policy owners, can own multiple polices. """
class Customer(models.Model):
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE)
    name = models.CharField(max_length=128, db_column=constants.CUSTOMER_NAME_COLUMN)
    company_account = models.CharField(max_length=128, null=True, db_column=constants.CUSTOMER_COMPANY_ACCOUNT)
    email = models.CharField(max_length=256, null=True, blank=True, db_column=constants.CUSTOMER_EMAIL_COLUMN)
    phone = models.CharField(max_length=128, null=True, blank=True, db_column=constants.CUSTOMER_PHONE_COLUMN)
    dob = models.DateField(null=True, db_column=constants.CUSTOMER_DOB_COLUMN)
    # Other fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Policy model - one customer can have multiple polices
class Policy(models.Model):
    # uuid to associate policy documents in cloud storage
    # uuid = models.UUIDField(default=uuid.uuid4,
    #                      help_text="Unique ID for this particular policy across whole database")
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE) # many=>one: multiple policies for one customer
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE) # many=>one: multiple policeis for one agency
    number = models.CharField("Policy Number", max_length=128, db_column=constants.POLICY_NUMBER_COLUMN)
    start_date = models.DateField(null=True, blank=True, db_column=constants.POLICY_START_DATE_COLUMN)
    end_date = models.DateField(null=True, blank=True, db_column=constants.POLICY_END_DATE_COLUMN)
    premium_amount = models.DecimalField(null=True, blank=True, db_column=constants.POLICY_PREMIUM_COLUMN, decimal_places=2, max_digits=10)
    LOB = (
        ('Auto', 'Auto'),
        ('Home', 'Home'),
        ('Life', 'Life'),
        ('Umbrella' 'Umbrella'),
        ('Commercial', 'Commercial')
    )
    lob = models.CharField(max_length=32, blank=False, help_text='Policy business type', db_column=constants.POLICY_LOB_COLUMN)

# Alert for a specific Policy
class PolicyAlert(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE) # multiple alerts => one customers
    policy = models.ForeignKey("Policy", on_delete=models.CASCADE) # one alert =>one policy
    alert_level = models.CharField(max_length=128, db_column=constants.POLICY_ALERT_LEVEL_COLUMN) # "Critical/Pending"
    due_date = models.DateField(null=True, blank=True, db_column=constants.POLICY_ALERT_DUE_DATE_COLUMN)
    created_date = models.DateField(null=True, blank=True, db_column=constants.POLICY_ALERT_CREATED_DATE_COLUMN)
    work_status = models.CharField(max_length=128, null=True, db_column=constants.POLICY_ALERT_WORK_STATUS_COLUMN) # InProgress/New,
    alert_category = models.CharField(max_length=128, null=True, db_column=constants.POLICY_ALERT_CATEGORY_COLUMN) # Alert Reason Summary
    alert_sub_category = models.CharField(max_length=512, null=True, db_column=constants.POLICY_ALERT_SUB_CATEGORY_COLUMN) # Alert Reason details
    is_active = models.BooleanField(default=True)
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE) # multiple alerts => one agency
    # ManyToManyField used because vehicle can have many policies and policy can cover many vehicles.
    # vehicle = models.ManyToManyField(
    #    Vehicle, help_text="Select a vehicle for this policy")
    # ManyToManyField used because driver can appear in many policies and policy can cover many drivers.
    # driver = models.ManyToManyField(
    #    Driver, help_text="Select a driver for this policy")
    
    def __str__(self):
        """String for representing the Model object."""
        return f"{self.policy.number} - {self.alert_level}"
    
    def get_absolute_url(self):
        """Returns the url to access a particular policy instance."""
        return reverse('policy-detail', args=[str(self.id)])

class PolicyDocument(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,
                          help_text="Unique ID for this particular policy document")
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    file_name_uploaded = models.CharField(max_length=512)
    file_name_cloud = models.CharField(max_length=512)
    file_type = models.CharField(max_length=128)
    file_text_extract = models.TextField(null=True)

class Driver(models.Model):
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    driving_license = models.CharField(max_length=256)
    issue_date = models.DateField()
    expiry_date = models.DateField()

class Vehicle(models.Model):
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    vin = models.CharField(max_length=256)
    license_plate = models.CharField(max_length=256)
    reg_end_date = models.DateField()
    registered_owner = models.CharField(max_length=256)

class EmailTemplate(models.Model):
    name = models.CharField(max_length=256, null=False)
    subject_line = models.CharField(max_length=256, null=False)
    body = models.TextField(null=False)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    category = models.CharField(max_length=256, null=True) # applicable alert category
    sub_category = models.CharField(max_length=256, null=True) # applicable alert sub-category
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

# Maintain history of sent emails. 
# Agency/Customer - must exist to send email.
# Mail could related to Policy or Alert or could be normal communication.
# Policy/Alert/Template: may or may not be associated.
class SentEmail(models.Model):
    mail_to = models.CharField(max_length=256, null=False)
    subject_line = models.CharField(max_length=256, null=False)
    body = models.TextField(null=False)
    category = models.CharField(max_length=256, null=True) # context - if availabe
    sub_category = models.CharField(max_length=256, null=True) # context - if available
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True) # 
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, null=True)
    policy_alert = models.ForeignKey('PolicyAlert', on_delete=models.CASCADE, null=True)
    template = models.ForeignKey('EmailTemplate', on_delete=models.CASCADE, null=True)
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

class GoogleAuthContext(models.Model):
    state = models.TextField()
    auth_url = models.TextField()
    code = models.TextField(null=True)
    email = models.TextField(null=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='id')
    policy_alert = models.ForeignKey('PolicyAlert', on_delete=models.CASCADE, null=True)
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

"""
  Prompt template Key features:
  - template_text: Main prompt content with placeholder variables
  - versioning: Support for template versions via parent_template_id
  - usage_count: Track popularity
"""
class PromptTemplate(models.Model):
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=True)
    teplate_text = models.TextField(null=False)
    category = models.CharField(max_length=256, null=True) # context - if availabe
    sub_category = models.CharField(max_length=256, null=True) # context - if available    
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    version = models.IntegerField(default=1)
    parent_template_id = models.ForeignKey(
        'self',  # Refers to the same model
        on_delete=models.SET_NULL,  # What happens if the referenced row is deleted
        null=True,  # Allows the field to be empty
        blank=True,  # Makes the field optional in forms
        related_name='revisions'  # Reverse relation name
    )
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

