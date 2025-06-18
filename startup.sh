#!/bin/bash
export PYTHONPATH=$PYTHONPATH
python manage.py migrate
python seed_database.py
python manage.py collectstatic 
# gunicorn --bind 0.0.0.0:8000 --workers 2 sd_proj.wsgi:application
