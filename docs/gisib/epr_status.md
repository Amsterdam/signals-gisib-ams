## GISIB Registratie EPR Flow
When A Signal is imported and EPR curatives are made in the GISIB system the 
system must periodically check these EPR curatives to see if they are handeld by
the GISIB system.

The celery task `check_epr_curative_status` can be scheduled to check all open
EPR curatives via the celery crontab.

When an EPR curative is checked the field `Registratie EPR status` indicates the 
current status. This status can have several values, as listed below:

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


The `Handled` column indicates whether an EPR curative with the corresponding
Registratie EPR status has been processed and resolved 
(i.e., "Afgehandeld" in Dutch).

When all EPR curatives that where created for a Signal are processed the Signal 
can be updated.
