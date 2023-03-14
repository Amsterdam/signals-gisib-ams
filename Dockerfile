# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11

##################################################
#                   Python                       #
##################################################
FROM python:${PYTHON_VERSION}-slim-buster as app

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=main.settings
ARG DJANGO_SECRET_KEY=insecure_docker_build_key

WORKDIR /app

RUN useradd --no-create-home signals-gisib

COPY requirements.txt /requirements/requirements.txt

RUN set -eux;  \
    apt-get update; \
    apt-get install -y \
      build-essential \
      gdal-bin \
      postgresql-client-11 \
      build-essential \
      libpq-dev \
      gettext \
    ; \
    apt-get purge -y --auto-remove; \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /requirements/requirements.txt

COPY app /app

RUN set -eux; \
    chgrp signals-gisib /app; \
    chmod g+w /app; \
    mkdir -p /app/static /app/media; \
    chown signals-gisib /app/static; \
    chown signals-gisib /app/media

USER signals-gisib

RUN SECRET_KEY=$DJANGO_SECRET_KEY python manage.py collectstatic --no-input

CMD ["gunicorn", "main.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--reload"]

FROM app as dev
USER root
COPY requirements_dev.txt /requirements/requirements.txt
RUN pip install -r /requirements/requirements.txt
USER signals-gisib
