# Importing the EPR configuration from GISIB
To create an EPR curative in GISIB some configuration must be loaded.

## "Nestformaat" configuration
In GISIB there are Collection items with the object_kind_name `Nestformaat`. 
These items contain the configuration needed to translate the given answer about
the nest size that has been spotted in the given oak tree.

In the Signal extra properties this is given as:
```json
[
  ...
  {
    "id": "extra_nest_grootte",
    "label": "Op de boom gezien",
    "answer": {
      "id": "deken",
      "label": "Rupsen bedekken de stam als een deken"
    }
  }
  ...
]
```

The match is done with a translation between the given "label".

When this document was created the translation is:

| Signal extra property label                         | GISIB Description                                   |
|-----------------------------------------------------|-----------------------------------------------------|
| Nest is zo groot als een tennisbal                  | Nest is zo groot als een tennisbal                  |
| Nest is zo groot als een voetbal                    | Nest is zo groot als een voetbal                    |
| Rupsen bedekken de stam als een deken               | Rupsen bedekken de stam als een deken               |
| De rupsen in de boom hebben nog geen nest gevormd   | De rupsen in de boom hebben nog geen nest gevormd   |


## Status of an EPR Curative
An EPR curative is created and gets a certain state in GISIB. Every X period
the app will check the status from all open EPR curatives. To know when an EPR
curative has been processed the app needs to know for which ID's to look for.
This data is imported by getting all collection items with the object_kind_name
`Registratie EPR`. 

In GISIB te following statuses are configured:

| EPR Curative status  | Handled  |
|----------------------|----------|
| Melding              | No       |
| Inspectie            | No       |
| Registratie EPR      | No       |
| Geen                 | Yes      |
| EPR Niet bestrijden  | Yes      |
| EPR Bestreden        | Yes      |
| EPR Deels bestreden  | No       |
| Dubbele melding      | Yes      |
| Niet in beheergebied | Yes      |


## Django management command
A Django management command is provided to import the configuration.

```shell
python manage.py import_epr_configuration --help
```

```
usage: manage.py import_epr_configuration [-h] [--clear] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                                          [--skip-checks]

Start import of EPR configuration needed to translate between Signals and GISIB

options:
  -h, --help            show this help message and exit
  --clear               Clear the configuration from the table before starting the import.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```

## API

The configuration can be retrieved through the provided API, more information
about the API can be found [here](../api/README.md).