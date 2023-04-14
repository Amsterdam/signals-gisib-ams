# How to run signals-gisib-ams app in Kubernetes using Helm
This README provides instructions on how to deploy the `signals-gisib-ams`
application in Kubernetes using Helm. Before deploying the application, we need
to deploy two dependencies: PostgreSQL and RabbitMQ.

However, note that deployment of these components is **optional** if you already
have other solutions like an Azure database for PostgreSQL or another instance
of RabbitMQ that you wish to use.

## Prerequisites
Before you begin, ensure that you have the following prerequisites:

- Kubernetes cluster is installed and configured
- Helm is installed

## Deploying PostgreSQL and RabbitMQ (optional)
To deploy PostgreSQL and RabbitMQ, we will use the bash scripts located in the
[helm-charts/manual/postgresql](./manual/postgresql) and
[helm-charts/manual/rabbitmq](./manual/rabbitmq) directories respectively.

1. Open a terminal and navigate to the root directory of the `signals-gisib-ams`
application.
2. Run the following command to deploy PostgreSQL:
    ```bash
    ./helm-charts/manual/postgres/install.sh
    ```
3. Run the following command to deploy RabbitMQ:
    ```bash
    ./helm-charts/manual/rabbitmq/install.sh
    ```

Note: **These commands assume that you have already configured Helm to work with
your Kubernetes cluster.**

## Deploying signals-gisib-ams
After PostgreSQL and RabbitMQ are deployed, we can deploy the
`signals-gisib-ams` application using the following steps:

Open a terminal and navigate to the root directory of the `signals-gisib-ams`
application.

Run the following command to deploy the application:

```bash
helm upgrade --install signals-gisib-ams ./helm-charts/signals-gisib-ams
```
This command deploys the application using the `signals-gisib-ams` chart
located in the root directory of the application.

Note: **This command assumes that you have already configured Helm to work with
your Kubernetes cluster.**

Congratulations, you have successfully deployed the `signals-gisib-ams`
application in Kubernetes using Helm!

## Setting Up Secrets in Kubernetes
When deploying the `signals-gisib-ams` app, some sensitive settings need to be
stored as secrets in the `secrets.yaml` file.

To set up a secret in Kubernetes using kubectl, you can create a `secrets.yaml`
file with the following structure:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-custom-signals-gisib-ams-secrets
type: Opaque
data:
  DATABASE_PASSWORD: aW5zZWN1cmU=
  RABBITMQ_PASSWORD: aW5zZWN1cmU=
  SECRETKEY: aW5zZWN1cmU=
  GISIB_PASSWORD: aW5zZWN1cmU=
  GISIB_APIKEY: aW5zZWN1cmU=
  KEYCLOAK_CLIENT_ID: aW5zZWN1cmU=
  KEYCLOAK_CLIENT_SECRET_KEY: aW5zZWN1cmU=
```

Here, `my-custom-signals-gisib-ams-secrets` is the name of the secret, and the
values of the sensitive settings are encoded in Base64. Replace the values 
`aW5zZWN1cmU=` (the base64-endcoded string `insecure`) with the base64-encoded
values of your actual secrets.

To create the secret in Kubernetes, you can run the following command:

```bash
kubectl apply -f secrets.yaml
```

This way, the sensitive settings can be securely passed to the
`signals-gisib-ams` app without being exposed in the deployment files.

## Using Existing Secrets in Kubernetes
If you have a secret defined in your Kubernetes cluster, you can reference it in
your deployment by setting the `existingSecret` field in your `values.yaml`
file. For example, if you have a secret named 
`my-custom-signals-gisib-ams-secrets` (that we have set up in the example above)
, you can reference it in your `values.yaml` file like this:

```yaml
existingSecret: my-custom-signals-gisib-ams-secrets
```

This will tell Kubernetes to use the secret named 
`my-custom-signals-gisib-ams-secrets` for the app deployment instead of creating
a new secret. Make sure that the secret has the same keys as those referenced in
the `values.yaml` file.

## Customizable Environment Variables
The `signals-gisib-ams app` can be customized by setting values in a
`values.yaml` file when deploying. Among the values that can be set are
environment variables (env vars) that control various aspects of the
application's behavior. The following table explains the env vars that can be
set:

| Env Var Name                           | Description                                                                                           | Default Value         |
|----------------------------------------|-------------------------------------------------------------------------------------------------------|-----------------------|
| ALLOWED_HOSTS                          | A comma-separated list of allowed hosts for the app. Set to `*` to allow any host.                    | `gisib.signals.local` |
| LOGGING_LEVEL                          | The level of logging to use (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).                  | `INFO`                |
| APPLICATION_INSIGHTS_CONNECTION_STRING | A connection string for Application Insights. Set to `false` to disable Application Insights.         | `false`               |
| CORS_ALLOW_ALL_ORIGINS                 | Whether to allow requests from any origin. Set to `True` to allow all origins.                        | `True`                |
| CORS_ALLOWED_ORIGINS                   | A comma-separated list of allowed origins for CORS.                                                   | `null`                |
| DATABASE_HOST                          | The hostname or IP address of the PostgreSQL database server.                                         | `postgresql`          |
| DATABASE_PORT                          | The port number to use for the PostgreSQL database server.                                            | `5432`                |
| DATABASE_USER                          | The username to use when connecting to the PostgreSQL database server.                                | `postgres`            |
| DATABASE_NAME                          | The name of the database to use.                                                                      | `signals-gisib`       |
| RABBITMQ_HOST                          | The hostname or IP address of the RabbitMQ server.                                                    | `rabbitmq`            |
| RABBITMQ_PORT                          | The port number to use for the RabbitMQ server.                                                       | `5672`                |
| RABBITMQ_VHOST                         | The virtual host to use when connecting to the RabbitMQ server.                                       | `""`                  |
| RABBITMQ_USER                          | The username to use when connecting to the RabbitMQ server.                                           | `signals-gisib-ams`   |
| GISIB_BASE_URI                         | The base URI of the GISIB API.                                                                        | `null`                |
| GISIB_USERNAME                         | The username to use when authenticating with the GISIB API.                                           | `null`                |
| GISIB_LIMIT                            | The maximum number of records to retrieve from the GISIB API per request.                             | `500`                 |
| GISIB_SLEEP                            | The number of seconds to sleep between requests to the GISIB API.                                     | `0.5`                 |
| SIGNALS_BASE_URI                       | The base URI of the Signals API.                                                                      | `null`                |
| KEYCLOAK_ENABLED                       | Whether Keycloak authentication is enabled.                                                           | `false`               |
| KEYCLOAK_SERVER_URL                    | The URL of the Keycloak server.                                                                       | `null`                |
| KEYCLOAK_REALM_NAME                    | The name of the Keycloak realm to use.                                                                | `null`                |
| KEYCLOAK_GRANT_TYPE                    | The grant type to use when authenticating with                                                        | `null`                |

Example `values.yaml`:
```yaml
env:
  ALLOWED_HOSTS: gisib.signals.local
  CORS_ALLOW_ALL_ORIGINS: true
  CORS_ALLOWED_ORIGINS: http://gisib.signals.local,https://gisib.signals.local
```

Open a terminal and navigate to the root directory of the `signals-gisib-ams`
application.

Run the following command to deploy the application:

```bash
helm upgrade --install signals-gisib-ams ./helm-charts/signals-gisib-ams --values /path/to/values.yaml
```
