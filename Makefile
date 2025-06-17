# Oneshell means I can run multiple lines in a recipe in the same shell, so I don't have to
# chain commands together with semicolon
.ONESHELL:

# Set shell
SHELL=/usr/bin/bash

VERSION_FILE="./sd_main/version.py"
BUILD_DAY=`date +%Y-%m-%d`
BUILD_TIME=`date +%H:%M`
BUILD_HOST=`hostname`

### commands, no file dependencies ###
.PHONY: version

all: version
	docker image rm --force 198752717356.dkr.ecr.us-west-2.amazonaws.com/shivark/dj_sd:latest
	docker build -t 198752717356.dkr.ecr.us-west-2.amazonaws.com/shivark/dj_sd:latest .

version:
	truncate -s 0 ${VERSION_FILE}
	echo "VERSION='v0.1'" >> ${VERSION_FILE}
	echo "BUILD_DAY='${BUILD_DAY}'" >> ${VERSION_FILE}
	echo "BUILD_TIME='${BUILD_TIME}'" >> ${VERSION_FILE}
	echo "BUILD_HOST='${BUILD_HOST}'" >> ${VERSION_FILE}
	cat ${VERSION_FILE}

push:
	aws ecr get-login-password --region us-west-2 --profile shivark | docker login --username AWS --password-stdin 198752717356.dkr.ecr.us-west-2.amazonaws.com
	docker push 198752717356.dkr.ecr.us-west-2.amazonaws.com/shivark/dj_sd:latest

flush_mig:
	rm -f db.sqlite3
	rm -f sd_main/migrations/0001_initial*.py
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 data/seed_database.py


