from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import CharField, Value
from django.db.models.functions import JSONObject
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from signals_gisib.filters import FeatureCollectionFilterSet
from signals_gisib.models.gisib import CollectionItem
from signals_gisib.pagination import LinkHeaderPagination

schema_view = get_schema_view(
    openapi.Info(
        title="signals-gisib-ams",
        default_version="0.1.11",
        description="This API returns information about oak trees in a specific location as a GeoJSON output. "
                    "The API supports query parameters for filtering results.",
        license=openapi.License(name="EUPL", url="https://github.com/Amsterdam/signals-gisib-ams/blob/main/LICENSE"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
    authentication_classes=[],
    urlconf=None,
)


class GisibViewSet(GenericViewSet):
    lookup_field = 'gisib_id'
    queryset = CollectionItem.objects.all()
    filterset_class = None

    @action(detail=False, url_path=r'geography', methods=['GET'], filterset_class=FeatureCollectionFilterSet)
    @swagger_auto_schema(
        operation_description='Retrieve the geography feature collection',
        responses={200: openapi.Response('Feature collection', schema=openapi.Schema(
            type='object',
            properties={
                'type': openapi.Schema(type='string', example='FeatureCollection'),
                'features': openapi.Schema(
                    type='array',
                    items=openapi.Schema(
                        type='object',
                        properties={
                            'id': openapi.Schema(type='integer', example=1234567890),
                            'type': openapi.Schema(type='string', example='Feature'),
                            'geometry': openapi.Schema(
                                type='object',
                                properties={
                                    'type': openapi.Schema(type='string', example='Point'),
                                    'coordinates': openapi.Schema(
                                        type='array',
                                        items=openapi.Schema(type='number', format='float'),
                                        example=[4.984062, 52.308218]
                                    )
                                }
                            ),
                            'properties': openapi.Schema(type='object', example={'species': 'Quercus'})
                        }
                    )
                )
            }
        ))}
    )
    def geography(self, *args, **kwargs):
        features_qs = self.filter_queryset(self.get_queryset().annotate(
            feature=JSONObject(
                type=Value('Feature', output_field=CharField()),
                id='gisib_id',
                geometry=AsGeoJSON('geometry', template='%(function)s(%(expressions)s)::jsonb'),
                properties='properties',
            )
        )).order_by('-id')

        feature_collection = {'type': 'FeatureCollection', 'features': []}
        paginator = LinkHeaderPagination(page_query_param='page')
        page_qs = paginator.paginate_queryset(features_qs, self.request, view=self)

        features = page_qs.aggregate(features=JSONBAgg('feature'))
        feature_collection.update(features)
        headers = paginator.get_pagination_headers()

        return Response(feature_collection, status=200, headers=headers)
