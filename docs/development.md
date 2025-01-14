# Local Development Guide
This guide explains how to set up and run the project locally using Docker for
local development.

## Prerequisites
Before starting with the setup, make sure the following are installed:

- Git
- Docker

## Cloning the repository
First, clone the repository:

```shell
git clone https://github.com/amsterdam/signals-gisib-ams
```

## Building the Docker images
After cloning the repository, navigate to the root directory and pull the
relevant images and build the services:

```shell
cd signals-gisib-ams/
docker-compose pull
docker-compose build
```

## Running the application
To run the application run the following command:
```shell
docker-compose up app
```

You can now access the Django admin on http://localhost:8000/admin.

In the [docker-compose.yml](../docker-compose.yml) file, the command section
under the app service specifies that the container should run the
[/run.sh](../docker-compose/run.sh) script. This script is responsible for
running all the basic setup required for the application to work properly.

## Create/Recreate the requirements

Set up a virtual environment and activate it:

```shell
$(which python3) -m venv venv
source venv/bin/activate
```

To create or update the dependencies run the provided `make` command:

```shell
make requirements
```

This will update the [requirements.txt](./requirements/requirements.txt), 
[requirements_dev.txt](./requirements/requirements_dev.txt) and 
[requirements_test.txt](./requirements/requirements_test.txt).

Install dependencies in the virtual environment using the provided `make` command:

```shell
make install
```

Updating the Docker container:

```shell
docker-compose build
```

or to force docker to build from scratch:

```shell
docker-compose build --no-cache
```

## Running the test suite and style checks
When developing you may want to run the test suite and style checks from time
to time. Run the test suite:

```shell
docker-compose run --rm app tox
```

Or if you only want to run a specific test or tests:

```shell
docker-compose run --rm app tox -e pytest {path/to/test::test.py::test_function} -- -n0
```

**Make sure to check if the all checks succeed before submitting a pull request.**
