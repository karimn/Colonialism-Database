import datetime

from django.db import models, connection

class Location(models.Model):
  name = models.CharField("Name", max_length = 50)
  in_location = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "In")

  #class Meta:
    #order_with_respect_to = 'in_location'

  def __unicode__(self): 
    if self.in_location:
      return self.name + ", " + unicode(self.in_location)
    else:
      return self.name 

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

class Religion(models.Model):
  def __unicode__(self):
    return self.name

  name = models.CharField(max_length = 50, unique = True)

class Race(models.Model):
  def __unicode__(self):
    return self.name

  name = models.CharField(max_length = 50, unique = True)

class Ethnicity(models.Model):
  def __unicode__(self):
    return self.name

  class Meta:
    verbose_name_plural = 'Ethnicities'

  name = models.CharField(max_length = 50, unique = True)

class EthnicOrigin(models.Model):
  def __unicode__(self):
    return self.name

  name = models.CharField(max_length = 50, unique = True)

class LogEntry(models.Model):
  STATUS_CHOICES = ((0, 'Inactive'), (1, 'Active'), (2, 'Deleted'))
  CHANGE_CHOICES = ((0, 'Addition'), (1, 'Activation'), (2, 'Deletion'), (3, 'Modification'), (4, 'Migration'))

  class Meta:
    verbose_name_plural = 'LogEntries'

  def __unicode__(self):
    return 'Status: %s, Change: %s' % (self.satus, self.change)

  status = models.IntegerField(choices = STATUS_CHOICES, default = 0)
  change = models.IntegerField(choices = CHANGE_CHOICES)

  remarks = models.TextField(null = True)

  # TODO user
  datetime = models.DateTimeField('Date/Time', initial = datetime.datetime.now)

  previous = models.ForeignKey('self', null = True, default = None)
