from django.db import models

from colonialismdb.common.models import Location, BaseDataEntry, Category, SpatialAreaUnit, Currency
from colonialismdb.sources.models import BaseSourceObject 
    
class MainDataEntry(BaseDataEntry):
  class Meta(BaseDataEntry.Meta):
    verbose_name = "infrastructure data entry"
    verbose_name_plural = "infrastructure data entries"
    permissions = ( ('activate_maindataentry', 'Can activate submitted data entry'), )

  # Should these be moved to location?
  spatial_area = models.IntegerField(null = True, blank = True)
  spatial_area_unit = models.ForeignKey(SpatialAreaUnit, null = True, blank = True, related_name = '%(app_label)s_%(class)s_related')

  currency = models.ForeignKey(Currency, null = True, blank = True, related_name = '%(app_label)s_%(class)s_related')
  currency_exchange_rate = models.IntegerField(null = True, blank = True)

  railroad_length = models.IntegerField(null = True, blank = True)
  railroad_freight = models.BooleanField(default = False)
  railroad_revenue = models.IntegerField(null = True, blank = True)
  railroad_expenditure = models.IntegerField(null = True, blank = True)

  road_length = models.IntegerField(null = True, blank = True)
  telegraph_length = models.IntegerField(null = True, blank = True)

  def activate(self):
    super(MainDataEntry, self).activate()
