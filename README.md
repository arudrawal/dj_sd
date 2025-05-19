# dj_sd
Django Share documents

# SQLite
python3 manage.py flush - truncate tables

# SQLite - start fresh
rm -f db.sqlite3
rm sd_main/migrations/0001_initial.py
python3 manage.py makemigrations
python3 manage.py migrate
python3 data/seed_databse.py

# PostgreSQL - start fresh
source data/create_database.sh
rm sd_main/migrations/0001_initial.py
python3 manage.py makemigrations
python3 manage.py migrate
python3 data/seed_databse.py
