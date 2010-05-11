from django.db import models 

# Create your models here.

class Location(models.Model):
  name = models.CharField("Name", max_length = 50)
  in_location = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "In")
# class Ethnicity(models.Model): #  name = models.CharField(max_length = 50, unique = True)

class MainDataEntry(models.Model):
  RELIGION_CHOICES = ((0, 'None'), (1, 'Christian'), (2, 'Muslim'), (3, 'Jew'))
  RACE_CHOICES = ((0, 'White'), (1, 'Black'))
  ETHNICITY_CHOICES = ((0, 'Indian'), (1, 'Russian')) 
  ETHNIC_ORIGIN_CHOICES = ((0, 'Foreign'), (1, 'Indigenous')) 
  UNIT_CHOICES = ((1, 'Hundreds'), (2, 'Thousands'), (3, 'Millions'))
  POP_COND_CHOICES = ((0, 'None'), (1, 'Dead'), (2, 'Educated'), (3, 'Enslaved'), (4, 'Illiterate'), (5, 'Impaired'))

  class Meta:
    verbose_name = "Population Data Entry"
    verbose_name_plural = "Population Data Entries"
  
  source_id = models.IntegerField("Source ID", null = True, blank = True)
  begin_date = models.DateField("Start Date", null = True, blank = True, help_text = "Examples: If data refers to specific day, enter that day (e.g., April 3, 1900) as the begin and end date. If data encompasses a full calendar year enter January 1, 1900 as Begin date and December 31, 1900, as End date.")
  end_date = models.DateField("End Date", null = True, blank = True, help_text = "Examples: If data refers to specific day, enter that day (e.g., April 3, 1900) as the begin and end date. If data encompasses a full calendar year enter January 1, 1900 as Begin date and December 31, 1900, as End date.")
  location = models.ForeignKey(Location, help_text = "The English name which could be different from the original name in the source")
  original_location_name = models.CharField("Original Location Name", max_length = 50, null = True, blank = True, help_text = "Original name used in the source if different from the English name")
  alternate_location_name = models.CharField("Alternate Location Name", max_length = 50, null = True, blank = True)
  religion = models.IntegerField(choices = RELIGION_CHOICES, null = True, blank = True)
  race = models.IntegerField(choices = RACE_CHOICES, null = True, blank = True)
  ethnicity = models.IntegerField(choices = ETHNICITY_CHOICES, null = True, blank = True)
  ethnic_origin = models.IntegerField("Ethnic Origin", choices = ETHNIC_ORIGIN_CHOICES, null = True, blank = True)
  age_start = models.CharField("Start Age", max_length = 50, default = 'Unknown', help_text = "Years old at beginning of age grouping")
  age_end = models.CharField("End Age", max_length = 50, default = 'Unknown', help_text = "Years old at end of age grouping")
  remarks = models.TextField(null = True, blank = True)
  # TODO Link field
  individuals_population_value = models.IntegerField("Individuals", null = True, blank = True)
  families_population_value = models.IntegerField("Families", null = True, blank = True)
  male_population_value = models.IntegerField("Male", null = True, blank = True)
  female_population_value = models.IntegerField("Female", null = True, blank = True)
  value_unit = models.IntegerField("Units", choices = UNIT_CHOICES, null = True, blank = True)
  is_total = models.BooleanField("Is Total", default = False)
  population_condition = models.IntegerField("Population Condition", choices = POP_COND_CHOICES, default = 0)
  polity = models.CharField(max_length = 100, null = True, blank = True)
  iso = models.CharField("ISO", max_length = 100, null = True, blank = True) 
  wb = models.CharField("WB", max_length = 100, null = True, blank = True)

  
