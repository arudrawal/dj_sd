## Overview
The web application is designed as proof of concept to simplify the routine activities at an insurance agency. For example, renewal reminders, collecting data/images and estabilishing the accuracy of the uploaded data with the help of image scaning and other modern tools.

## Get Started
Quickly get started with local development.

### Environment setup
```
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r ./requirements.txt
```
### SQLite
```
- python3 manage.py flush - truncate tables
```
### SQLite - start fresh - no database changes
```
- rm -f db.sqlite3
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 data/seed_databse.py
- python3 manage.py runserver
```

### SQLite - start fresh - change database schema. Avoid creating new migrations.
```
- rm -f db.sqlite3
- rm sd_main/migrations/0001_initial.py
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 data/seed_databse.py
```
### PostgreSQL - start fresh
#### Assuming PostgresSql is installed on the system
- source data/create_database.sh
- rm sd_main/migrations/0001_initial.py
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 data/seed_databse.py

### Run Dockerized application with Postgres
    Assuming PostgresSql is installed on the system
- source data/create_database.sh # create empty database
- docker compose up --build      # Build docker image
- docker compose run web python3 manage.py migrate # Create database
- docker compose run web python3 data/seed_databse.py # Seed test data

### Push docker image to AWS
- docker compose up --build
- docker tag dj_sd-web:latest 198752717356.dkr.ecr.us-west-2.amazonaws.com/shivark/dj_sd:latest
- aws ecr get-login-password --region us-west-2 --profile shivark | docker login --username AWS
--password-stdin 198752717356.dkr.ecr.us-west-2.amazonaws.com
- docker push 198752717356.dkr.ecr.us-west-2.amazonaws.com/shivark/dj_sd:latest
