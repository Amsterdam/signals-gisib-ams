# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13-slim-bookworm

##################################################
#                   Python                       #
##################################################
FROM python:${PYTHON_VERSION} AS app

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=main.settings
ARG DJANGO_SECRET_KEY=insecure_docker_build_key

WORKDIR /app

RUN useradd --no-create-home signals-gisib

COPY ./app/requirements /app/requirements

RUN set -eux;  \
    apt-get update; \
    apt-get install -y \
      build-essential \
      gdal-bin \
      build-essential \
      libpq-dev \
      gettext \
    ; \
    apt-get purge -y --auto-remove; \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /app/requirements/requirements.txt

COPY app /app

RUN set -eux; \
    chgrp signals-gisib /app; \
    chmod g+w /app; \
    mkdir -p /app/static /app/media; \
    chown -R signals-gisib /app/static; \
    chown signals-gisib /app/media

RUN ls -lah /app

USER signals-gisib

RUN SECRET_KEY=$DJANGO_SECRET_KEY python manage.py collectstatic --no-input

CMD ["gunicorn", "main.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--reload", "-w", "2", "--threads", "4"]

FROM app AS dev
USER root
RUN pip install -r /app/requirements/requirements_dev.txt
USER signals-gisib
