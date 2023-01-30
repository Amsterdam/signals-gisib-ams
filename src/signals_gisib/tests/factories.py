from factory import Faker
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from signals_gisib.models import Signal
from signals_gisib.models.gisib import CollectionItem
from signals_gisib.tests.fuzzy import FuzzyPoint
from signals_gisib.tests.utils import BBOX_AMSTERDAM


class CollectionItemFactory(DjangoModelFactory):
    class Meta:
        model = CollectionItem
        django_get_or_create = ('gisib_id', )

    gisib_id = Faker('random_int', min=1000, max=9999, step=1)
    object_kind_name = FuzzyChoice(['Boom', ])
    geometry = FuzzyPoint(*BBOX_AMSTERDAM)
    properties = {}
    raw_properties = {}


class SignalFactory(DjangoModelFactory):
    class Meta:
        model = Signal
        django_get_or_create = ('signal_id', )

    signal_id = Faker('random_int', min=1000, max=9999, step=1)
    snapshot = {}
