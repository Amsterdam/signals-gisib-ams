# Creating EPR Curative
This file explains how an EPR curative is created in the GISIB system. The EPR
curative is created when a Signal is received containing information about the
location of trees affected by the Eikenprocessierups.

## Signal
When a signal is received, a task is triggered to create the EPR curative in the
GISIB system. This task uses the `create_epr_curative` function defined in the
[create_epr_curative.py](../../app/signals_gisib/gisib/create_epr_curative.py)
file located in the `signals_gisib/gisib` folder of the application.

The `extra_properties` of a Signal contain the selected trees and relevant
information. This information must be translated to the correct values for
GISIB. The `nest_size` and `tree_id(s)` are currently the only questions that
are translated to the appropriate GISIB value. The translation is done by
checking the given answer with a translation dictionary, and then the correct id
is selected from the configuration stored in the database. The configuration is
imported as described in [importing_epr_configuration.md](./importing_epr_configuration.md).

If no tree id is given or the tree id is not known by GISIB, the location
provided by the Signal is used instead. The coordinates must be in the format of
the [Rijksdriehoekscoördinaten](https://nl.wikipedia.org/wiki/Rijksdriehoeksco%C3%B6rdinaten)
system.

## Creating an EPR curative

Below are two examples of how to create an EPR curative.

### Create an EPR Curative with a tree ID
To create an EPR curative with a known tree id:
```
URI: {GISIB_BASE_URI}/Collections/Insert
METHOD: POST
Headers: {'Authorization': {BEARER_TOKEN}}
```
Body:
```json
{
    "Properties": {
        "SIG Nummer melding": 123456,
        "Datum melding": "01-04-2023 12:00",
        "Nestformaat": 654321,
        "Boom": 7890
    },
    "ObjectKindNaam": "EPR Curatief"
}
```
The Properties object contains the following fields:

- SIG Nummer melding: The signal number of the notification.
- Datum melding: The date and time of the notification.
- Nestformaat: The id of the nest size as defined in the configuration stored in the database.
- Boom: The id of the tree affected by the Eikenprocessierups.

- Response:
```json
{
  "Warnings": null,
  "Message": "OK",
  "Errors": null,
  "Properties": {
    "SIG Nummer melding": 123456,
    "Datum melding": "01-04-2023 12:00",
    "Nestformaat": 654321,
    "Boom": 7890,
    "Id": 234567,
    "GUID": "{00000000-0000-0000-0000-000000000000}"
  }
}
```

### Create an EPR Curative without a tree ID
If the tree id is not known:
```
URI: {GISIB_BASE_URI}/Collections/Insert
METHOD: POST
Headers: {'Authorization': {BEARER_TOKEN}}
```
Body:
```json
{
    "Properties": {
        "SIG Nummer melding": 123456,
        "Datum melding": "01-04-2023 12:00",
        "Nestformaat": 654321,
        "Geometry": {
          "type": "Point",
          "coordinates": [127506.00, 480104.00]
        }
    },
    "ObjectKindNaam": "EPR Curatief"
}
```
The Properties object contains the same fields as described above, however the
`Boom` field has been replaced by the `Geometry` field containing the location
in the RD-coordinates format.

Response:
```json
{
  "Warnings": null,
  "Message": "OK",
  "Errors": null,
  "Properties": {
    "SIG Nummer melding": 123456,
    "Datum melding": "01-04-2023 12:00",
    "Nestformaat": 654321,
    "Id": 234567,
    "GUID": "{00000000-0000-0000-0000-000000000000}"
  }
}
```