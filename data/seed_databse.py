import os
import sys
import django

SUPER_USER = 'admin'
SUPER_PASS = 'secret1#'
COMPANY_LIST = ['Farmers', 'State Farm', 'All State']
GROUPS = ['asharma_group', 'bobs_group', 'chucks_group']
AGENCIES = [{'name': 'Archana Agency', 'company': COMPANY_LIST[0]},
            {'name': 'Bobs Agency', 'company': COMPANY_LIST[1]},
            {'name': 'Chucks Agency', 'company': COMPANY_LIST[2]},
        ]
CUSTOMER_MAP = {
    AGENCIES[0]['name']: {str.lower('Name'): 'name', str.lower('Billing Account'): 'company_account', str.lower('Email'): 'email', str.lower('Phone Number'): 'phone', str.lower('DOB'): 'dob'},
    AGENCIES[1]['name']: {str.lower('Name'): 'name', str.lower('Billing Account'): 'company_account', str.lower('Email'): 'email', str.lower('Phone Number'): 'phone', str.lower('DOB'): 'dob'},
    AGENCIES[2]['name']: {str.lower('Name'): 'name', str.lower('Billing Account'): 'company_account', str.lower('Email'): 'email', str.lower('Phone Number'): 'phone', str.lower('DOB'): 'dob'},
}
POLICY_MAP = {
    AGENCIES[0]['name']: {str.lower('Policy'): 'number', str.lower('LOB'): 'lob', str.lower('Policy Start Date'): 'start_date', str.lower('Policy End Date'): 'end_date'},
    AGENCIES[1]['name']: {str.lower('Policy'): 'number', str.lower('LOB'): 'lob', str.lower('Policy Start Date'): 'start_date', str.lower('Policy End Date'): 'end_date'},
    AGENCIES[2]['name']: {str.lower('Policy'): 'number', str.lower('LOB'): 'lob', str.lower('Policy Start Date'): 'start_date', str.lower('Policy End Date'): 'end_date'},
}
ALERT_MAP = {
    AGENCIES[0]['name']: {str.lower('Alert Classification'): 'alert_level', str.lower('Due Date'): 'due_date', 
                        str.lower('Created Date'): 'date_created', str.lower('Status'): 'work_status',
                        str.lower('Alert Category'): 'alert_category', str.lower('Alert Sub-Category'): 'alert_sub_category'},
    AGENCIES[1]['name']: {str.lower('Alert Classification'): 'alert_level', str.lower('Due Date'): 'due_date', 
                        str.lower('Created Date'): 'date_created', str.lower('Status'): 'work_status',
                        str.lower('Alert Category'): 'alert_category', str.lower('Alert Sub-Category'): 'alert_sub_category'},
    AGENCIES[2]['name']: {str.lower('Alert Classification'): 'alert_level', str.lower('Due Date'): 'due_date', 
                        str.lower('Created Date'): 'date_created', str.lower('Status'): 'work_status',
                        str.lower('Alert Category'): 'alert_category', str.lower('Alert Sub-Category'): 'alert_sub_category'},
}
DOMAIN_EMAIL = 'shivark.com'
AJAY_EMAIL = f'ajay@{DOMAIN_EMAIL}'
MUKESH_EMAIL = f'mukesh@{DOMAIN_EMAIL}'
ARCHANA_EMAIL = f'archana@{DOMAIN_EMAIL}'
USERS = [{'user_name':'ajay', 'email': AJAY_EMAIL, 'password': SUPER_PASS, 'groups': [GROUPS[0], GROUPS[1]]},
         {'user_name':'mukesh', 'email': MUKESH_EMAIL, 'password': SUPER_PASS, 'groups': [GROUPS[0]]},
         {'user_name':'archana', 'email': ARCHANA_EMAIL, 'password': SUPER_PASS, 'groups': [GROUPS[0]]},
        ]
AGENCY_USERS = {
    AGENCIES[0]['name']: ['ajay', 'mukesh', 'archana'],
    AGENCIES[1]['name']: ['ajay'],
    AGENCIES[2]['name']: ['ajay'],
}

def create_admin_user():
    from django.contrib.auth.models import User
    # Admin user
    db_admin = User.objects.filter(username=SUPER_USER).first()
    if not db_admin:
        db_admin = User.objects.create_superuser(username=SUPER_USER, email=AJAY_EMAIL, password=SUPER_PASS)
    return db_admin

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
        db_user = User.objects.filter(username=user['user_name']).first()
        if not db_user: # User.objects.filter(username=user['user_name']).exists():
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
    db_agencies_by_name = {}
    for agency in agency_list:
        db_agency = Agency.objects.filter(name=agency['name']).first()
        if not db_agency: # Agency.objects.filter(name=agency['name']).exists():
            db_agency = Agency.objects.create(name=agency['name'], company=company_dict[agency['company']])
        db_agencies_by_name[agency['name']] = db_agency
    return db_agencies_by_name

def create_agency_users():
    from sd_main.models import Agency, AgencyUser
    from django.contrib.auth.models import User
    for agency_name in AGENCY_USERS.keys():
        db_agency = Agency.objects.filter(name=agency_name).first()
        if db_agency:
            for uname in AGENCY_USERS[agency_name]:
                db_user = User.objects.filter(username=uname).first()
                if db_user:
                    db_au = AgencyUser.objects.filter(agency=db_agency, user=db_user).first()
                    if not db_au:
                        db_au = AgencyUser(agency=db_agency, user=db_user)
                        db_au.save()
                        print(f"Added User={uname}, to Agency={agency_name}, ")
                    else:
                        print(f"Existed User={uname} to Agency={agency_name}")

def create_agency_settings(db_agencies_by_name):
    from sd_main.models import AgencySetting
    for agency_name, customer_csv_map in CUSTOMER_MAP.items():
        db_agency = db_agencies_by_name[agency_name]
        if not AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.CUSTOMER_CSV_MAP).exists():
            AgencySetting.objects.create(agency=db_agency, name=AgencySetting.CUSTOMER_CSV_MAP, json_value=customer_csv_map)
    
    for agency_name, policy_csv_map in POLICY_MAP.items():
        db_agency = db_agencies_by_name[agency_name]
        if not AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.POLICY_CSV_MAP).exists():
            AgencySetting.objects.create(agency=db_agency, name=AgencySetting.POLICY_CSV_MAP, json_value=policy_csv_map)

    for agency_name, alert_csv_map in ALERT_MAP.items():
        db_agency = db_agencies_by_name[agency_name]
        if not AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.ALER_CSV_MAP).exists():
            AgencySetting.objects.create(agency=db_agency, name=AgencySetting.ALER_CSV_MAP, json_value=alert_csv_map)
    

if __name__ == '__main__':
   new_root = os.path.join(os.path.dirname(__file__), '..')
   print (f"New root: {new_root}")
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
   create_agency_settings(db_agencies)
   print (f"Created Agency Settings")
   create_agency_users()
   print (f"Created Agency Users")

