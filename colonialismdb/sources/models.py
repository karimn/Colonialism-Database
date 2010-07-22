from django.db import models
from django.contrib.auth.models import User

from colonialismdb.common.models import BaseSubmitModel, Category

class SourceType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_sourcetype', 'Can activate source type'), )
  
class SourceSubject(Category):
  class Meta(Category.Meta):
    permissions = ( ('active_sourcesubject', 'Can activate source subject'), )

class DigitizationPriority(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_digipriority', 'Can activate digitization priority'), )

class Language(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_language', 'Can activate source language'), )

class Source(BaseSubmitModel):
  class Meta(BaseSubmitModel.Meta):
    permissions = ( ('activate_source', 'Can active source'), )

  old_id = models.IntegerField(null = True, blank = True) # column to hold old source id from original Access db
  
  author = models.CharField(max_length = 100, blank = True)
  editor = models.CharField(max_length = 100, blank = True)

  title = models.CharField(max_length = 100)
  original_title = models.CharField(max_length = 100, blank = True, null = True)
  year = models.PositiveSmallIntegerField(blank = True)
  publisher = models.CharField(max_length = 100, blank = True)
  city = models.CharField(max_length = 50, blank = True)
  series = models.CharField(max_length = 100, blank = True)
  volume = models.CharField(max_length = 100, blank = True)
  edition = models.CharField(max_length = 20, blank = True)
  isbn = models.CharField(max_length = 50, blank = True)

  total_pages = models.PositiveIntegerField(blank = True)
  scanned_size = models.DecimalField(blank = True, decimal_places = 2, help_text = 'Scanned size in MB')

  written_language1 = models.ForeignKey(Language, blank = True, related_name = 'written_lang1_for_source') 
  written_language2 = models.ForeignKey(Language, blank = True, related_name = 'written_lang2_for_source')  

  source_type = models.ForeignKey(SourceType, blank = True) 
  subject = models.ForeignKey(SourceSubject, blank = True)
  keywords = models.TextField(blank = True)

  location = models.CharField(max_length = 100, blank = True)
  url = models.URLField(verify_exists = False, blank = True)
  
  source_file = models.FileField(upload_to = 'sources/%Y/%m/%d', blank = True)

  remarks = models.TextField(blank = True)

  # Curator would the user who submitted this row

  digitization_priority_gra = models.ForeignKey(DigitizationPriority, blank = True, related_name = 'prority_gra_for')
  digitization_priority_pi = models.ForeignKey(DigitizationPriority, blank = True, related_name = 'priority_pi_for')
  
  record_date = models.DateField(blank = True)

