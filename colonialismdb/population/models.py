from django.db import models

from colonialismdb.common.models import Location, Religion, Race, Ethnicity, EthnicOrigin, BaseDataEntry, Category
from colonialismdb.sources.models import BaseSourceObject 

class PopulationCondition(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_population_condition', 'Can activate submitted population condition'), 
                    ('merge_population_condition', 'Can merge population condition entries') )

class Occupation(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_occupation', 'Can activate submitted occupation'), 
                    ('merge_occupation', 'Can merge occupation entries') )

class MainDataEntry(BaseDataEntry):
  class Meta(BaseDataEntry.Meta):
    verbose_name = "population data entry"
    verbose_name_plural = "population data entries"
    permissions = ( ('activate_main_data_entry', 'Can activate submitted population data entry'), )

  INDIVID_FAM_CHOICES = ((0, 'Individuals'), (1, 'Families'))

  religion = models.ForeignKey(Religion, null = True, blank = True, default = None)
  race = models.ForeignKey(Race, null = True, blank = True, default = None)
  ethnicity = models.ForeignKey(Ethnicity, null = True, blank = True, default = None)
  ethnic_origin = models.ForeignKey(EthnicOrigin, null = True, blank = True, default = None)
  
  #TODO age data integrity check
  age_start = models.IntegerField("Start Age", default = None, null = True, blank = True)
  age_end = models.IntegerField("End Age", default = None, null = True, blank = True)

  # Link field not used

  value_unit = models.CharField("Units", max_length = 15, choices = BaseDataEntry.UNIT_CHOICES, default = 'units')
  individ_fam = models.IntegerField("Individuals / Families", choices = INDIVID_FAM_CHOICES, default = 0)
  population_gender = models.CharField("gender", max_length = 1, choices = BaseDataEntry.GENDER_CHOICES, default = None, null = True)
  population_value = models.DecimalField("value", max_digits = 10, decimal_places = 2) #, null = True, blank = True)
  value_precision = models.IntegerField("level of precision", choices = BaseDataEntry.VAL_PRECISION_CHOICES, default = 0, null = True)
  
  population_condition = models.ForeignKey(PopulationCondition, null = True, blank = True, default = None, verbose_name = 'condition')
  occupation = models.ForeignKey(Occupation, null = True, blank = True, default = None)

  def activate(self):
    super(MainDataEntry, self).activate()

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




  
