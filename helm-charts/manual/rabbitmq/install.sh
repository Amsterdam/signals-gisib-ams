#!/bin/bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm upgrade --install \
    rabbitmq bitnami/rabbitmq \
    --namespace default \
    --create-namespace \
    --values values.yaml \
    --version 11.4.0
