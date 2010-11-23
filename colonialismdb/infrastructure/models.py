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

  currency = models.ForeignKey(Currency, null = True, blank = True, related_name = '%(app_label)s_%(class)s_related')
  currency_exchange_rate = models.CharField(max_length = 50, null = True, blank = True)

  railroad_revenue = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Gross railway revenue for the year")
  railroad_expenditure = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Gross railway expenditure (including building and extraordinary costs) for the year")
  railroad_length = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True)
  railroad_length_unit = models.ForeignKey(LengthUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_railroad_set")
  railroad_num_passengers = models.DecimalField("railroad passengers per year", max_digits = 20, decimal_places = 2, null = True, blank = True)
  railroad_num_passengers_value_unit = models.CharField("passengers value units", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  railroad_passenger_km = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Passenger-kilometers (total km traveled) per year") 
  railroad_passenger_km_value_unit = models.CharField("passenger-kilometer value units", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  railroad_freight = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Quantity of railway freight carried per year")
  railroad_freight_value_unit = models.CharField("railway freight value units", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  railroad_freight_unit = models.ForeignKey(WeightUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_freight_set")
  railroad_freight_ton_km = models.DecimalField(max_digits = 20, decimal_places = 3, null = True, blank = True, help_text = "in metric tons")
  railroad_freight_ton_km_value_unit = models.CharField("freight ton-kilometer value units", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  
  road_revenue = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Gross road revenue for the year")
  road_expenditure = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Gross road expenditure for the year")
  road_length = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True)
  road_length_unit = models.ForeignKey(LengthUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_road_set")

  num_motor_vehicles = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True)
  num_motor_vehicles_value_unit = models.CharField("number of motor vehicles value units", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  motor_vehicles_type = models.ForeignKey(MotorVehicleType, null = True, blank = True)

  num_telephones = models.BigIntegerField("number of telephones registered / in use", null = True, blank = True)

  telegraph_length = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True)
  telegraph_length_unit = models.ForeignKey(LengthUnit, null = True, blank = True, related_name = "infrastructure_maindataentry_telegraph_set")
  telegraph_num_stations = models.BigIntegerField("number of telegraph stations", blank = True, null = True)
  telegraph_num_sent = models.DecimalField("number of telgraphs sent", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "per year")
  telegraph_num_sent_value_unit = models.CharField("number of telegraphs sent value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')


  postal_revenue = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Gross postal revenue for the year")
  postal_expenditure = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Gross postal expenditure for the year")
  postal_num_stations = models.BigIntegerField("number of postal stations", blank = True, null = True)
  postal_num_items = models.DecimalField("mail sent/received", max_digits = 20, decimal_places = 2, blank = True, null = True, help_text = "per year")
  postal_num_items_value_unit = models.CharField("mail sent/received value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  postal_items_type = models.ForeignKey(PostalItemType, null = True, blank = True)
  postal_num_boxes = models.BigIntegerField("number of postal boxes", null = True, blank = True)
  postal_num_staff = models.BigIntegerField("number of postal staff", null = True, blank = True)

  ships_all_num = models.BigIntegerField("number of all ships", null = True, blank = True)
  ships_all_num_value_unit = models.CharField("number of all ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_motor_num = models.BigIntegerField("number of motor ships", null = True, blank = True)
  ships_motor_num_value_unit = models.CharField("number of motor ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_sail_num = models.BigIntegerField("number of sail ships", null = True, blank = True)
  ships_sail_num_value_unit = models.CharField("number of sail ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_steam_num = models.BigIntegerField("number of steam ships", null = True, blank = True)
  ships_steam_num_value_unit = models.CharField("number of steam ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_steammotor_num = models.BigIntegerField("number of steam and motor ships", null = True, blank = True)
  ships_steammotor_num_value_unit = models.CharField("number of steam and motor ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')

  ships_all_ton = models.DecimalField("tonnage of all ships", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "in metric tons")
  ships_all_ton_value_unit = models.CharField("tonnage of all ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_motor_ton = models.DecimalField("tonnage of motor ships", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "in metric tons")
  ships_motor_ton_value_unit = models.CharField("tonnage of motor ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_sail_ton = models.DecimalField("tonnage of sail ships", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "in metric tons")
  ships_sail_ton_value_unit = models.CharField("tonnage of sail ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_steam_ton = models.DecimalField("tonnage of steam ships", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "in metric tons")
  ships_steam_ton_value_unit = models.CharField("tonnage of steam ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  ships_steammotor_ton = models.DecimalField("tonnage of steam and motor ships", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "in metric tons")
  ships_steammotor_ton_value_unit = models.CharField("tonnage of steam and motor ships value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')

  # TODO remove below merchant ship fields and integrate them with above ships fields
  merchant_ships_num = models.BigIntegerField("number of merchant ships registered", null = True, blank = True)
  merchant_ships_type = models.ForeignKey(MerchantShipType, blank = True, null = True)
  merchant_ships_cargo = models.BigIntegerField(null = True, blank = True)
  merchant_ships_cargo_unit = models.ForeignKey(WeightUnit, blank = True, null = True, related_name = "infrastructure_maindataentry_merchant_ships_cargo_set")

  air_cargo = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, blank = True)
  air_cargo_unit = models.ForeignKey(WeightUnit, blank = True, null = True, related_name = "infrastructure_maindataentry_air_cargo_set")
  air_cargo_ton_km = models.DecimalField("air cargo ton-kilometers", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Cargo ton-kilometers (total km traveled) per year")
  air_cargo_ton_km_value_unit = models.CharField("air cargo ton-kilometers value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  air_passenger_km = models.DecimalField("air passenger-kilometers", max_digits = 20, decimal_places = 2, null = True, blank = True, help_text = "Passenger-kilometers (total km traveled) per year") 
  air_passenger_km_value_unit = models.CharField("air passenger-kilometers value unit", max_length = 20, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')

  def activate(self):
    super(MainDataEntry, self).activate()

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
