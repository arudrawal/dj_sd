import os
import sys
import django

SUPER_USER='admin'
SUPER_PASS='secret1#'
GROUP1 = 'asharma_agency'
EMAIL='ajay@shivark.com'

def create_users():
    from django.contrib.auth.models import User
    from django.contrib.auth.models import Group
    if not User.objects.filter(username=SUPER_USER).exists():
        User.objects.create_superuser(username=SUPER_USER, email=EMAIL, password=SUPER_PASS)
 
    asharma_group, created = Group.objects.get_or_create(name=GROUP1)
 
    if not User.objects.filter(username='ajay').exists():
        user_ajay = User.objects.create_user("ajay", EMAIL, SUPER_PASS)
        # user_ajay.groups.add(asharma_group)
        asharma_group.user_set.add(user_ajay)

if __name__ == '__main__':
   sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
   os.environ['DJANGO_SETTINGS_MODULE'] = 'sd_proj.settings'
   django.setup()
   create_users()

