#!/bin/sh

# Truncate tables
PGPASSWORD=test psql --host localhost --username=test -d local_sd << EOF
truncate sd_main_agencysetting;
EOF
