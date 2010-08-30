from django.db import models

from colonialismdb.common.models import Location, BaseDataEntry, Category, SpatialAreaUnit, Currency, LengthUnit, WeightUnit
from colonialismdb.sources.models import BaseSourceObject 

class MotorVehicleType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_mvehicletype', 'Can activate submitted type'), 
                    ('merge_mvehicletype', 'Can merge occupation type') )

  def merge_into(self, other):
    super(MotorVehicleType, self).merge_into(other)
    self.maindataentry_set.all().update(motor_vehicles_type = other)
    
class PostalItemType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_postalitemtype', 'Can activate submitted type'), 
                    ('merge_postalitemtype', 'Can merge occupation type') )

  def merge_into(self, other):
    super(PostalItemType, self).merge_into(other)
    self.maindataentry_set.all().update(postal_items_type = other)

class MerchantShipType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_mshiptype', 'Can activate submitted type'), 
                    ('merge_mshiptype', 'Can merge occupation type') )

  def merge_into(self, other):
    super(MerchantShipType, self).merge_into(other)
    self.maindataentry_set.all().update(merchant_ships_type = other)

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

  railroad_revenue = models.IntegerField(null = True, blank = True, help_text = "Gross railway revenue for the year")
  railroad_expenditure = models.IntegerField(null = True, blank = True, help_text = "Gross railway expenditure (including building and extraordinary costs) for the year")
  railroad_length = models.IntegerField(null = True, blank = True)
  railroad_length_unit = models.ForeignKey(LengthUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_railroad_set")
  railroad_num_passengers = models.IntegerField("railroad passengers per year", null = True, blank = True)
  railroad_passenger_km = models.IntegerField("railroad passenger-kilometers", null = True, blank = True, help_text = "Passenger-kilometers (total km traveled) per year") 
  railroad_freight = models.IntegerField(null = True, blank = True, help_text = "Quantity of railway freight carried per year")
  railroad_freight_unit = models.ForeignKey(WeightUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_freight_set")
  
  road_revenue = models.IntegerField(null = True, blank = True, help_text = "Gross road revenue for the year")
  road_expenditure = models.IntegerField(null = True, blank = True, help_text = "Gross road expenditure for the year")
  road_length = models.IntegerField(null = True, blank = True)
  road_length_unit = models.ForeignKey(LengthUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_road_set")

  num_motor_vehicles = models.IntegerField("number of motor vehicles", null = True, blank = True)
  motor_vehicles_type = models.ForeignKey(MotorVehicleType, null = True, blank = True)

  num_telephones = models.IntegerField("number of telephones registered / in use", null = True, blank = True)
  
  telegraph_length = models.IntegerField(null = True, blank = True)
  telegraph_length_unit = models.ForeignKey(LengthUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_telegraph_set")
  telegraph_num_stations = models.IntegerField("number of telegraph stations", blank = True, null = True)
  telegraph_num_sent = models.IntegerField("number of telgraphs sent", blank = True, null = True, help_text = "per year")

  # TODO TelegraphWires?

  postal_revenue = models.IntegerField(null = True, blank = True, help_text = "Gross postal revenue for the year")
  postal_expenditure = models.IntegerField(null = True, blank = True, help_text = "Gross postal expenditure for the year")
  postal_num_stations = models.IntegerField("number of postal stations", blank = True, null = True)
  postal_num_items = models.IntegerField("number of items sent", blank = True, null = True, help_text = "per year")
  postal_items_type = models.ForeignKey(PostalItemType, null = True, blank = True)
  postal_num_boxes = models.IntegerField("number of postal boxes", null = True, blank = True)
  postal_num_staff = models.IntegerField("number of postal staff", null = True, blank = True)

  merchant_ships_num = models.IntegerField("number of merchant ships registered", null = True, blank = True)
  merchant_ships_type = models.ForeignKey(MerchantShipType, blank = True, null = True)

  merchant_ships_cargo = models.IntegerField(null = True, blank = True)
  merchant_ships_cargo_unit = models.ForeignKey(WeightUnit, blank = True, null = True, related_name = "infrastructure_maindataentry_merchant_ships_cargo_set")

  air_cargo = models.IntegerField(null = True, blank = True)
  air_cargo_unit = models.ForeignKey(WeightUnit, blank = True, null = True, related_name = "infrastructure_maindataentry_air_cargo_set")

  air_passenger_km = models.IntegerField("air passenger-kilometers", null = True, blank = True, help_text = "Passenger-kilometers (total km traveled) per year") 

  def activate(self):
    super(MainDataEntry, self).activate()

    if self.spatial_area_unit and not self.spatial_area_unit.active:
      self.spatial_area_unit.activate()

    if self.currency and not self.currency.active:
      self.currency.activate()

    if self.railroad_length_unit and not self.railroad_length_unit.active: self.railroad_length_unit.activate()
    if self.road_length_unit and not self.road_length_unit.active: self.road_length_unit.activate()
    if self.telegraph_length_unit and not self.telegraph_length_unit.active: self.telegraph_length_unit.activate()

    if self.railroad_freight_unit and not self.railroad_freight_unit.active: self.railroad_freight_unit.activate()

    if self.motor_vehicles_type and not self.motor_vehicles_type.active: self.motor_vehicles_type.activate()

    if self.postal_items_type and not self.postal_items_type.active: self.postal_items_type.activate()
    
    if self.merchant_ships_type and not self.merchant_ships_type.active: self.merchant_ships_type.activate()

    if self.merchant_ships_cargo_unit and not self.merchant_ships_cargo_unit.active: self.merchant_ships_cargo_unit.activate()
    if self.air_cargo_unit and not self.air_cargo_unit.active: self.air_cargo_unit.activate()
