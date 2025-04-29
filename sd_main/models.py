import uuid
from django.db import models
from django.urls import reverse

class GroupSetting(models.Model):
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value =  models.TextField(max_length=1024)
    json_value =  models.JSONField()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'name'], name='unique_group_setting')
        ]
    def __str__(self):
        return f"{self.group} {self.name}"

class Driver(models.Model):
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    driving_license = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField()

class Vehicle(models.Model):
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    vin = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=50)
    reg_end_date = models.DateField()
    registered_owner = models.CharField(max_length=100)

# Create your models here.
class Policy(models.Model):
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=100)
    # uuid to associate policy documents in cloud storage
    uuid = models.UUIDField(default=uuid.uuid4,
                          help_text="Unique ID for this particular policy across whole database")
    POLICY_TYPE = (
        ('auto', 'Auto'),
        ('life', 'Life'),
    )
    policy_type = models.CharField(max_length=32, choices=POLICY_TYPE, default='auto', blank=False, help_text='Policy type')
    policy_owner = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=False, blank=False)
    POLICY_STATUS = (
        ('e', 'Expired'),
        ('r', 'Renewal'),
        ('c', 'Completed'),
        ('n', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=POLICY_STATUS,
        blank=True,
        default='r',
        help_text='Renewal pending',
    )
    owner_phone = models.CharField(max_length=100, null=True, blank=True)
    owner_email = models.CharField(max_length=100, null=True, blank=True)
    
    # ManyToManyField used because vehicle can have many policies and policy can cover many vehicles.
    vehicle = models.ManyToManyField(
        Vehicle, help_text="Select a vehicle for this policy")
    # ManyToManyField used because driver can appear in many policies and policy can cover many drivers.
    driver = models.ManyToManyField(
        Driver, help_text="Select a driver for this policy")
    
    def __str__(self):
        """String for representing the Model object."""
        return self.policy_number
    
    def get_absolute_url(self):
        """Returns the url to access a particular policy instance."""
        return reverse('policy-detail', args=[str(self.id)])

class PolicyDocument(models.Model):
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4,
                          help_text="Unique ID for this particular policy document")
    policy_id = models.ForeignKey('Policy', on_delete=models.CASCADE)
    file_name_uploaded = models.CharField(max_length=512)
    file_name_cloud = models.CharField(max_length=512)
    file_type = models.CharField(max_length=32)
    file_text_extract = models.TextField(null=True)

