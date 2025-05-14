#!/bin/sh

# Truncate tables
PGPASSWORD=test psql --host localhost --username=test -d local_sd << EOF
truncate sd_main_policyalert, sd_main_driver, sd_main_vehicle, sd_main_policydocument,sd_main_policy, sd_main_customer;
EOF
