# GISIB Geograpy endpoint
The endpoint `/public/gisib/geography/` is used to retrieve collections that are
imported from the GISIB system (for more information see this document
[importing Oak (Quercus) trees](../gisib/importing_oak_trees.md)). This endpoint
must be called with a query parameter called `object_kind_name`, and the only
value supported at this moment is `Boom`. It is also possible to filter the
results using the optional `bbox` query parameter.

## Request URL
```
/public/gisib/geography/?object_kind_name={object_kind_name}&bbox={minX},{minY},{maxX},{maxY}
```

* {object_kind_name}: the object kind you want to retrieve, currently the only value is `Boom`
* {minX}: the minimum longitude of the bounding box
* {minY}: the minimum latitude of the bounding box
* {maxX}: the maximum longitude of the bounding box
* {maxY}: the maximum latitude of the bounding box

## Request method
```
GET
```

## Response
The endpoint will return a feature collection containing features in the
following format:
```json
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Link: 
 <http://127.0.0.1:8001/public/gisib/geography/?object_kind_name=Boom&bbox=4.0,52.0,4.9,54.0>; rel="self"
Vary: Accept
X-Total-Count: 2

{
    "type": "FeatureCollection",
    "features": [
        {
            "id": 1875186,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.8655,
                    52.358868
                ]
            },
            "properties": {
                "species": "Quercus robur"
            }
        },
        {
            "id": 1875184,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.864281,
                    52.358289
                ]
            },
            "properties": {
                "species": "Quercus robur"
            }
        }
    ]
}
```

See [this](./geo_json.md) documentation for more information on
FeatureCollections.

## Example Request using cURL
Assuming that the application is running on localhost, the following is an
example request using cURL to filter the results using a bounding box:

```shell
curl -X GET "http://localhost:8001/public/gisib/geography/?object_kind_name=Boom&bbox=4.0,52.0,4.9,54.0"
```

This request will return all oak trees that are imported from the GISIB system
with the `object_kind_name` of "Boom" and are within the specified bounding box,
in the format described above.

Want to know how to run the system locally? Check out the
[development guide](../development.md).