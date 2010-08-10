from django.db import models
from django.contrib.auth.models import User

from colonialismdb.common.models import BaseSubmitModel, Category, Language, Location

class SourceType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_sourcetype', 'Can activate source type'),
                    ('merge_sourcetype', 'Can merge source type entries') )

  def merge_into(self, other):
    super(SourceType, self).merge_into(other)

    self.basesourceobject_set.all().update(source_type = other)

  
class SourceSubject(Category):
  class Meta(Category.Meta):
    permissions = ( ('active_sourcesubject', 'Can activate source subject'),
                    ('merge_sourcesubject', 'Can merge source subject entries') )

  def merge_into(self, other):
    super(SourceSubject, self).merge_into(other)

    for bso in self.basesourceobject_set.all():
      bso.subjects.remove(self)
      bso.subjects.add(other)

class DigitizationPriority(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_digipriority', 'Can activate digitization priority'),
                    ('merge_digipriority', 'Can merge digitization priority entries') )

    verbose_name_plural = 'digitization priorities'

  def merge_into(self, other):
    super(DigitizationPriority, self).merge_into(other)

    self.priority_gra_for_source.all().update(digitization_priority_gra = other)
    self.priority_pi_for_source.all().update(digitization_priority_pi = other)

    self.priority_gra_for_table.all().update(digitization_priority_gra = other)
    self.priority_pi_for_table.all().update(digitization_priority_pi = other)

class BaseSourceObject(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    pass

  def activate(self):
    super(Source, self).activate()

    if self.subjects:
      for subject in self.subjects.all():
        if not subject.active:
          subject.activate()

    if self.languages:
      for lang in self.languages.all():
        if not lang.active:
          lang.activate()

    if self.digitization_priority_gra and not self.digitization_priority_gra.active:
      self.digitization_priority_gra.activate()

    if self.digitization_priority_pi and not self.digitization_priority_pi.active:
      self.digitization_priority_pi.activate()

  subjects = models.ManyToManyField(SourceSubject, blank = True)

  source_file = models.FileField(upload_to = 'sources/%Y/%m/%d', blank = True)

  digitization_priority_gra = models.ForeignKey(DigitizationPriority, null = True, blank = True, related_name = 'prority_gra_for_%(class)s')
  digitization_priority_pi = models.ForeignKey(DigitizationPriority, null = True, blank = True, related_name = 'priority_pi_for_%(class)s')
  
  record_date = models.DateField(blank = True, null = True) # auto_now_add = True

  remarks = models.TextField(blank = True)

  url = models.URLField(max_length = 500, verify_exists = True, blank = True)

  languages = models.ManyToManyField(Language)

class Source(BaseSourceObject):
  class Meta(BaseSourceObject.Meta):
    permissions = ( ('activate_source', 'Can active source'), )

  def __unicode__(self):
    if self.volume and len(unicode(self.volume)) > 0:
      return "%s, %s" % (self.title, self.volume)
    elif self.edition and len(unicode(self.edition)) > 0:
      return "%s, %s" % (self.title, self.edition)

    return self.title

  def activate(self):
    super(Source, self).activate()

    if self.source_type and not self.source_type.active:
      self.source_type.activate()

  old_id = models.IntegerField(null = True, blank = True, unique = True) # column to hold old source id from original Access db
  
  author = models.CharField(max_length = 100, blank = True)
  editor = models.CharField(max_length = 100, blank = True)
  title = models.CharField(max_length = 500)
  original_title = models.CharField(max_length = 500, blank = True, null = True)
  year = models.PositiveSmallIntegerField(blank = True, null = True)
  publisher = models.CharField(max_length = 100, blank = True)
  city = models.CharField(max_length = 50, blank = True)
  series = models.CharField(max_length = 100, blank = True)
  volume = models.CharField(max_length = 100, blank = True)
  edition = models.CharField(max_length = 20, blank = True)
  isbn = models.CharField(max_length = 50, blank = True)

  total_pages = models.PositiveIntegerField(blank = True, null = True)
  scanned_size = models.DecimalField(blank = True, null = True, decimal_places = 2, max_digits = 8, help_text = 'Scanned size in MB')

  source_type = models.ForeignKey(SourceType, blank = True, null = True) 
  keywords = models.TextField(blank = True)

  location = models.CharField(max_length = 500, blank = True)

class Table(BaseSourceObject):
  class Meta(BaseSourceObject.Meta):
    permissions = ( ('activate_table', 'Can activate table'), )

  def __unicode__(self):
    return self.name

  def activate(self):
    super(Table, self).activate()

    if not self.source.active:
      self.source.activate()

    if self.included_countries:
      for country in self.included_countries.all():
        if not country.active:
          country.activate()

  old_id = models.IntegerField(null = True, blank = True, unique = True) # column to hold old source id from original Access db

  old_source_id = models.IntegerField(null = True, blank = True) # column to hold old source id from original Access db

  source = models.ForeignKey(Source)

  nr = models.CharField("NR", max_length = 20)

  name = models.CharField(max_length = 500)
  original_name = models.CharField(max_length = 500, blank = True, null = True)

  included_countries = models.ManyToManyField(Location)

  begin_page = models.IntegerField()
  end_page = models.IntegerField()

  begin_year = models.PositiveSmallIntegerField(blank = True, null = True)
  end_year = models.PositiveSmallIntegerField(blank = True, null = True)

  prc = models.CharField(max_length = 100, blank = True, null = True)
