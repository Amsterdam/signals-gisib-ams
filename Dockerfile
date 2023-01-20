FROM python:3.11-slim-buster as app

# Create a new user/group called signals-gisib
RUN groupadd -r signals-gisib && useradd --no-log-init -r -g signals-gisib signals-gisib

RUN mkdir -p /media && mkdir -p /static && chown signals-gisib /media && chown signals-gisib /static

# Add package dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    postgresql-client-11 \
    build-essential \
    libpq-dev \
    gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements
COPY requirements.txt /requirements.txt

# Install the requirements
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the app folder
COPY src/ /app/

# Change ownership of the src folder to signals-gisib user/group
RUN chown -R signals-gisib:signals-gisib /app/

# Switch to the signals-gisib user
USER signals-gisib

# Move to the app folder
WORKDIR /app/

# Collect static files
RUN SECRET_KEY=$DJANGO_SECRET_KEY python manage.py collectstatic --no-input

FROM app as dev
USER root
ADD requirements_dev.txt /requirements_dev.txt
RUN pip install -r /requirements_dev.txt
