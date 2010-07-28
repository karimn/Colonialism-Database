from django.db import models
from django.contrib.auth.models import User

from colonialismdb.common.models import BaseSubmitModel, Category, Language, Location

class SourceType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_sourcetype', 'Can activate source type'), )
  
class SourceSubject(Category):
  class Meta(Category.Meta):
    permissions = ( ('active_sourcesubject', 'Can activate source subject'), )

class DigitizationPriority(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_digipriority', 'Can activate digitization priority'), )
    verbose_name_plural = 'digitization priorities'

class Source(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_source', 'Can active source'), )

  old_id = models.IntegerField(null = True, blank = True) # column to hold old source id from original Access db
  
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

  total_pages = models.PositiveIntegerField(blank = True)
  scanned_size = models.DecimalField(blank = True, null = True, decimal_places = 2, max_digits = 8, help_text = 'Scanned size in MB')

  written_language1 = models.ForeignKey(Language, null = True, blank = True, related_name = 'written_lang1_for_source') 
  written_language2 = models.ForeignKey(Language, null = True, blank = True, related_name = 'written_lang2_for_source')  

  source_type = models.ForeignKey(SourceType, blank = True, null = True) 
  subjects = models.ManyToManyField(SourceSubject, blank = True)
  keywords = models.TextField(blank = True)

  location = models.CharField(max_length = 500, blank = True)
  url = models.URLField(verify_exists = False, blank = True)
  
  source_file = models.FileField(upload_to = 'sources/%Y/%m/%d', blank = True)

  remarks = models.TextField(blank = True)

  # Curator would the user who submitted this row

  digitization_priority_gra = models.ForeignKey(DigitizationPriority, null = True, blank = True, related_name = 'prority_gra_for_sources')
  digitization_priority_pi = models.ForeignKey(DigitizationPriority, null = True, blank = True, related_name = 'priority_pi_for_sources')
  
  record_date = models.DateField(blank = True, null = True)

class Table(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_table', 'Can activate table'), )

  old_id = models.IntegerField(null = True, blank = True)
  old_source_id = models.IntegerField(null = True, blank = True) # column to hold old source id from original Access db

  source = models.ForeignKey(Source)

  nr = models.CharField("NR", max_length = 20)

  name = models.CharField(max_length = 500)
  original_name = models.CharField(max_length = 500, blank = True, null = True)
  original_language = models.ForeignKey(Language, blank = True, null = True)

  subjects = models.ManyToManyField(SourceSubject, blank = True)
  included_countries = models.ManyToManyField(Location)

  begin_page = models.IntegerField()
  end_page = models.IntegerField()

  begin_year = models.PositiveSmallIntegerField(blank = True, null = True)
  end_year = models.PositiveSmallIntegerField(blank = True, null = True)

  prc = models.CharField(max_length = 100, blank = True, null = True)

  # Curator is the "submitted_by" user

  url = models.URLField(max_length = 500, verify_exists = True, blank = True)
  source_file = models.FileField(upload_to = 'sources/%Y/%m/%d', blank = True)

  remarks = models.TextField(blank = True) 

  digitization_priority_gra = models.ForeignKey(DigitizationPriority, null = True, blank = True, related_name = 'prority_gra_for_tables')
  digitization_priority_pi = models.ForeignKey(DigitizationPriority, null = True, blank = True, related_name = 'priority_pi_for_tables')

  record_date = models.DateField(blank = True, null = True)
