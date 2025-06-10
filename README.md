## Overview
The web application is designed as proof of concept to simplify the routine activities at an insurance agency. For example, renewal reminders, collecting data/images and estabilishing the accuracy of the uploaded data with the help of image scaning and other modern tools.

## Get Started
Quickly get started with local development.

# Environment setup
```
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r ./requirements.txt
```
# SQLite
```
- python3 manage.py flush - truncate tables
```
# SQLite - start fresh - no database changes
```
- rm -f db.sqlite3
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 data/seed_databse.py
- python3 manage.py runserver
```

# SQLite - start fresh - change database schema. Avoid creating new migrations.
```
- rm -f db.sqlite3
- rm sd_main/migrations/0001_initial.py
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 data/seed_databse.py
```
# PostgreSQL - start fresh
- source data/create_database.sh
- rm sd_main/migrations/0001_initial.py
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 data/seed_databse.py
