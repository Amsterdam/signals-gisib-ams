# Welcome to the "signals-gisib-ams" GitHub project!

The "signals-gisib-ams" GitHub project is a tool that facilitates communication between the RESTful Signals API and 
GISIB (Geographic Information System) for the City of Amsterdam.

## GISIB Registratie EPR Flow

The Registratie EPR status is a field in the GISIB system that indicates the current status of an Eikenprocessierups (EPR) report. This status can have several values, as listed below:

| Registratie EPR      | Afgehandeld? |
|----------------------|--------------|
| Melding              | Nee          |
| Inspectie            | Nee          |
| Registratie EPR      | Nee          |
| Geen                 | Ja           |
| EPR Niet bestrijden  | Ja           |
| EPR Bestreden        | Ja           |
| EPR Deels bestreden  | Nee          |
| Dubbele melding      | Ja           |
| Niet in beheergebied | Ja           |

When a report related to the Eikenprocessierups is made, the Registratie EPR status can have one of two values: "Melding" or "Registratie EPR". The status of the report may change as work is done to address the issue, and it is important to periodically check the Registratie EPR status in the GISIB system to see if it has changed.

The "Afgehandeld?" column indicates whether a report with the corresponding Registratie EPR status has been processed and resolved (i.e., "Afgehandeld" in Dutch).

## Running and developing locally

Set up a virtual environment and activate it:

```shell
$(which python3) -m venv venv
source venv/bin/activate
```

Install dependencies in the virtual environment using the provided `make` command:

```shell
make install
```

Start the development database provided in the docker-compose.yml:

```shell
docker-compose up -d postgis
```

You can now either run the application from the virtual environment using the following command:

```shell
python app/manage.py runserver 0.0.0.0:8000
```

Or you can use docker-compose:

```shell
docker-compose up app
```

## Running the tests

To run the complete test suite you can use the following command:

```shell
docker-compose run --rm app tox
```

## Note
This project is designed and optimized for the Amsterdam municipality and may not be fully compatible with other 
environments. It is recommended to consider this limitation before implementation in other locations.

## Thanks for visiting!
