from django.db import models, connection

# Create your models here.

class Location(models.Model):
  name = models.CharField("Name", max_length = 50)
  in_location = models.ForeignKey('self', null = True, blank = True, default = None, verbose_name = "In")

  def __unicode__(self): 
    if self.in_location:
      return self.name + ", " + unicode(self.in_location)
    else:
      return self.name 

  @staticmethod
  def get_location_ids_in(locations):
    ids = [str(loc.pk) for loc in locations]

    query = """WITH RECURSIVE in_region(id) AS
           ((SELECT id 
            FROM population_location
            WHERE id IN (%s)) UNION
            (SELECT pl.id
            FROM in_region ir, population_location pl
            WHERE pl.in_location_id = ir.id))
           SELECT id FROM in_region""" % ','.join(ids)

    cursor = connection.cursor() 
    cursor.execute(query) # TODO capture exception on query failure

    return [lid[0] for lid in cursor.fetchall()]

class MainDataEntry(models.Model):
  RELIGION_CHOICES = ((0, 'None'), (1, 'Christian'), (2, 'Muslim'), (3, 'Jew'))
  RACE_CHOICES = (('Whites', 'White'), ('Negroes', 'Black'))
  ETHNICITY_CHOICES = ((0, 'Indian'), (1, 'Russian')) 
  ETHNIC_ORIGIN_CHOICES = ((0, 'Foreign'), (1, 'Indigenous')) 
  UNIT_CHOICES = (('hundreds', 'Hundreds'), ('thousands', 'Thousands'), ('millions', 'Millions'))
  POP_COND_CHOICES = ((0, 'None'), (1, 'Dead'), (2, 'Educated'), (3, 'Enslaved'), (4, 'Illiterate'), (5, 'Impaired'))

  class Meta:
    verbose_name = "Population Data Entry"
    verbose_name_plural = "Population Data Entries"
    ordering = ['begin_date', 'end_date']
  
  source_id = models.IntegerField("Source ID", null = True, blank = True)
  begin_date = models.DateField("Start Date", null = True, blank = True, help_text = "Examples: If data refers to specific day, enter that day (e.g., April 3, 1900) as the begin and end date. If data encompasses a full calendar year enter January 1, 1900 as Begin date and December 31, 1900, as End date.")
  end_date = models.DateField("End Date", null = True, blank = True, help_text = "Examples: If data refers to specific day, enter that day (e.g., April 3, 1900) as the begin and end date. If data encompasses a full calendar year enter January 1, 1900 as Begin date and December 31, 1900, as End date.")
  location = models.ForeignKey(Location, help_text = "The English name which could be different from the original name in the source")
  original_location_name = models.CharField("Original Location Name", max_length = 50, null = True, blank = True, help_text = "Original name used in the source if different from the English name")
  alternate_location_name = models.CharField("Alternate Location Name", max_length = 50, null = True, blank = True)
  religion = models.IntegerField(choices = RELIGION_CHOICES, null = True, blank = True)
  race = models.CharField(max_length = 15, choices = RACE_CHOICES, null = True, blank = True)
  ethnicity = models.IntegerField(choices = ETHNICITY_CHOICES, null = True, blank = True)
  ethnic_origin = models.IntegerField("Ethnic Origin", choices = ETHNIC_ORIGIN_CHOICES, null = True, blank = True)
  age_start = models.CharField("Start Age", max_length = 50, default = 'Unknown', help_text = "Years old at beginning of age grouping")
  age_end = models.CharField("End Age", max_length = 50, default = 'Unknown', help_text = "Years old at end of age grouping")
  remarks = models.TextField(null = True, blank = True)
  # TODO Link field
  individuals_population_value = models.DecimalField("Individuals", max_digits = 10, decimal_places = 2, null = True, blank = True)
  families_population_value = models.DecimalField("Families", max_digits = 10, decimal_places = 2, null = True, blank = True)
  male_population_value = models.DecimalField("Male", max_digits = 10, decimal_places = 2, null = True, blank = True)
  female_population_value = models.DecimalField("Female", max_digits = 10, decimal_places = 2, null = True, blank = True)
  value_unit = models.CharField("Units", max_length = 15, choices = UNIT_CHOICES, null = True, blank = True)
  is_total = models.BooleanField("Is Total", default = False)
  population_condition = models.IntegerField("Population Condition", choices = POP_COND_CHOICES, default = 0)
  polity = models.CharField(max_length = 100, null = True, blank = True)
  iso = models.CharField("ISO", max_length = 100, null = True, blank = True) 
  wb = models.CharField("WB", max_length = 100, null = True, blank = True)

  def __unicode__(self) :
    return "%s (%s - %s)" % (self.location, self.begin_date, self.end_date)

  
