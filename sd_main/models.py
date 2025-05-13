import uuid
from django.db import models
from django.urls import reverse
from django.conf import settings

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
    active = models.BooleanField(default=True)
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
    active = models.BooleanField(default=True)
    # Other fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AgencySetting(models.Model):
    POLICY_CSV_MAP = 'policy_csv_map'
    CUSTOMER_CSV_MAP = 'customer_csv_map'
    ALER_CSV_MAP = 'alert_csv_map'
    NAME_CHOICES = {
        POLICY_CSV_MAP: POLICY_CSV_MAP,
        CUSTOMER_CSV_MAP: CUSTOMER_CSV_MAP,
        ALER_CSV_MAP: ALER_CSV_MAP,
    }
    name = models.CharField(max_length=100, choices=NAME_CHOICES, blank=False)
    text_value =  models.TextField(max_length=1024)
    json_value = models.JSONField()
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['agency', 'name'], name='unique_agency_setting')
        ]
    def __str__(self):
        return f"{self.agency} {self.name}"

""" Customers are policy owners, can own multiple polices. """
class Customer(models.Model):
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    company_account = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=128)
    dob = models.DateField()
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
    number = models.CharField("Policy Number", max_length=128)
    start_date = models.DateField(null=True, blank=False)
    end_date = models.DateField(null=True, blank=False)
    LOB = (
        ('Auto', 'Auto'),
        ('Home', 'Home'),
        ('Life', 'Life'),
    )
    lob = models.CharField(max_length=32, choices=LOB, default='auto', blank=False, help_text='Policy business type')

# Alert for a specific Policy
class PolicyAlert(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE) # multiple alerts => one customers
    policy = models.ForeignKey("Policy", on_delete=models.CASCADE) # one alert =>one policy
    alert_level = models.CharField("Critical/Pending", max_length=128)
    due_date = models.DateField(null=True, blank=True)
    created_date = models.DateField(null=False, blank=False)
    work_status = models.CharField("InProgress/New", max_length=128)
    alert_category = models.CharField("Alert Reason Summary", max_length=128)
    alert_sub_category = models.CharField("Alert Reason details", max_length=512)
    agency = models.ForeignKey("Agency", on_delete=models.CASCADE) # multiple alerts => one agency
    # ManyToManyField used because vehicle can have many policies and policy can cover many vehicles.
    # vehicle = models.ManyToManyField(
    #    Vehicle, help_text="Select a vehicle for this policy")
    # ManyToManyField used because driver can appear in many policies and policy can cover many drivers.
    # driver = models.ManyToManyField(
    #    Driver, help_text="Select a driver for this policy")
    
    def __str__(self):
        """String for representing the Model object."""
        return self.policy_number
    
    def get_absolute_url(self):
        """Returns the url to access a particular policy instance."""
        return reverse('policy-detail', args=[str(self.id)])

class PolicyDocument(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,
                          help_text="Unique ID for this particular policy document")
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    file_name_uploaded = models.CharField(max_length=512)
    file_name_cloud = models.CharField(max_length=512)
    file_type = models.CharField(max_length=32)
    file_text_extract = models.TextField(null=True)

class Driver(models.Model):
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    driving_license = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField()

class Vehicle(models.Model):
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    vin = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=50)
    reg_end_date = models.DateField()
    registered_owner = models.CharField(max_length=100)
