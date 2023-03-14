from django.db.models import CharField, Value
from django.db.models.functions import JSONObject
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from signals_gisib.filters import FeatureCollectionFilterSet
from signals_gisib.models.aggregates import JSONAgg
from signals_gisib.models.expressions import AsGeoJSON
from signals_gisib.models.gisib import CollectionItem
from signals_gisib.pagination import LinkHeaderPagination


class GisibViewSet(GenericViewSet):
    lookup_field = 'gisib_id'
    queryset = CollectionItem.objects.all()
    filterset_class = None

    @action(detail=False, url_path=r'geography', methods=['GET'], filterset_class=FeatureCollectionFilterSet)
    def geography(self, *args, **kwargs):
        features_qs = self.filter_queryset(self.get_queryset().annotate(
            feature=JSONObject(
                type=Value('Feature', output_field=CharField()),
                id='gisib_id',
                geometry=AsGeoJSON('geometry'),
                properties='properties',
            )
        )).order_by('-id')

        feature_collection = {'type': 'FeatureCollection', 'features': []}
        paginator = LinkHeaderPagination(page_query_param='page')
        page_qs = paginator.paginate_queryset(features_qs, self.request, view=self)

        features = page_qs.aggregate(features=JSONAgg('feature'))
        feature_collection.update(features)
        headers = paginator.get_pagination_headers()

        return Response(feature_collection, status=200, headers=headers)
