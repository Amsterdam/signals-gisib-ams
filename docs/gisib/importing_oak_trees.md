# Importing Oak (Quercus) Trees from GISIB
The GISIB system is not able to provide the data needed to display Oak trees on
a map fast enough. Therefore, the Oak trees are imported in the database.

## Django management command
A Django management command is provided to import the Oak trees.

```shell
python manage.py import_oak_trees --help
```

```
usage: manage.py import_oak_trees [-h] [--days DAYS] [--clear] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                                  [--skip-checks]

Start import oak trees data

optional arguments:
  -h, --help            show this help message and exit
  --days DAYS           Number of days in the past to import oak trees
  --clear               Clear the oak trees from the table before starting the import.
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

## Celery
This project includes a Celery task that can be scheduled via the Django admin.

The task is named `import_quercus_trees` and it (like name suggest) imports all 
oak trees into the system.

You can configure the task to check for changes since a certain number of days 
ago by setting the parameter for `time_delta`. If you want to **clear** the
database before importing the data, you can set the `clear` parameter to `True`.

**Please note that running the task may take some time, depending on the size of
the data being imported and the connection to GISIB. We recommend scheduling
the task once per day or per week, rather than at shorter intervals, to avoid
overloading the system and/or GISIB.**

## API

The Oak trees can be accessed through the provided API, more information about
the API can be found [here](../api/README.md).