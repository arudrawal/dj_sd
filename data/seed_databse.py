import os
import sys
import django

SUPER_USER = 'admin'
SUPER_PASS = 'secret1#'
COMPANY_LIST = ['Farmers', 'State Farm', 'All State']
GROUPS = ['asharma_group', 'bobs_group', 'chucks_group']
AGENCIES = [{'name': 'Archana Agency', 'company': COMPANY_LIST[0], 'group': GROUPS[0]},
            {'name': 'Bobs Agency', 'company': COMPANY_LIST[1], 'group': GROUPS[1]},
            {'name': 'Chucks Agency', 'company': COMPANY_LIST[2], 'group': GROUPS[2]},
        ]
DOMAIN_EMAIL = 'shivark.com'
AJAY_EMAIL = f'ajay@{DOMAIN_EMAIL}'
MUKESH_EMAIL = f'mukesh@{DOMAIN_EMAIL}'
ARCHANA_EMAIL = f'archana@{DOMAIN_EMAIL}'
USERS = [{'user_name':'ajay', 'email': AJAY_EMAIL, 'password': SUPER_PASS, 'groups': [GROUPS[0], GROUPS[1]]},
         {'user_name':'mukesh', 'email': MUKESH_EMAIL, 'password': SUPER_PASS, 'groups': [GROUPS[0]]},
         {'user_name':'archana', 'email': ARCHANA_EMAIL, 'password': SUPER_PASS, 'groups': [GROUPS[0]]},
        ]

def create_admin_user():
    from django.contrib.auth.models import User
    # Admin user
    if not User.objects.filter(username=SUPER_USER).exists():
        db_admin = User.objects.create_superuser(username=SUPER_USER, email=AJAY_EMAIL, password=SUPER_PASS)
        return db_admin
    return User.objects.filter(username=SUPER_USER).first()

def create_groups(group_list: list):
    from django.contrib.auth.models import Group
    # Create groups - indexed by group name
    db_groups = {}
    for group in group_list:
        db_group, created = Group.objects.get_or_create(name=group)
        db_groups[group] = db_group
        # db_group.user_set.add(db_user)
    return db_groups

# Admin user
#if not User.objects.filter(username=SUPER_USER).exists():
#    User.objects.create_superuser(username=SUPER_USER, email=AJAY_EMAIL, password=SUPER_PASS)
# Create groups - indexed by group name
#db_groups = {}
#for group in GROUPS:
#    db_group, created = Group.objects.get_or_create(name=group)
#    db_groups[group] = db_group
#    # db_group.user_set.add(db_user)

def create_other_users(user_list: list, db_groups: dict):
    from django.contrib.auth.models import User
    db_users = {}
    for user in user_list:
        if not User.objects.filter(username=user['user_name']).exists():
            db_user = User.objects.create_user(user['user_name'], user['email'], user['password'])
            for user_group in user['groups']:
                db_user.groups.add(db_groups[user_group])
            db_users[user['user_name']] = db_user
    return db_users

def create_company():
    from sd_main.models import Company
    # Insurance Companies
    db_companies = {}
    for company_name in COMPANY_LIST:
        db_company = Company.objects.filter(name=company_name).first()
        if not db_company: # Company.objects.filter(name=company).exists():
            db_company = Company.objects.create(name=company_name)
        db_companies[company_name] = db_company
    return db_companies

def create_agencies(agency_list: dict, company_dict: dict, group_dict: dict):
    from sd_main.models import Agency
    db_agencies = {}
    for agency in agency_list:
        if not Agency.objects.filter(name=agency['name']).exists():
            db_agency = Agency.objects.create(name=agency['name'], group=group_dict[agency['group']], company=company_dict[agency['company']])
            db_agencies[agency['name']] = db_agency
    return db_agencies

if __name__ == '__main__':
   new_root = os.path.join(os.path.dirname(__file__), '..')
   print (f"New root: {new_root}")
   exit
   sys.path.append(new_root)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'sd_proj.settings'
   django.setup()
   create_admin_user()
   db_groups = create_groups(GROUPS)
   print (f"Created Groups: {db_groups.keys()}")
   db_users = create_other_users(USERS, db_groups)
   print (f"Created Users: {db_users.keys()}")
   db_companies = create_company()
   print (f"Created Companies: {db_companies.keys()}")
   db_agencies = create_agencies(AGENCIES, db_companies, db_groups)
   print (f"Created Agencies: {db_agencies.keys()}")
