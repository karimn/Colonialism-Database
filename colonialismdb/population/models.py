from django.db import models

from colonialismdb.common.models import Location, Religion, Race, Ethnicity, EthnicOrigin, BaseDataEntry, Category
from colonialismdb.sources.models import BaseSourceObject 

class PopulationCondition(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_population_condition', 'Can activate submitted population condition'), )

class Occupation(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_occupation', 'Can activate submitted occupation'), )

class MainDataEntry(BaseDataEntry):
  class Meta(BaseDataEntry.Meta):
    verbose_name = "data entry"
    verbose_name_plural = "data entries"
    ordering = ['location', 'begin_date', ]
    permissions = ( ('activate_main_data_entry', 'Can activate submitted population data entry'), )

  GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
  INDIVID_FAM_CHOICES = ((0, 'Individuals'), (1, 'Families'))
  VAL_PRECISION_CHOICES = ((0, 'Exact'), (1, 'Uncertain'), (2, 'Estimate'))
  
  # TODO separate tables for sources, tables, pages, etc.
  old_source_id = models.IntegerField("Source ID", null = True, blank = True)
  old_combined_id = models.CharField("Combined ID", max_length = 30)
  page_num = models.IntegerField("Page Number", null = True, blank = True, default = None)

  source = models.ForeignKey(BaseSourceObject, blank = True, null = True)

  #TODO date data integrity check
  begin_date = models.DateField("Start Date", null = True, blank = True)
  end_date = models.DateField("End Date", null = True, blank = True)
  circa = models.BooleanField(default = False)

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

  is_total = models.BooleanField("Is Total", default = False)
  value_unit = models.CharField("Units", max_length = 15, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  individ_fam = models.IntegerField("Individuals/Families", choices = INDIVID_FAM_CHOICES)
  population_gender = models.CharField(max_length = 1, choices = GENDER_CHOICES, default = None, null = True)
  population_value = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
  value_precision = models.IntegerField(choices = VAL_PRECISION_CHOICES, default = 0, null = True)
  
  population_condition = models.ForeignKey(PopulationCondition, null = True, blank = True, default = None)
  occupation = models.ForeignKey(Occupation, null = True, blank = True, default = None)

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

    if self.population_condition and not self.population_condition.active:
      self.population_condition.activate()




  
