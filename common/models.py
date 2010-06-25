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
  submitted_by = models.ForeignKey(User, related_name = "submitted_%(app_label)s_%(class)s")
  
class BaseDataEntry(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

  UNIT_CHOICES = (('hundreds', 'Hundreds'), ('thousands', 'Thousands'), ('millions', 'Millions'), ('units', 'Units'))

class Location(BaseSubmitModel):
  name = models.CharField("Name", max_length = 50)
  in_location = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "In")

  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_location', 'Can activate submitted location'), )

  def __unicode__(self): 
    if self.in_location:
      return self.name + ", " + unicode(self.in_location)
    else:
      return self.name 

  def activate(self):
    super(Location, self).activate()

    if self.in_location and not self.in_location.active:
      self.in_location.activate()

  def is_root(self):
    return not self.in_location

  def is_terminal(self):
    return Location.objects.filter(in_location = self.pk).count() == 0

  def get_sub_locations(self, include_self = True, max_distance = None):
    return Location.objects.filter(pk__in = Location.get_location_ids_in((self,), include_self, max_distance))

  @staticmethod
  def get_location_ids_in(locations, include_self = True, max_distance = None):
    ids = [str(loc.pk) for loc in locations]
    query = None

    if include_self:
      query = """WITH RECURSIVE in_region(id, distance) AS
             ((SELECT id, 0 
              FROM common_location
              WHERE id IN (%s)) UNION
              (SELECT pl.id, ir.distance + 1
              FROM in_region ir, common_location pl
              WHERE pl.in_location_id = ir.id %s))
             SELECT id FROM in_region""" % (','.join(ids), (("and ir.distance < %i" % max_distance) if max_distance else ''))
    else:
      if max_distance and max_distance < 1:
        return []

      query = """WITH RECURSIVE in_region(id, distance) AS
             ((SELECT id, 1 
              FROM common_location
              WHERE in_location_id IN (%s)) UNION
              (SELECT pl.id, ir.distance + 1
              FROM in_region ir, common_location pl
              WHERE pl.in_location_id = ir.id %s))
             SELECT id FROM in_region""" % (','.join(ids), (("and ir.distance < %i" % max_distance) if max_distance else ''))


    cursor = connection.cursor() 
    cursor.execute(query) # TODO capture exception on query failure

    return [lid[0] for lid in cursor.fetchall()]

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


