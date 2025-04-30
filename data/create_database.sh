#!/bin/sh

# drop and create local sd db
PGPASSWORD=test psql --host localhost --username=test -t -c 'drop database local_sd'
PGPASSWORD=test psql --host localhost --username=test -t -c 'create database local_sd'
PGPASSWORD=test psql --host localhost --username=test -t -c 'GRANT ALL PRIVILEGES ON DATABASE local_sd TO test;'

