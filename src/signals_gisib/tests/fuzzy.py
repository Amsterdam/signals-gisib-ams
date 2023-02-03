import random

from django.contrib.gis.geos import Point
from factory.fuzzy import BaseFuzzyAttribute


class FuzzyPoint(BaseFuzzyAttribute):
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        super().__init__()

    def fuzz(self):
        return Point(random.uniform(self.min_x, self.max_x), random.uniform(self.min_y, self.max_y), srid=4326)
