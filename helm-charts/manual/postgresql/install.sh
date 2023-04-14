#!/bin/bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm upgrade --install \
    postgresql bitnami/postgresql \
    --namespace default \
    --create-namespace \
    --values values.yaml \
    --version 12.1.0
