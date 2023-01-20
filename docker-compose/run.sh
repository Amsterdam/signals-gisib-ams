#!/bin/bash

# Apply migrations
python manage.py migrate --noinput

# Create the super user if it does not exists
echo "Creating the super user if it does not already exists"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='signals.gisib.ams').exists() or User.objects.create_superuser('signals.gisib.ams', 'signals.gisib.ams@example.com', 'insecure')" | python manage.py shell

# Collect static
python manage.py collectstatic --no-input

# Start Gunicorn to run the ASGI application defined in main.asgi using 1 worker process and bind it to all available network interfaces on port 8000.
python -m gunicorn main.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --reload
