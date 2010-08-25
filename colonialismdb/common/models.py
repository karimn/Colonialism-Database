import datetime

from django.db import models, connection
from django.contrib.auth.models import User

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
  submitted_by = models.ForeignKey(User, null = True, related_name = "submitted_%(app_label)s_%(class)s")

class Category(BaseSubmitModel, MergeableModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

  def __unicode__(self):
    return unicode(self.name)

  def merge_into(self, other):
    super(Category, self).merge_into(other)

  name = models.CharField(max_length = 100, unique = True)

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

class PoliticalUnit(BaseSubmitModel,MergeableModel):
  name = models.CharField("name", max_length = 150)
  unit_type = models.ManyToManyField(PoliticalUnitType, null = True, blank = True)

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_politicalunit', 'Can activate submitted political unit'),
                    ('merge_politicalunit', 'Can merge political unit entries') )

  def activate(self):
    super(PoliticalUnit, self).activate()

  def __unicode__(self):
    return self.name

  def merge_into(self, other):
    super(PoliticalUnit, self).merge_into(other)

    self.politically_contains.all().update(politically_in = other)

class Location(PoliticalUnit):
  geographically_in = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "geographically in", related_name = "geographically_contains")
  politically_in = models.ForeignKey(PoliticalUnit, null = True, blank = True, default = None, verbose_name = "politically in", related_name = "politically_contains")
  full_name = models.CharField(max_length = 200, blank = True)

  # TODO Spatial characteristics 

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_location', 'Can activate submitted location'),
                    ('merge_location', 'Can activate location entries') )

  def save(self, *args, **kwargs):
    self.clean()
    super(Location, self).save(*args, **kwargs)

    for loc in self.geographically_contains.all():
      loc.clean()

  def delete(self, *args, **kwargs):
    geo_contains = self.geographically_contains.all()

    super(Location, self).delete(*args, **kwargs)

    for loc in geo_contains:
      loc.geographically_in = None
      loc.save()

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

    self.geographically_contains.all().update(geographically_in = other)

    self.population_maindataentry_related.all().update(location = other)
    self.government_maindataentry_related.all().update(location = other)

    for tbl in self.table_set.all():
      tbl.included_countries.remove(self)
      tbl.included_countries.add(other)

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

  """
  def __unicode__(self): 
    geo = self.get_geographically_in()

    if geo:
      return self.name + " (%s - %s)" % (self.begin_date, self.end_date) + ", " + unicode(self.geo)
    else:
      return self.name + " (%s - %s)" % (self.begin_date, self.end_date)
  """

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

  GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
  UNIT_CHOICES = (('hundreds', 'Hundreds'), ('thousands', 'Thousands'), ('millions', 'Millions'), ('units', 'Units'))
  VAL_PRECISION_CHOICES = ((0, 'Unspecified'), (1, 'Uncertain'), (2, 'Estimate'))

  # Source info
  old_source_id = models.IntegerField("Source ID", null = True, blank = True)
  old_combined_id = models.CharField("Combined ID", max_length = 30)

  primary_source = models.TextField(null = True, blank = True)
  page_num = models.IntegerField("Page Number", null = True, blank = True, default = None)

  source = models.ForeignKey('sources.BaseSourceObject', blank = True, null = True, related_name = "%(app_label)s_%(class)s_related")

  # Date info
  begin_date = models.DateField("Start Date", null = True, blank = True)
  end_date = models.DateField("End Date", null = True, blank = True)
  circa = models.BooleanField(default = False)
  
  # Location info
  location = models.ForeignKey(Location, related_name = '%(app_label)s_%(class)s_related')
  original_location_name = models.CharField("Original Location Name", max_length = 50, null = True, blank = True)
  alternate_location_name = models.CharField("Alternate Location Name", max_length = 50, null = True, blank = True)

  is_total = models.BooleanField("Is Total", default = False)

  polity = models.CharField(max_length = 100, null = True, blank = True)
  iso = models.CharField("ISO", max_length = 100, null = True, blank = True) 
  wb = models.CharField("WB", max_length = 100, null = True, blank = True)

  value_unit = models.CharField("Units", max_length = 15, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')

  remarks = models.TextField(null = True, blank = True)

  def __unicode__(self) :
    return "%s (%s - %s)" % (unicode(self.location), self.begin_date, self.end_date)
  
  def activate(self):
    super(BaseDataEntry, self).activate()

    if not self.location.active:
      self.location.activate()
