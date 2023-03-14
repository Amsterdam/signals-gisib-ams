from django.db.models import Func


class AsGeoJSON(Func):
    """
    A Django Function class that creates a SQL expression that returns the
    geometry in GeoJSON format.
    """
    function = 'st_asgeojson'
    template = '%(function)s(%(expressions)s)::jsonb'
