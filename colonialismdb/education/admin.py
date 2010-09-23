from colonialismdb.education.models import MainDataEntry, EducationExpenditureType, SchoolType
from colonialismdb.common.models import SpatialAreaUnit, Currency
from colonialismdb.sources.models import Table
from colonialismdb.common.admin import BaseSubmitAdmin, BaseMergeableCategoryAdmin, BaseMainDataEntryAdmin
from django.contrib import admin

class MainDataEntryAdmin(BaseMainDataEntryAdmin) :
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by', 'datetime_created', ]}),

      ('Location Information', 
        {'fields' : ['location', 'original_location_name', 'alternate_location_name', 'spatial_area', 'spatial_area_unit']}),
      
      ('Date Range', 
        {'fields' : ['begin_date', 'end_date', 'circa']}),

      ('Currency',
        {'fields' : ['currency', 'currency_exchange_rate']}),

      ('Education Expenditure',
        {'fields' : ['education_expenditure', 'education_expenditure_type', 'is_total_expenditure']}),

      ('Schools',
        {'fields' : ['num_schools', 'is_total_schools', 'school_type', 'pub_priv', 'rel_sec']}),

      ('Students',
        {'fields' : ['num_students', 'student_gender', 'is_total_students']}),

      ('Teachers',
        {'fields' : ['num_teachers', 'teacher_gender', 'is_total_teachers']}),

      ('Source Information', 
        {'fields' : ['source', 'page_num', 'primary_source', 'polity', 'iso', 'wb']}),

      ('Other Information', 
        {'fields' : ['remarks', ]}),
  ]

  #radio_fields = { 'value_precision' : admin.HORIZONTAL, 'individ_fam' : admin.HORIZONTAL, 'population_gender' : admin.HORIZONTAL, 'value_unit' : admin.HORIZONTAL, }

  activate_perm = 'education.activate_maindataentry'

class EducationExpenditureTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'education.activate_educexpendtype'
    merge_perm = 'education.merge_educexpendtype'
    
class SchoolTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'education.activate_schooltype'
    merge_perm = 'education.merge_schooltype'

admin.site.register(MainDataEntry, MainDataEntryAdmin)
admin.site.register(EducationExpenditureType, EducationExpenditureTypeAdmin)
admin.site.register(SchoolType, SchoolTypeAdmin)
