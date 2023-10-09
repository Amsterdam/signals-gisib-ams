from django.contrib.gis.geos import Polygon
from django.db.models import Q, QuerySet
from django_filters import ChoiceFilter, FilterSet, NumberFilter
from django_filters.rest_framework import CharFilter
from rest_framework.exceptions import ValidationError


class FeatureCollectionFilterSet(FilterSet):
    id = NumberFilter(field_name='gisib_id', lookup_expr='exact')
    object_kind_name = ChoiceFilter(lookup_expr='iexact', required=True, choices=[('Boom', 'Boom')])
    bbox = CharFilter(method='filter_by_bbox')

    def filter_by_bbox(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        """
        Filter the queryset by CollectionItem's geometry field's bounding box
        :param queryset: the queryset to filter
        :param name: the name of the filter (unused)
        :param value: the bounding box values in the format 'min_lon,min_lat,max_lon,max_lat'
        :return: the filtered queryset
        """
        try:
            bbox = [float(x) for x in value.split(",")]
        except ValueError:
            raise ValidationError("Invalid bbox format. Expecting 'min_lon,min_lat,max_lon,max_lat'")
        if len(bbox) != 4:
            raise ValidationError("Invalid bbox format. Expecting 'min_lon,min_lat,max_lon,max_lat'")
        polygon = Polygon.from_bbox(bbox)
        return queryset.filter(Q(geometry__within=polygon) | Q(geometry__contains=polygon))

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        queryset = queryset.filter(geometry__isnull=False)
        return super().filter_queryset(queryset=queryset)
