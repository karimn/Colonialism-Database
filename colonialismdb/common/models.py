import datetime

from django.contrib.gis.db import models as geo_models
from django.db import models, connection
from django.contrib.auth.models import User

class LockableModel:
  locked = models.BooleanField(default = False)

class MergeableModel(models.Model):
  class Meta:
    abstract = True

  def merge_into(self, other):
    if not isinstance(other, type(self)):
      raise TypeError

class BaseSubmitModel(models.Model):
  class Meta:
    abstract = True

  def activate(self):
    self.active = True
    self.save()

  def deactivate(self):
    self.active = False
    self.save()

  active = models.BooleanField(default = False)
  submitted_by = models.ForeignKey(User, null = True, editable = False, related_name = "submitted_%(app_label)s_%(class)s")
  datetime_created = models.DateTimeField("created at", auto_now_add = True, editable = False)

class Category(BaseSubmitModel, MergeableModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

  def __unicode__(self):
    return unicode(self.name)

  def merge_into(self, other):
    super(Category, self).merge_into(other)

  NAME_MAX_LENGTH = 100

  name = models.CharField(max_length = NAME_MAX_LENGTH, unique = True)

class Religion(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_religion', 'Can activate submitted religion'),
                    ('merge_religion', 'Can merge religion entries') )

  def merge_into(self, other):
    super(Religion, self).merge_into(other)

    self.maindataentry_set.all().update(religion = other)

class Race(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_race', 'Can activate submitted race'), 
                    ('merge_race', 'Can merge race entries') )

  def merge_into(self, other):
    super(Race, self).merge_into(other)

    self.maindataentry_set.all().update(religion = other)

class Ethnicity(Category):
  class Meta(Category.Meta):
    verbose_name_plural = 'ethnicities'
    permissions = ( ('activate_ethnicity', 'Can activate submitted ethnicity'),
                    ('merge_ethnicity', 'Can merge ethnicity entries') )

  def merge_into(self, other):
    super(Ethnicity, self).merge_into(other)

    self.maindataentry_set.all().update(religion = other)
    
class EthnicOrigin(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_ethnic_origin', 'Can activate submitted ethnic origin'), 
                    ('merge_ethnic_origin', 'Can merge ethnic origin entries') )

  def merge_into(self, other):
    super(EthnicOrigin, self).merge_into(other)
    self.maindataentry_set.all().update(religion = other)

class LengthUnit(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_length_unit', 'Can activate submitted length unit'), 
                    ('merge_length_unit', 'Can merge length unit') )

  def merge_into(self, other):
    super(LengthUnit, self).merge_into(other)
    self.infrastructure_maindataentry_railroad_set.all().update(railroad_length_unit = other)
    self.infrastructure_maindataentry_road_set.all().update(road_length_unit = other)
    self.infrastructure_maindataentry_telegraph_set.all().update(telegraph_length_unit = other)

class WeightUnit(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_weight_unit', 'Can activate submitted weight unit'), 
                    ('merge_weight_unit', 'Can merge weight unit') )

  def merge_into(self, other):
    super(WeightUnit, self).merge_into(other)
    self.infrastructure_maindataentry_freight_set.all().update(railroad_freight_unit = other)
    self.infrastructure_maindataentry_merchant_ships_cargo_set.all().update(merchant_ships_cargo_unit = other)
    self.infrastructure_maindataentry_air_cargo_set.all().update(air_cargo_unit = other)

class PoliticalUnitType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_polunittype', 'Can activate submitted political unit type'),
                    ('merge_polunittype', 'Can merge pol unit type entries') )

  def merge_into(self, other):
    super(PoliticalUnitType, self).merge_into(other)

    for pu in self.politicalunit_set.all():
      pu.unit_type.remove(self)
      pu.unit_type.add(other)

class Language(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_language', 'Can activate source language'), 
                    ('merge_language', 'Can merge language entries') )
    
  def merge_into(self, other):
    super(Language, self).merge_into(other)

    for bo in self.basesourceobject_set.all():
      bo.languages.remove(self)
      bo.languages.add(other)

class SpatialAreaUnit(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_spareaunit', 'Can activate submitted area unit'), 
                    ('merge_spareaunit', 'Can merge occupation area unit') )

class Currency(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_currency', 'Can activate submitted currency'), 
                    ('merge_currency', 'Can merge occupation currency') )
    verbose_name_plural = "currencies"

class PoliticalUnit(BaseSubmitModel,MergeableModel):
  name = models.CharField("name", max_length = 150)
  unit_type = models.ManyToManyField(PoliticalUnitType, null = True, blank = True)

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_politicalunit', 'Can activate submitted political unit'),
                    ('merge_politicalunit', 'Can merge political unit entries') )

  def activate(self):
    super(PoliticalUnit, self).activate()

  def __unicode__(self):
    # Terribly ugly again because subclass method not automatically called
    try:
      return unicode(self.location)
    except Location.DoesNotExist:
      return self.name

  def clean(self):
    super(PoliticalUnit, self).clean()

  def merge_into(self, other):
    super(PoliticalUnit, self).merge_into(other)

    self.politically_contains.all().update(politically_in = other)

    self.population_maindataentry_related.all().update(location = other)
    self.government_maindataentry_related.all().update(location = other)
    self.education_maindataentry_related.all().update(location = other)
    self.infrastructure_maindataentry_related.all().update(location = other)

    for tbl in self.table_set.all():
      tbl.included_countries.remove(self)
      tbl.included_countries.add(other)

  def delete(self, *args, **kwargs):
    pol_contains = self.politically_contains.all()

    for loc in pol_contains:
      loc.politically_in = None
      loc.save()

    super(PoliticalUnit, self).delete(*args, **kwargs)

class Location(PoliticalUnit):
  geographically_in = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "geographically in", related_name = "geographically_contains")
  politically_in = models.ForeignKey(PoliticalUnit, null = True, blank = True, default = None, verbose_name = "politically in", related_name = "politically_contains")
  full_name = models.CharField(max_length = 200, blank = True)

  # Coding systems
  wb_code = models.CharField("World Bank code", max_length = 3, blank = True, null = True)
  iso_3166_1_letter_code = models.CharField("ISO 3166-1 (letters) code", max_length = 3, blank = True, null = True)
  iso_3166_1_num_code = models.DecimalField("ISO 3166-1 (numbers) code", max_digits = 3, decimal_places = 0, blank = True, null = True)
  iso_3166_2_code = models.CharField("ISO 3166-2 code", max_length = 5, blank = True, null = True)
  polity_num_code = models.DecimalField("Polity (numbers) code", max_digits = 3, decimal_places = 0, blank = True, null = True)
  polity_letter_code = models.CharField("Polity (letters) code", max_length = 3, blank = True, null = True)
  nato_code = models.CharField("NATO code", max_length = 3, blank = True, null = True)
  fips_code = models.CharField("FIPS code", max_length = 2, blank = True, null = True)
  undp_code = models.CharField("UNDP code", max_length = 3, blank = True, null = True)
  ICAO_code = models.CharField("ICAO code", max_length = 2, blank = True, null = True)

  # TODO Spatial characteristics 

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_location', 'Can activate submitted location'),
                    ('merge_location', 'Can activate location entries'),
                    ('convert2polunit', 'Can convert to political unit'), )

  def save(self, *args, **kwargs):
    self.clean()
    super(Location, self).save(*args, **kwargs)

    for loc in self.geographically_contains.all():
      loc.clean()

  def delete(self, *args, **kwargs):
    geo_contains = self.geographically_contains.all()

    for loc in geo_contains:
      loc.geographically_in = None
      loc.save()

    super(Location, self).delete(*args, **kwargs)

  def clean(self):
    if self.geographically_in:
      self.full_name = self.name + ", " + unicode(self.geographically_in)
    else:
      self.full_name = self.name 

  def __unicode__(self): 
    return self.full_name

  def activate(self):
    super(Location, self).activate()

    if self.geographically_in and not self.geographically_in.active:
      self.geographically_in.activate()

    if self.politically_in and not self.politically_in.active:
      self.politically_in.activate()

  """
  def is_root(self):
    return not self.in_location

  def is_terminal(self):
    return Location.objects.filter(in_location = self.pk).count() == 0

  """
  def get_geographic_sub_locations(self, include_self = True, max_distance = None):
    return Location.objects.filter(pk__in = Location.get_location_ids_geographically_in((self,), include_self, max_distance))

  @staticmethod
  def get_location_ids_geographically_in(locations, include_self = True, max_distance = None):
    ids = [str(loc.pk) for loc in locations]
    query = None

    if include_self:
      query = """WITH RECURSIVE in_region(id, distance) AS
             ((SELECT politicalunit_ptr_id, 0 
              FROM common_location
              WHERE politicalunit_ptr_id IN (%s)) UNION
              (SELECT pl.politicalunit_ptr_id, ir.distance + 1
              FROM in_region ir, common_location pl
              WHERE pl.geographically_in_id = ir.id %s))
             SELECT id FROM in_region""" % (','.join(ids), (("and ir.distance < %i" % max_distance) if max_distance else ''))
    else:
      if max_distance and max_distance < 1:
        return []

      query = """WITH RECURSIVE in_region(id, distance) AS
             ((SELECT politicalunit_ptr_id, 1 
              FROM common_location
              WHERE geographically_in_id IN (%s)) UNION
              (SELECT pl.politicalunit_ptr_id, ir.distance + 1
              FROM in_region ir, common_location pl
              WHERE pl.geographically_in_id = ir.id %s))
             SELECT id FROM in_region""" % (','.join(ids), (("and ir.distance < %i" % max_distance) if max_distance else ''))

    cursor = connection.cursor() 
    cursor.execute(query) # TODO capture exception on query failure

    return [lid[0] for lid in cursor.fetchall()]

  def get_geographically_in(self):
    return self.geographically_in

  def get_politically_in(self):
    return self.politically_in

  def merge_into(self, other):
    super(Location, self).merge_into(other)

    # Using a loop because I want save() to be called
    for geo_in in self.geographically_contains.all():
      geo_in.geographically_in = other
      geo_in.save()


  def convert_to_polunit(self):
    new_polunit = PoliticalUnit(name = self.name, active = self.active, submitted_by = self.submitted_by)
    new_polunit.save()

    for old_unit_type in self.unit_type.all():
      new_polunit.unit_type.add(old_unit_type)

    for geo_in in self.geographically_contains.all():
      geo_in.geographically_in = None 
      geo_in.politically_in = new_polunit
      geo_in.save()

    self.population_maindataentry_related.all().update(location = new_polunit)
    self.government_maindataentry_related.all().update(location = new_polunit)
    self.education_maindataentry_related.all().update(location = new_polunit)
    self.infrastructure_maindataentry_related.all().update(location = new_polunit)

    for tbl in self.table_set.all():
      tbl.included_countries.remove(self)
      tbl.included_countries.add(new_polunit)

class TemporalLocation(Location):
  temporal_is = models.ForeignKey(Location, null = False, blank = False, verbose_name = "is", related_name = "temp_locations")
  begin_date = models.DateField("Start Date", null = True, blank = True)
  end_date = models.DateField("End Date", null = True, blank = True)

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_temploc', 'Can activate submitted temporal location'),
                    ('merge_temploc', 'Can merge temporal location entries') )

  def get_geographically_in(self):
    if self.geographically_in:
      return self.geographically_in
    else:
      return self.temporal_is.get_geographically_in()

  def get_politically_in(self):
    if self.politically_in:
      return self.politically_in
    else:
      return self.temporal_is.get_politically_in()

  def activate(self):
    super(TemporalLocation, self).activate()

    if not self.temporal_is.active:
      self.temporal_is.activate()

  def merge_into(self, other):
    super(TemporalLocation, self).merge_into(other)

    self.temp_locations.all().update(temporal_is = other)

class BaseDataEntry(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    ordering = ['location', 'begin_date', ]
    abstract = True

  GENDER_CHOICES = (('U', 'Unspecified'), ('M', 'Male'), ('F', 'Female'))
  UNIT_CHOICES = (('hundreds', 'Hundreds'), 
                  ('thousands', 'Thousands'), 
                  ('millions', 'Millions'), 
                  ('thousand millions', 'Thousand Millions'),
                  ('units', 'Units'))
  VAL_PRECISION_CHOICES = ((0, 'Unspecified'), (1, 'Uncertain'), (2, 'Estimate'))

  # Source info
  #old_source_id = models.IntegerField("Source ID", null = True, blank = True)
  #old_combined_id = models.CharField("Combined ID", max_length = 30)

  primary_source = models.TextField(null = True, blank = True)
  page_num = models.IntegerField("Page Number", null = True, blank = True, default = None)

  source = models.ForeignKey('sources.BaseSourceObject', blank = True, null = True, related_name = "%(app_label)s_%(class)s_related")

  # Date info
  begin_date = models.DateField("Start Date", null = True, blank = True)
  end_date = models.DateField("End Date", null = True, blank = True)
  circa = models.BooleanField(default = False)
  
  # Location info
  #location = models.ForeignKey(Location, related_name = '%(app_label)s_%(class)s_related')
  location = models.ForeignKey(PoliticalUnit, related_name = '%(app_label)s_%(class)s_related')
  original_location_name = models.CharField("Original Location Name", max_length = 50, null = True, blank = True)
  alternate_location_name = models.CharField("Alternate Location Name", max_length = 50, null = True, blank = True)

  is_total = models.BooleanField("Is Total", default = False)

  polity = models.CharField(max_length = 100, null = True, blank = True)
  iso = models.CharField("ISO", max_length = 100, null = True, blank = True) 
  wb = models.CharField("WB", max_length = 100, null = True, blank = True)

  value_unit = models.CharField("Units", max_length = 20, choices = UNIT_CHOICES, default = 'units')

  remarks = models.TextField(null = True, blank = True)

  def __unicode__(self) :
    return "%s (%s - %s)" % (unicode(self.location), self.begin_date, self.end_date)
  
  def activate(self):
    super(BaseDataEntry, self).activate()

    if not self.location.active:
      self.location.activate()

    if self.source and not self.source.active:
      self.source.activate()

# This is an auto-generated Django model module created by ogrinspect.

class BaseGeo(geo_models.Model):
  ft_id = geo_models.IntegerField("FT ID", unique = True)
  point_x = geo_models.FloatField("x")
  point_y = geo_models.FloatField("y")

  srid = 4326

  objects = geo_models.GeoManager()

class GeoPoint(BaseGeo):
  class Meta:
    verbose_name = "geographic point"

  geom = geo_models.PointField(srid=BaseGeo.srid)

class GeoPolygon(BaseGeo):
  class Meta:
    verbose_name = "geographic polygon"

  shape_leng = geo_models.FloatField("length")
  shape_area = geo_models.FloatField("area")
  geom = geo_models.MultiPolygonField(srid=BaseGeo.srid)

# Auto-generated `LayerMapping` dictionary for GeoPoint model
geopoint_mapping = {
    'point_x' : 'POINT_X',
    'point_y' : 'POINT_Y',
    'ft_id' : 'FT_ID',
    'geom' : 'POINT',
}

# Auto-generated `LayerMapping` dictionary for GeoPolygon model
geopolygon_mapping = {
    'shape_leng' : 'SHAPE_Leng',
    'shape_area' : 'SHAPE_Area',
    'point_x' : 'POINT_X',
    'point_y' : 'POINT_Y',
    'ft_id' : 'FT_ID',
    'geom' : 'POLYGON',
}
