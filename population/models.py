from django.db import models
from colonialismdb.common.models import Location, Religion, Race, Ethnicity, EthnicOrigin, BaseDataEntry, LogEntry

class MainDataEntry(BaseDataEntry):
  UNIT_CHOICES = (('hundreds', 'Hundreds'), ('thousands', 'Thousands'), ('millions', 'Millions'))
  POP_COND_CHOICES = (('None', 'None'), ('Dead', 'Dead'), ('Educated', 'Educated'), ('Enslaved', 'Enslaved'), ('Illiterate', 'Illiterate'), ('Impaired', 'Impaired'))

  class Meta(BaseDataEntry.Meta):
    verbose_name = "Population Data Entry"
    verbose_name_plural = "Population Data Entries"
    #order_with_respect_to = 'location'
    ordering = ['location', 'begin_date', 'end_date']
  
  # TODO separate tables for sources, tables, pages, etc.
  source_id = models.IntegerField("Source ID", null = True, blank = True)
  combined_id = models.CharField("Combined ID", max_length = 30)
  page_num = models.IntegerField("Page Number", null = True, default = None)

  #TODO date data integrity check
  begin_date = models.DateField("Start Date", null = True, blank = True, help_text = "Examples: If data refers to specific day, enter that day (e.g., April 3, 1900) as the begin and end date. If data encompasses a full calendar year enter January 1, 1900 as Begin date and December 31, 1900, as End date.")
  end_date = models.DateField("End Date", null = True, blank = True, help_text = "Examples: If data refers to specific day, enter that day (e.g., April 3, 1900) as the begin and end date. If data encompasses a full calendar year enter January 1, 1900 as Begin date and December 31, 1900, as End date.")

  location = models.ForeignKey(Location, related_name = 'population_data_entries', help_text = "The English name which could be different from the original name in the source")
  original_location_name = models.CharField("Original Location Name", max_length = 50, null = True, blank = True, help_text = "Original name used in the source if different from the English name")
  alternate_location_name = models.CharField("Alternate Location Name", max_length = 50, null = True, blank = True)

  religion = models.ForeignKey(Religion, null = True, default = None)
  race = models.ForeignKey(Race, null = True, default = None)
  ethnicity = models.ForeignKey(Ethnicity, null = True, default = None)
  ethnic_origin = models.ForeignKey(EthnicOrigin, null = True, default = None)
  
  #TODO age data integrity check
  age_start = models.IntegerField("Start Age", default = None, null = True, help_text = "Years old at beginning of age grouping")
  age_end = models.IntegerField("End Age", default = None, null = True, help_text = "Years old at end of age grouping")

  remarks = models.TextField(null = True, blank = True)

  # Link field not used
  
  individuals_population_value = models.DecimalField("Individuals", max_digits = 10, decimal_places = 2, null = True, blank = True)
  families_population_value = models.DecimalField("Families", max_digits = 10, decimal_places = 2, null = True, blank = True)
  male_population_value = models.DecimalField("Male", max_digits = 10, decimal_places = 2, null = True, blank = True)
  female_population_value = models.DecimalField("Female", max_digits = 10, decimal_places = 2, null = True, blank = True)
  
  value_unit = models.CharField("Units", max_length = 15, choices = UNIT_CHOICES, null = True, blank = True)
  is_total = models.BooleanField("Is Total", default = False)
  population_condition = models.CharField("Population Condition", max_length = 20, choices = POP_COND_CHOICES, default = 'None') # TODO separate table

  polity = models.CharField(max_length = 100, null = True, blank = True)
  iso = models.CharField("ISO", max_length = 100, null = True, blank = True) 
  wb = models.CharField("WB", max_length = 100, null = True, blank = True)
  
  def __unicode__(self) :
    return "%s (%s - %s) [%s]" % (self.location, self.begin_date, self.end_date, self.log.status)

  
