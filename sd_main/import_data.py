import pandas as pd
from datetime import datetime
from .models import Policy

def convert_ymd_to_date(val: str) -> datetime:
    return datetime.strptime(str(val), "%Y%m%d")

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
def read_file_csv(file: str, non_str:dict={}) -> pd.DataFrame:
    try:
        data_type = get_csv_data_type(file, non_str=non_str)
        return pd.read_csv(file, sep=',', engine="c", dtype=data_type)
    except BaseException as e:
        print(e)
        return pd.DataFrame()
    
def get_existing_policies():
    """ Vendor specific unique hash (policy_id+end_date) """
    policy_by_hash = {}
    pol_dates = Policy.objects.all()
    
    for existing_cal_row in scal_dates:
        hash_key = str(existing_cal_row.service_id) + ':' + existing_cal_row.date.strftime("%Y%m%d")
        calendar_dates_by_service_date[hash_key] = existing_cal_row
    return calendar_dates_by_service_date

def import_policy(df_policy: pd.DataFrame):
    policy_by_id_end_date = get_existing_calendar()
    existing_service_ids = calendar_by_service_id.keys()
    if not df_calendar.empty:
        df_calendar_add = df_calendar  # assume all to add
        df_calendar_update = pd.DataFrame()  # assume none to update
        if len(existing_service_ids) > 0:
            df_calendar_add = df_calendar.loc[~df_calendar['service_id'].isin(existing_service_ids)]
            df_calendar_update = df_calendar.loc[df_calendar['service_id'].isin(existing_service_ids)]
        print(f"service_calendar: adding={len(df_calendar_add.index)}, updating={len(df_calendar_update.index)}")
        if not df_calendar_add.empty:
            self.add_calendar(df_calendar_add)
        if not df_calendar_update.empty:
            self.update_calendar(df_calendar_update, calendar_by_service_id)
    # calendar_by_service_id, calendar_by_row_id = self.get_existing_calendar()    
