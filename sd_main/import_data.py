import pandas as pd
from io import StringIO
from datetime import datetime
from .models import Policy
from django.contrib.auth.models import Group
from .models import Agency, Customer, AgencySetting, Policy
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import connection
from django.conf import settings
from dateutil import parser as date_parser

def get_engine():
    # create_engine is a function from SQLAlchemy, not psycopg2 directly
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']
    host = settings.DATABASES['default']['HOST']
    port = settings.DATABASES['default']['PORT']
    database_url = f'postgresql://{user}:{password}@{host}:{port}/{database_name}'
    return create_engine(database_url, echo=False)

def convert_ymd_to_date(val: str) -> datetime:
    return datetime.strptime(str(val), "%Y-%m-%d")

def convert_to_date(val: str) -> datetime:
    return date_parser.parse(val)

def convert_to_db_ymd(dt: datetime) -> str:
    return datetime.strftime(dt, "%Y-%m-%d")

""" Get all CSV columns as dictionary of type str unless given in non_str: {'col3': bool, 'col4': float}.
    return {'col1': str, 'col2': str, 'col3': bool, 'col4': float}
"""
def get_csv_data_type(dot_txt_file, non_str: dict = {}):
    csv_cols = pd.read_csv(dot_txt_file, nrows=1).columns
    dtype_dict = {}
    for column in csv_cols:
        if column in non_str.keys():
            dtype_dict[column] = non_str[column]
        else:
            dtype_dict[column] = str
    return dtype_dict

""" Read CSV file, non_str: dictionary non string type columns. """
def read_file_csv(file, data_type:dict={}) -> pd.DataFrame:
    try:
        return pd.read_csv(file, sep=',', engine="c", dtype=data_type)
    except BaseException as e:
        print(e)
        return pd.DataFrame()

def convert_to_dataframe(file: InMemoryUploadedFile) -> pd.DataFrame:
    """
    Reads the content of an uploaded file into a Pandas DataFrame.

    Args:
        file: An InMemoryUploadedFile object representing the uploaded file.

    Returns:
        A Pandas DataFrame containing the data from the file.
    """
    try:
        file_content = file.read().decode('utf-8')
        data1 = StringIO(file_content)
        data_type = get_csv_data_type(data1)
        data = StringIO(file_content)
        df = read_file_csv(data, data_type)
        df.columns = df.columns.str.lower() # all column names to lowercase
        df.columns = df.columns.str.replace(' ', '_') # replace space with '_'
    except:
        df = pd.DataFrame()
    return df

def extract_by_csv_map(df_input: pd.DataFrame, ag2db_map: dict):
    df_output = pd.DataFrame()
    for ag_col,db_col in ag2db_map.items():
        if ag_col in df_input.columns:  # do the column name conversion
            df_output[db_col] = df_input[ag_col]
        elif db_col in df_input.columns: # accept the converted columns as is
            df_output[db_col] = df_input[db_col]
    return df_output

def get_existing_customers(db_agency: Agency):
    """ Agency specific unique customer hash (customer.name) """
    customers_by_hash = {}
    all_customers = Customer.objects.filter(agency=db_agency).all()
    for existing_customer_row in all_customers:
        hash_key = f"{str(existing_customer_row.name)}"
        customers_by_hash[hash_key] = existing_customer_row
    return customers_by_hash

def add_customer(df_customer: pd.DataFrame, db_agency: Agency):
    customer_models = []
    for _,row in df_customer.iterrows():
        db_customer = Customer(name=row['name'], agency=db_agency) # must have name
        if 'company_account' in df_customer.columns:
            db_customer.company_account = row['company_account']
        if 'email' in df_customer.columns:
            db_customer.email = row['email']
        if 'phone' in df_customer.columns:
            db_customer.email = row['phone']
        if 'dob' in df_customer.columns:
            db_customer.dob = row['dob']
        customer_models.append(db_customer)
    Customer.objects.bulk_create(customer_models)
    return len(customer_models)

def update_customer(df_customer: pd.DataFrame, db_customer_by_hash: dict):
    customer_models = []
    customer_columns = []
    for _,row in df_customer.iterrows():
        if row['hash_key'] in db_customer_by_hash.keys():
            updated = False
            db_customer =  db_customer_by_hash[row['hash_key']]
            if 'company_account' in df_customer.columns:
                if db_customer.company_account != row['company_account']:
                    if 'company_account' not in customer_columns:
                        customer_columns.append('company_account')
                    db_customer.company_account == row['company_account']
                    updated = True
            if 'email' in df_customer.columns:
                if db_customer.email != row['email']:
                    db_customer.email = row['email']
                    if 'email' not in customer_columns:
                        customer_columns.append('email')
                    updated = True
            if 'phone' in df_customer.columns:
                if db_customer.email != row['phone']:
                    db_customer.email = row['phone']
                    if 'phone' not in customer_columns:
                        customer_columns.append('phone')
                    updated = True
            if 'dob' in df_customer.columns:
                if db_customer.dob != row['dob']:
                    db_customer.dob = row['dob']
                    if 'dob' not in customer_columns:
                        customer_columns.append('dob')
                    updated = True
            if updated:
                customer_models.append(db_customer)
    # Perform the bulk update
    if len(customer_models):
        Customer.objects.bulk_update(customer_models, customer_columns)
    return len(customer_models)

def import_customer(df_customer: pd.DataFrame, db_agency: Agency):
    # group_object = Group.objects.filter(name=group_name).first()
    customer_by_hash = get_existing_customers(db_agency)
    existing_hash_ids = customer_by_hash.keys()
    # Special treatment for Date column: parse input date then convert to ORM freidly format.
    if 'dob' in df_customer.columns:
        df_customer['dt_dob'] = df_customer['dob'].apply(lambda dobval: convert_to_date(dobval))
        df_customer['dob'] = df_customer['dob'].apply(lambda sdt: convert_to_db_ymd(sdt))
    add_count = update_count = 0
    if not df_customer.empty and db_agency:
        df_customer["hash_key"] = df_customer.apply(lambda row: str(row["name"]), axis=1)
        df_customer_add = df_customer  # assume all to add
        df_customer_update = pd.DataFrame()  # assume none to update
        if len(existing_hash_ids) > 0:
            df_customer_add = df_customer.loc[~df_customer['hash_key'].isin(existing_hash_ids)]
            df_customer_update = df_customer.loc[df_customer['hash_key'].isin(existing_hash_ids)]
        add_count = len(df_customer_add.index)
        update_count = len(df_customer_update.index)
        if not df_customer_add.empty:
            add_customer(df_customer_add, db_agency)
        if not df_customer_update.empty:
            update_customer(df_customer_update, customer_by_hash)
    print(f"customer: adding={add_count}, updating={update_count}")
    return add_count, update_count

def get_existing_policies(db_agency: Agency):
    """ Agency specific unique hash (policy_number+end_date) """
    policies_by_hash = {}
    all_policies = Policy.objects.filter(agency=db_agency).all()
    for existing_policy_row in all_policies:
        hash_key = f"{str(existing_policy_row.policy_number)}:{convert_to_db_ymd(existing_policy_row.end_date)}"
        policies_by_hash[hash_key] = existing_policy_row
    return policies_by_hash

def add_policy(df_policy: pd.DataFrame, db_agency: Agency):
    policy_instances = []
    for _,row in df_policy.iterrows():
        db_policy = Policy(policy_number=row['policy_number'], policy_owner=row['policy_owner'], agency=db_agency, policy_type = row['policy_type'])
        if 'start_date' in df_policy.columns:
            db_policy.start_date = row['start_date']
        if 'end_date' in df_policy.columns:
            db_policy.end_date = row['end_date']
        if 'owner_phone' in df_policy.columns:
            db_policy.owner_phone = row['owner_phone']
        if 'owner_email' in df_policy.columns:
            db_policy.owner_email = row['owner_email']
        policy_instances.append(db_policy)
    Policy.objects.bulk_create(policy_instances)
    return len(policy_instances)

def update_policy(df_policy: pd.DataFrame, db_policies_by_hash: dict):
    policy_instances = []
    policy_columns = []
    for _,row in df_policy.iterrows():
        if row['hash_key'] in db_policies_by_hash.keys():
            update = False
            db_policy = db_policies_by_hash['hash_key']
            if 'start_date' in df_policy.columns:
                if db_policy.start_date != row['start_date']:
                    db_policy.start_date = row['start_date']
                    if 'start_date' not in policy_columns:
                        policy_columns.append('start_date')
                    update = True
                if 'end_date' in df_policy.columns:
                    if db_policy.end_date != row['end_date']:
                        db_policy.end_date = row['end_date']
                        if 'end_date' not in policy_columns:
                            policy_columns.append('end_date')
                        update = True
                if 'owner_phone' in df_policy.columns:
                    if db_policy.owner_phone != row['owner_phone']:
                        db_policy.owner_phone = row['owner_phone']
                        if 'owner_phone' not in policy_columns:
                            policy_columns.append('owner_phone')
                        update = True
                if 'owner_email' in df_policy.columns:
                    if db_policy.owner_email != row['owner_email']:
                        db_policy.owner_email = row['owner_email']
                        if 'owner_email' not in policy_columns:
                            policy_columns.append('owner_email')
                        update = True
            if update:
                policy_instances.append(db_policy)
    if len(policy_instances):
        Policy.objects.bulk_update(policy_instances, policy_columns)
    return len(policy_instances)


def import_policy(df_policy: pd.DataFrame, db_agency: Agency):
    # group_object = Group.objects.filter(name=group_name).first()
    policies_by_hash = get_existing_policies(db_agency)
    existing_hash_ids = policies_by_hash.keys()
    df_policy['dt_start_date'] = df_policy['start_date'].apply(lambda sdval: convert_to_date(sdval))
    df_policy['dt_end_date'] = df_policy['end_date'].apply(lambda edval: convert_to_date(edval))
    df_policy['start_date'] = df_policy['dt_start_date'].apply(lambda sdt: convert_to_db_ymd(sdt)) 
    df_policy['end_date'] = df_policy['dt_end_date'].apply(lambda edt: convert_to_db_ymd(edt))
    add_count = update_count = 0
    if not df_policy.empty and db_agency:
        df_policy["hash_key"] = df_policy.apply(lambda row: str(row["policy_number"]) + ":" + str(row["end_date"]), axis=1)
        df_policy_add = df_policy  # assume all to add
        df_policy_update = pd.DataFrame()  # assume none to update
        if len(existing_hash_ids) > 0:
            df_policy_add = df_policy.loc[~df_policy['hash_key'].isin(existing_hash_ids)]
            df_policy_update = df_policy.loc[df_policy['hash_key'].isin(existing_hash_ids)]
        add_count = len(df_policy_add.index)
        update_count = len(df_policy_update.index)
        if not df_policy_add.empty:
            add_policy(df_policy_add, db_agency)
        if not df_policy_update.empty:
            update_policy(df_policy_update, db_agency)
    print(f"Policies: adding={add_count}, updating={update_count}")
    return add_count, update_count

def import_alert(df_alert: pd.DataFrame, db_agency: Agency):
    pass