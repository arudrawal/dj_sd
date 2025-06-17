GMAIL_SCOPES = [# 'https://www.googleapis.com/auth/drive.metadata.readonly',
                # 'https://www.googleapis.com/auth/calendar.readonly'
                "https://www.googleapis.com/auth/gmail.send"
                ]

# DF_HASH_KEY = "hash_key"
DF_CUSTOMER_HASH_KEY = "customer_hash_key"
DF_POLICY_HASH_KEY = "policy_hash_key"
DF_POLICY_ALERT_HASH_KEY = "policy_alert_hash_key"

# table: sd_main_customer
CUSTOMER_NAME_COLUMN = "name"
CUSTOMER_COMPANY_ACCOUNT = "company_account"
CUSTOMER_PHONE_COLUMN = "phone"
CUSTOMER_EMAIL_COLUMN = "email"
CUSTOMER_DOB_COLUMN = "dob"

# table: sd_main_policy
POLICY_NUMBER_COLUMN = "number"
POLICY_START_DATE_COLUMN = "start_date"
POLICY_END_DATE_COLUMN = "end_date"
POLICY_PREMIUM_COLUMN = "premium_amount"
POLICY_LOB_COLUMN = "lob"

# table: sd_main_policy_alert
POLICY_ALERT_LEVEL_COLUMN = "alert_level"
POLICY_ALERT_DUE_DATE_COLUMN = "due_date"
POLICY_ALERT_CREATED_DATE_COLUMN = "created_date"
POLICY_ALERT_WORK_STATUS_COLUMN = "work_status"
POLICY_ALERT_CATEGORY_COLUMN = "alert_category"
POLICY_ALERT_SUB_CATEGORY_COLUMN = "alert_sub_category"
POLICY_ALERT_IS_ACTIVE_COLUMN = "is_active"

DOC_MERGE_KEYWORDS = {
    "customer_name": "Customer Name",
    "insurance_company_name": "Insurance Company Name",
    "policy_type": "Poilicy Type [Auto/Home/Life/Umbrella]",
    "policy_number": "Policy Number",
    "expiration_date" : "Expiration Date",
    "premium_amount": "Premium Amount",
    "renewal_link": "Renewal Link",
    "agent_full_name": "Agent Fullname",
    "agent_title": "Agent Title",
    "contact_information": "Contact Information",
}
