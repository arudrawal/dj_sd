#!/bin/sh

# drop and create local sd db
PGPASSWORD=test psql --host localhost --username=test -t -c 'drop database local_sd'
PGPASSWORD=test psql --host localhost --username=test -t -c 'create database local_sd'
PGPASSWORD=test psql --host localhost --username=test -t -c 'GRANT ALL PRIVILEGES ON DATABASE local_sd TO test;'

# DJ_DATA=`pwd`
# cd ..
# DJ_ROOT=`pwd`
# rm -f $DJ_ROOT/sd_main/migrations/001*
# python3 manager.py makemigrations
# python3 manager.py migrate
# python3 $DJ_DATA/seed_databse.py
# cd $DJ_DATA
