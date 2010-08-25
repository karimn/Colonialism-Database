from django.db import models

from colonialismdb.common.models import Location, BaseDataEntry, Category, SpatialAreaUnit, Currency
from colonialismdb.sources.models import BaseSourceObject 

class EducationExpenditureType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_educexpendtype', 'Can activate submitted type'), 
                    ('merge_educexpendtype', 'Can merge occupation type') )

class SchoolType(Category):
  class Meta(Category.Meta):
    permissions = ( ('activate_schooltype', 'Can activate submitted type'), 
                    ('merge_schooltype', 'Can merge occupation type') )
    
class MainDataEntry(BaseDataEntry):
  class Meta(BaseDataEntry.Meta):
    verbose_name = "education data entry"
    verbose_name_plural = "education data entries"
    permissions = ( ('activate_maindataentry', 'Can activate submitted education data entry'), )

  PUB_PRIV_CHOICES = (('public', 'Public'), ('private', 'Private'))
  REL_SEC_CHOICES = (('religious', 'Religious'), ('secular', 'Secular'))
  SCH_GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'), ('both', 'Both'))

  # Should these be moved to location?
  spatial_area = models.IntegerField(null = True, blank = True)
  spatial_area_unit = models.ForeignKey(SpatialAreaUnit, null = True, blank = True, related_name = '%(app_label)s_%(class)s_related')

  currency = models.ForeignKey(Currency, null = True, blank = True, related_name = '%(app_label)s_%(class)s_related')
  currency_exchange_rate = models.IntegerField(null = True, blank = True)

  education_expenditure = models.IntegerField(null = True, blank = True)
  education_expenditure_type = models.ForeignKey(EducationExpenditureType, null = True, blank = True)
  is_total_expenditure = models.BooleanField(default = False)

  num_schools = models.IntegerField("number of schools", null = True, blank = True)
  is_total_schools = models.BooleanField("is total number of schools", default = False)
  school_type = models.ForeignKey(SchoolType, null = True, blank = True)
  pub_priv = models.CharField("public / private", max_length = 10, choices = PUB_PRIV_CHOICES)
  rel_sec = models.CharField("religious / secular", max_length = 10, choices = REL_SEC_CHOICES)

  num_students = models.IntegerField("number of students", null = True, blank = True)
  student_gender = models.CharField(max_length = 10, choices = SCH_GENDER_CHOICES, default = 'both')
  is_total_students = models.BooleanField("is total number of students", default = False)

  num_teachers = models.IntegerField("number of teachers", null = True, blank = True)
  teacher_gender = models.CharField(max_length = 10, choices = SCH_GENDER_CHOICES, default = 'both')
  is_total_teachers = models.BooleanField("is total number of teachers", default = False)

  def activate(self):
    super(MainDataEntry, self).activate()

    if self.spatial_area_unit and not self.spatial_area_unit.active:
      self.spatial_area_unit.activate()

    if self.currency and not self.currency.active:
      self.currency.activate()
      
    if self.education_expenditure_type and not self.education_expenditure_type.active:
      self.education_expenditure_type.activate()

    if self.school_type and not self.school_type.active:
      self.school_type.activate()
