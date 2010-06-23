from django.db import models
from colonialismdb.common.models import Location, Religion, Race, Ethnicity, EthnicOrigin, BaseDataEntry

class MainDataEntry(BaseDataEntry):
  UNIT_CHOICES = (('hundreds', 'Hundreds'), ('thousands', 'Thousands'), ('millions', 'Millions'))
  POP_COND_CHOICES = (('None', 'None'), ('Dead', 'Dead'), ('Educated', 'Educated'), ('Enslaved', 'Enslaved'), ('Illiterate', 'Illiterate'), ('Impaired', 'Impaired'))

  class Meta(BaseDataEntry.Meta):
    verbose_name = "population data entry"
    verbose_name_plural = "population data entries"
    ordering = ['location', 'begin_date', ]
    permissions = ( ('activate_main_data_entry', 'Can activate submitted population data entry'), )
  
  # TODO separate tables for sources, tables, pages, etc.
  source_id = models.IntegerField("Source ID", null = True, blank = True)
  combined_id = models.CharField("Combined ID", max_length = 30)
  page_num = models.IntegerField("Page Number", null = True, blank = True, default = None)

  #TODO date data integrity check
  begin_date = models.DateField("Start Date", null = True, blank = True)
  end_date = models.DateField("End Date", null = True, blank = True)

  location = models.ForeignKey(Location, related_name = 'population_data_entries')
  original_location_name = models.CharField("Original Location Name", max_length = 50, null = True, blank = True)
  alternate_location_name = models.CharField("Alternate Location Name", max_length = 50, null = True, blank = True)

  religion = models.ForeignKey(Religion, null = True, blank = True, default = None)
  race = models.ForeignKey(Race, null = True, blank = True, default = None)
  ethnicity = models.ForeignKey(Ethnicity, null = True, blank = True, default = None)
  ethnic_origin = models.ForeignKey(EthnicOrigin, null = True, blank = True, default = None)
  
  #TODO age data integrity check
  age_start = models.IntegerField("Start Age", default = None, null = True, blank = True)
  age_end = models.IntegerField("End Age", default = None, null = True, blank = True)

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
    return "%s (%s - %s)" % (unicode(self.location), self.begin_date, self.end_date)

  def activate(self):
    super(MainDataEntry, self).activate()

    if not self.location.active:
      self.location.activate()

    if self.race and not self.race.active:
      self.race.activate()

    if self.religion and not self.religion.active:
      self.religion.activate()
    
    if self.ethnicity and not self.ethnicity.active:
      self.ethnicity.activate()
      
    if self.ethnic_origin and not self.ethnic_origin.active:
      self.ethnic_origin.activate()




  
