#!/bin/bash

# Apply database migrations
echo "Make database migrations"
python manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

celery -A os_locator_etl worker -l INFO --detach
python manage.py runserver 0.0.0.0:80
