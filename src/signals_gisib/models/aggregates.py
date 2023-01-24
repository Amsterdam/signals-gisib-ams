from django.db.models import Aggregate, JSONField


class JSONAgg(Aggregate):
    """
    A Django Aggregate class that creates a SQL expression that returns the
    result of the json_agg function in jsonb format
    """
    function = 'json_agg'
    template = '%(function)s(%(distinct)s%(expressions)s)::jsonb'
    output_field = JSONField()
