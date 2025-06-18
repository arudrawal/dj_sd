import os
import sys
import django
import json
import yaml
from io import StringIO
from sd_main.aws_utils import download_s3_object

S3_BUCKET_NAME='sdconf'
GMAIL_JSON = 'gmail_api_client_secret.json'
SETTINGS_YAML = 'settings.yaml'
AUTH_CALLBACK_URI = 'gmail_oauth_callback'

SUPER_USER = ''
SUPER_PASS = ''
COMPANY_LIST = ['Farmers', 'State Farm', 'All State']
GROUPS = ['asharma_group', 'bobs_group', 'chucks_group']
AGENCIES = [{'name': 'Archana Agency', 'company': COMPANY_LIST[0]},
            {'name': 'Bobs Agency', 'company': COMPANY_LIST[1]},
            {'name': 'Chucks Agency', 'company': COMPANY_LIST[2]},
        ]
#    Raw Agency_map: Policy,Name,Billing Account,Policy Start Date,Policy End Date,LOB,Status,Phone Number,Email,Alert Classification,Due Date,Created Date,Alert Category,Alert Sub-Category
#  Apply conversion: Convert all to lower and replace space by '_'
# Xlated Agency_map: policy,name,billing_account,policy_start_date,policy_end_date,lob,status,phone_number,email,alert_classification,due_date,created_date,alert_category,alert_sub-category
# database_map: number,name,company_account,start_date,end_date,lob,work_status,phone,email,alert_level,due_date,date_created,alert_category,alert_sub_category
farmers_customer_map = {
        str.lower('Name'): 'name', 
        str.lower('Billing Account').replace(' ', '_' ): 'company_account', 
        str.lower('Email'): 'email', 
        str.lower('Phone Number').replace(' ', '_'): 'phone', 
        str.lower('DOB'): 'dob',
    }
CUSTOMER_MAP = {
    AGENCIES[0]['name']: farmers_customer_map,
    AGENCIES[1]['name']: farmers_customer_map,
    AGENCIES[2]['name']: farmers_customer_map,
}
farmers_policy_map = {
        str.lower('Policy'): 'number', 
        str.lower('LOB'): 'lob', 
        str.lower('Policy Start Date').replace(' ', '_'): 'start_date',
        str.lower('Policy End Date').replace(' ', '_'): 'end_date',
        str.lower('Premium').replace(' ', '_'): 'premium_amount',
    }
POLICY_MAP = {
    AGENCIES[0]['name']: farmers_policy_map,
    AGENCIES[1]['name']: farmers_policy_map,
    AGENCIES[2]['name']: farmers_policy_map,
}
farmers_alert_map = {
    str.lower('Alert Classification').replace(' ', '_'): 'alert_level', 
    str.lower('Due Date').replace(' ', '_'): 'due_date',
    str.lower('Created Date').replace(' ', '_'): 'created_date', 
    str.lower('Status'): 'work_status',
    str.lower('Alert Category').replace(' ', '_'): 'alert_category', 
    str.lower('Alert Sub-Category').replace(' ', '_'): 'alert_sub_category',
}
ALERT_MAP = {
    AGENCIES[0]['name']: farmers_alert_map,
    AGENCIES[1]['name']: farmers_alert_map,
    AGENCIES[2]['name']: farmers_alert_map,
}

DOMAIN_EMAIL = 'shivark.com'
AJAY_EMAIL = f'ajay@{DOMAIN_EMAIL}'
MUKESH_EMAIL = f'mukesh@{DOMAIN_EMAIL}'
ARCHANA_EMAIL = f'archana@{DOMAIN_EMAIL}'
USERS = [{'user_name':'ajay', 'email': AJAY_EMAIL, 'groups': [GROUPS[0], GROUPS[1]]},
         {'user_name':'mukesh', 'email': MUKESH_EMAIL, 'groups': [GROUPS[0]]},
         {'user_name':'archana', 'email': ARCHANA_EMAIL, 'groups': [GROUPS[0]]},
        ]
AGENCY_USERS = {
    AGENCIES[0]['name']: ['ajay', 'mukesh', 'archana'],
    AGENCIES[1]['name']: ['ajay'],
    AGENCIES[2]['name']: ['ajay'],
}

EMAIL_TEMPLATE = {
    'name': 'Basic Renewal Reminder',
    'subject_line': 'Reminder: Your Insurance Policy is Due for Renewal',
    'body': "Dear {{customer_name}} \n"
            "We hope this message finds you well. This is a friendly reminder that your insurance policy with {{insurance_company_name}}, policy number {{policy_number}}, is set to expire on {{expiration_date}}.\n\n"
            "To ensure continued coverage without interruption, we recommend renewing your policy before the expiration date. Renewing now will give you peace of mind and avoid any potential gaps in coverage.\n\n"
            "Policy Details:\n"
            "Policy Type: {{policy_type}}\n"
            "Renewal Due Date: {{expiration_date}}\n"
            "Premium Amount: {{premium_amount}}\n"
            "Renew Now: {{renewal_link}}\n\n"
            "If you have any questions about your coverage, or if you’d like to make changes to your policy before renewal, please don’t hesitate to reach out. You can contact us at {{contact_phone_number}} or {{contact_email_address}}.\n\n"
            "Thank you for choosing {{insurance_company_name}}. We appreciate your continued trust."
            "Warm regards,\n"
            "{{agent_full_name}}\n"
            "{{agent_title}}\n"
            "{{insurance_company_name}}\n"
            "{{contact_information}}"
}

def init_super_user():
    data = None
    app_runner_url = os.environ.get("AWS_APP_RUNNER_DEFAULT_DOMAIN")
    if app_runner_url:
        yaml_string = download_s3_object(S3_BUCKET_NAME, SETTINGS_YAML)
        data = yaml.safe_load(StringIO(yaml_string))
        print(f"YAML data loaded successfully [s3]: {S3_BUCKET_NAME}/{SETTINGS_YAML}")
    else:
        yaml_file_path = f"secrets/{SETTINGS_YAML}"
        try:
            with open(yaml_file_path, 'r') as file:
                data = yaml.safe_load(file)
                print(f"YAML data loaded successfully: {yaml_file_path}")
        except FileNotFoundError:
            print(f"Error: The file '{yaml_file_path}' was not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
    if data:
        return data['djadmin']['user'], data['djadmin']['password']
    return 'admin', 'password'

def get_mail_client_credentials():
    client_id_data = callback_url = None
    gmail_client_path = f"secrets/{GMAIL_JSON}"
    app_runner_url = os.environ.get("AWS_APP_RUNNER_DEFAULT_DOMAIN")
    if app_runner_url: # App runner
        callback_url=f'{app_runner_url}/{AUTH_CALLBACK_URI}/'
        json_content = download_s3_object(S3_BUCKET_NAME, GMAIL_JSON)
        if json_content:
            client_id_data = json.loads(json_content)
    elif os.path.exists(gmail_client_path):
        callback_url = f'http://localhost:8000/{AUTH_CALLBACK_URI}/'
        with open(gmail_client_path, "r") as client_id_file:
            client_id_data = json.load(client_id_file)
    return client_id_data, callback_url


def create_admin_user(super_user, super_pass):
    from django.contrib.auth.models import User
    # Admin user
    db_admin = User.objects.filter(username=super_user).first()
    if not db_admin:
        db_admin = User.objects.create_superuser(username=super_user, email=AJAY_EMAIL, password=super_pass)
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

def create_other_users(user_list: list, db_groups: dict, super_pass):
    from django.contrib.auth.models import User
    db_users = {}
    for user in user_list:
        db_user = User.objects.filter(username=user['user_name']).first()
        if not db_user: # User.objects.filter(username=user['user_name']).exists():
            db_user = User.objects.create_user(user['user_name'], user['email'], super_pass)
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
    
    AGENCY_OAUTH_SETTINGS = {
        AGENCIES[0]['name']: {AgencySetting.AGENCY_OAUTH_PROVIDER: 'google', AgencySetting.AGENCY_OAUTH_EMAIL: 'archana@shivark.com'},
        AGENCIES[1]['name']: {AgencySetting.AGENCY_OAUTH_PROVIDER: 'google', AgencySetting.AGENCY_OAUTH_EMAIL: 'mukesh@shivark.com'},
        AGENCIES[2]['name']: {AgencySetting.AGENCY_OAUTH_PROVIDER: 'google', AgencySetting.AGENCY_OAUTH_EMAIL: 'ajay@shivark.com'},
    }
    
    for agency_name, agency_setting in AGENCY_OAUTH_SETTINGS.items():
        db_agency = db_agencies_by_name[agency_name]
        if not AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.AGENCY_OAUTH_PROVIDER).exists():
            AgencySetting.objects.create(agency=db_agency, name=AgencySetting.AGENCY_OAUTH_PROVIDER, text_value=agency_setting[AgencySetting.AGENCY_OAUTH_PROVIDER])
        if not AgencySetting.objects.filter(agency=db_agency, name=AgencySetting.AGENCY_OAUTH_EMAIL).exists():
            AgencySetting.objects.create(agency=db_agency, name=AgencySetting.AGENCY_OAUTH_EMAIL, text_value=agency_setting[AgencySetting.AGENCY_OAUTH_EMAIL])

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

def create_agency_email_template():
    from sd_main.models import Agency, EmailTemplate
    for agency_name in AGENCY_USERS.keys():
        db_agency = Agency.objects.filter(name=agency_name).first()
        if db_agency:
            db_email_template = EmailTemplate(
                agency=db_agency,
                name=EMAIL_TEMPLATE['name'],
                subject_line=EMAIL_TEMPLATE['subject_line'],
                body=EMAIL_TEMPLATE['body']
            )
            db_email_template.save()
            print(f"Saved Email Template to Agency= {agency_name}")

def load_system_settings():
    from sd_main.models import SystemSetting
    ret_val = False
    client_id_data, callback_url = get_mail_client_credentials()
    db_gmail_client = SystemSetting.objects.filter(name=SystemSetting.GMAIL_CLIENT_ID).first()
    if not db_gmail_client:
        db_gmail_client = SystemSetting.objects.create(name=SystemSetting.GMAIL_CLIENT_ID, json_value=client_id_data)
        ret_val = True
    db_gmail_redirect_url = SystemSetting.objects.filter(name=SystemSetting.GMAIL_REDIRECT_URL).first()
    if not db_gmail_redirect_url:
        db_gmail_redirect_url = SystemSetting.objects.create(name=SystemSetting.GMAIL_REDIRECT_URL, text_value=callback_url)
        ret_val = True
    return ret_val

if __name__ == '__main__':
    # new_root = os.path.join(os.path.dirname(__file__), '..')
    # print (f"New root: {new_root}")
    # sys.path.append(new_root)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sd_proj.settings'
    django.setup()
    super_user, super_pass = init_super_user()
    create_admin_user(super_user, super_pass)

    db_groups = create_groups(GROUPS)
    print (f"Created Groups: {db_groups.keys()}")
    db_users = create_other_users(USERS, db_groups, super_pass)
    print (f"Created Users: {db_users.keys()}")
    db_companies = create_company()
    print (f"Created Companies: {db_companies.keys()}")
    db_agencies = create_agencies(AGENCIES, db_companies, db_groups)
    print (f"Created Agencies: {db_agencies.keys()}")
    create_agency_settings(db_agencies)
    print (f"Created Agency Settings")
    create_agency_users()
    print (f"Created Agency Users")
    create_agency_email_template()
    print(f"Created Agency Email Templates")
    if load_system_settings():
        print (f"Added System Settings Gmail OAUTH client/Redirect URL")

