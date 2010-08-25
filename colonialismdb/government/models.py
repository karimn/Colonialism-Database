from django.db import models

from colonialismdb.common.models import Location, BaseDataEntry, Category, SpatialAreaUnit, Currency
from colonialismdb.sources.models import BaseSourceObject 

class RevenueType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_revenuetype', 'Can activate submitted revenue type'), 
                    ('merge_revenuetype', 'Can merge occupation revenue type') )

class ExpenditureType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_expendituretype', 'Can activate submitted expenditure type'), 
                    ('merge_expendituretype', 'Can merge occupation expenditure type') )
    
class MoneySupplyType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_moneysupplytype', 'Can activate submitted money supply type'), 
                    ('merge_moneysupplytype', 'Can merge occupation money supply type') )

class MilitaryType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_militarytype', 'Can activate submitted military type'), 
                    ('merge_militarytype', 'Can merge occupation military type') )

class OfficialsType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_officialstype', 'Can activate submitted officials type'), 
                    ('merge_officialstype', 'Can merge occupation officials type') )

class MainDataEntry(BaseDataEntry):
  class Meta(BaseDataEntry.Meta):
    verbose_name = "government data entry"
    verbose_name_plural = "government data entries"
    permissions = ( ('activate_maindataentry', 'Can activate submitted govt data entry'), )

  # Should these be moved to location?
  spatial_area = models.IntegerField(null = True, blank = True)
  spatial_area_unit = models.ForeignKey(SpatialAreaUnit, null = True, blank = True)

  currency = models.ForeignKey(Currency, null = True, blank = True)
  currency_exchange_rate = models.IntegerField(null = True, blank = True)

  revenue = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
  revenue_type = models.ForeignKey(RevenueType, null = True, blank = True)

  expenditure = models.IntegerField(null = True, blank = True)
  expenditure_type = models.ForeignKey(ExpenditureType, null = True, blank = True)

  public_debt = models.IntegerField(null = True, blank = True) 

  money_supply = models.IntegerField(null = True, blank = True)
  money_supply_type = models.ForeignKey(MoneySupplyType, null = True, blank = True)

  military = models.IntegerField("military personnel", null = True, blank = True)
  military_type = models.ForeignKey(MilitaryType, null = True, blank = True)

  officials = models.IntegerField(null = True, blank = True)
  officials_type = models.ForeignKey(OfficialsType, null = True, blank = True)

  def activate(self):
    super(MainDataEntry, self).activate()

    if self.spatial_area_unit and not self.spatial_area_unit.active:
      self.spatial_area_unit.activate()

    if self.currency and not self.currency.active:
      self.currency.activate()
    
    if self.revenue_type and not self.revenue_type.active:
      self.revenue_type.activate()
      
    if self.expenditure_type and not self.expenditure_type.active:
      self.expenditure_type.activate()

    if self.money_supply_type and not self.money_supply_type.active:
      self.money_supply_type.activate()

    if self.military_type and not self.military_type.active:
      self.military_type.activate()

    if self.officials_type and not self.officials_type.active:
      self.officials_type.activate()
