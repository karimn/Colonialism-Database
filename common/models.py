import datetime

from django.db import models, connection
from django.contrib.auth.models import User

class LogEntry(models.Model):
  STATUS_CHOICES = ((0, 'Inactive'), (1, 'Active'), (2, 'Deleted'))
  CHANGE_CHOICES = ((0, 'Addition'), (1, 'Activation'), (2, 'Deletion'), (3, 'Modification'), (4, 'Migration'))

  class Meta:
    verbose_name_plural = 'LogEntries'

  def __unicode__(self):
    return 'Status: %s, Change: %s, User: %s' % (self.status, self.change, self.user)

  status = models.IntegerField(choices = STATUS_CHOICES, default = 0)
  change = models.IntegerField(choices = CHANGE_CHOICES)

  remarks = models.TextField(null = True)

  user = models.ForeignKey(User, related_name = 'logs')

  datetime = models.DateTimeField('Date/Time', default = datetime.datetime.now)

  previous = models.ForeignKey('self', null = True, default = None)

class BaseSubmitModel(models.Model):
  class Meta:
    abstract = True

    permissions = (
        ('submit_new', 'Can enter new data to be reviewed'),
        ('active_new', 'Can accept newly submitted data'),
    )

  log = models.ForeignKey(LogEntry)

class BaseDataEntry(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

class Location(BaseSubmitModel):
  name = models.CharField("Name", max_length = 50)
  in_location = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "In")

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

class Category(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    abstract = True

  def __unicode__(self):
    return self.name
  
  name = models.CharField(max_length = 50, unique = True)

class Religion(Category):
  pass

class Race(Category):
  pass

class Ethnicity(Category):
  class Meta(Category.Meta):
    verbose_name_plural = 'Ethnicities'

class EthnicOrigin(Category):
  pass


