#!/bin/bash
export PYTHONPATH=$PYTHONPATH
# python3 manage.py migrate && python3 data/seed_database.py
python3 manage.py collectstatic && gunicorn --bind 0.0.0.0:8000 --workers 2 sd_proj.wsgi
