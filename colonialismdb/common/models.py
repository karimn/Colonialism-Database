import datetime

from django.db import models, connection
from django.contrib.auth.models import User

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
  
class BaseDataEntry(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

  UNIT_CHOICES = (('hundreds', 'Hundreds'), ('thousands', 'Thousands'), ('millions', 'Millions'), ('units', 'Units'))

class Category(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

  def __unicode__(self):
    return unicode(self.name)

  name = models.CharField(max_length = 50, unique = True)

class Religion(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_religion', 'Can activate submitted religion'), )

class Race(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_race', 'Can activate submitted race'), )

class Ethnicity(Category):
  class Meta(Category.Meta):
    verbose_name_plural = 'ethnicities'
    permissions = ( ('activate_ethnicity', 'Can activate submitted ethnicity'), )

class EthnicOrigin(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_ethnic_origin', 'Can activate submitted ethnic origin'), )

class PoliticalUnitType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_politicalunittype', 'Can activate submitted political unit type'), )

class PoliticalUnit(BaseSubmitModel):
  name = models.CharField("name", max_length = 50)
  unit_type = models.ManyToManyField(PoliticalUnitType, null = True, blank = True)

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_politicalunit', 'Can activate submitted political unit'), )

  def activate(self):
    super(PoliticalUnit, self).activate()

  def __unicode__(self):
    return self.name

class Location(PoliticalUnit):
  geographically_in = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "geographically in", related_name = "geographically contains")
  politically_in = models.ForeignKey(PoliticalUnit, null = True, blank = True, default = None, verbose_name = "politically in", related_name = "politically contains")

  # TODO Spatial characteristics 

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_location', 'Can activate submitted location'), )

  def __unicode__(self): 
    if self.geographically_in:
      return self.name + ", " + unicode(self.geographically_in)
    else:
      return self.name 

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

class TemporalLocation(Location):
  temporal_is = models.ForeignKey('self', null = False, blank = False, verbose_name = "is")
  begin_date = models.DateField("Start Date", null = True, blank = True)
  end_date = models.DateField("End Date", null = True, blank = True)

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_temporallocation', 'Can activate submitted temporal location'), )

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

  def __unicode__(self): 
    geo = self.get_geographically_in()

    if geo:
      return self.name + " (%s - %s)" % (self.begin_date, self.end_date) + ", " + unicode(self.geo)
    else:
      return self.name + " (%s - %s)" % (self.begin_date, self.end_date)

  def activate(self):
    super(TemporalLocation, self).activate()

    if not self.temporal_is.active:
      self.temporal_is.activate()


