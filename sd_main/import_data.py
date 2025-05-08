import pandas as pd
from io import StringIO
from datetime import datetime
from .models import Policy
from django.contrib.auth.models import Group
from .models import Customer, AgencySetting, Policy
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

def convert_to_ymd(dt: datetime) -> str:
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
    except:
        df = pd.DataFrame()
    return df

def extract_customers(user_group:Group, df_input: pd.DataFrame):
    customer_ag2db_map = AgencySetting.objects.filter(group=user_group, name=AgencySetting.CUSTOMER_CSV_MAP).first()
    customer_ag2db_map
    pass

def extract_policies(group:str, df_critical_alerts: pd.DataFrame):
    pass

def extract_alerts(group:str, df_critical_alerts: pd.DataFrame):
    pass

def get_existing_policies(group_name: str):
    """ Vendor specific unique hash (policy_number+end_date) """
    policies_by_hash = {}
    all_policies = Policy.objects.filter(group=group_name)
    for existing_policy_row in all_policies:
        hash_key = f"{str(existing_policy_row.policy_number)}:{convert_to_ymd(existing_policy_row.end_date)}"
        policies_by_hash[hash_key] = existing_policy_row
    return policies_by_hash

def add_policy(df_policy: pd.DataFrame, group_object):
    db_columns = ["policy_number", "policy_owner", "start_date", "end_date","owner_phone", "owner_email", "policy_type"]
    df_db_policy = df_policy[db_columns]
    policy_model_instances = [Policy(policy_number=row['policy_number'], policy_owner=row['policy_owner'],
                                     start_date=row['start_date'], end_date=row['end_date'],
                                     owner_phone = row['owner_phone'], owner_email = row['owner_email'],
                                     policy_type = row['policy_type'], group = group_object) for _,row in df_db_policy.iterrows()]
    Policy.objects.bulk_create(policy_model_instances)
    return len(policy_model_instances)

def update_policy(df_policy: pd.DataFrame, group_object: Group):
    return len(df_policy.index)

def import_policy(df_policy: pd.DataFrame, group_name: str):
    group_object = Group.objects.filter(name=group_name).first()
    policies_by_hash = get_existing_policies(group_name)
    existing_hash_ids = policies_by_hash.keys()
    df_policy['dt_start_date'] = df_policy['start_date'].apply(lambda sdval: convert_to_date(sdval))
    df_policy['dt_end_date'] = df_policy['end_date'].apply(lambda edval: convert_to_date(edval))
    df_policy['start_date'] = df_policy['dt_start_date'].apply(lambda sdt: convert_to_ymd(sdt)) 
    df_policy['end_date'] = df_policy['dt_end_date'].apply(lambda edt: convert_to_ymd(edt))
    add_count = update_count = 0
    if not df_policy.empty and group_object:
        df_policy["hash_key"] = df_policy.apply(lambda row: str(row["policy_number"]) + ":" + str(row["end_date"]), axis=1)
        df_policy_add = df_policy  # assume all to add
        df_policy_update = pd.DataFrame()  # assume none to update
        if len(existing_hash_ids) > 0:
            df_policy_add = df_policy.loc[~df_policy['hash_key'].isin(existing_hash_ids)]
            df_policy_update = df_policy.loc[df_policy['hash_key'].isin(existing_hash_ids)]
        add_count = len(df_policy_add.index)
        update_count = len(df_policy_update.index)
        print(f"service_calendar: adding={len(df_policy_add.index)}, updating={len(df_policy_update.index)}")
        if not df_policy_add.empty:
            add_policy(df_policy_add, group_object)
        if not df_policy_update.empty:
            update_policy(df_policy_update, group_object)
    return add_count, update_count
