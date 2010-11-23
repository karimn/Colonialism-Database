from colonialismdb.common import models
from colonialismdb.common import widgets

from django.contrib import admin, messages
from django.contrib.gis import admin as geo_admin
from reversion.admin import VersionAdmin
from reversion import revision
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.db import transaction

import reversion

class BaseVersionAdmin(VersionAdmin):
  autocomplete_fields = None

  def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    if self.autocomplete_fields and db_field.name in self.autocomplete_fields.keys():
      autocomplete_val = self.autocomplete_fields[db_field.name]
      if len(autocomplete_val) > 1:
        kwargs['widget'] = widgets.AutocompleteAdminWidget(db_field.rel, autocomplete_val[0], autocomplete_val[1]) 
      else:
        kwargs['widget'] = widgets.AutocompleteAdminWidget(db_field.rel, autocomplete_val[0]) 
      return db_field.formfield(**kwargs)
    else:
      return super(BaseVersionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class BaseSubmit:
  readonly_fields = ('active', 'submitted_by', 'datetime_created', )

class BaseSubmitInline(BaseSubmit):
  max_num = 0 # This is to prevent additions

class BaseSubmitStackedInline(BaseSubmitInline, admin.StackedInline):
  def queryset(self, request):
    qs = super(BaseSubmitStackedInline, self).queryset(request)

    if not request.user.has_perm(self.__class__.activate_perm):
      qs = qs.filter(submitted_by = request.user)

    return qs

class BaseSubmitTabularInline(BaseSubmitInline, admin.TabularInline):
  def queryset(self, request):
    qs = super(BaseSubmitTabularInline, self).queryset(request)

    if not request.user.has_perm(self.__class__.activate_perm):
      qs = qs.filter(submitted_by = request.user)

    return qs

class BaseSubmitAdmin(BaseSubmit, BaseVersionAdmin) :
  @revision.create_on_success
  def save_model(self, request, obj, form, change):
    if not change and obj.active == False:
      obj.submitted_by = request.user
      obj.save()
      revision.user = request.user
      revision.comment = "Submitted new data"
    else:
      obj.save()

  def queryset(self, request):
    qs = super(BaseSubmitAdmin, self).queryset(request)

    if not request.user.has_perm(self.__class__.activate_perm):
      qs = qs.filter(submitted_by = request.user)

    return qs

  @revision.create_on_success
  def activate(self, request, query_set):
    """ 
    We should have a concurrency problem here if more than one person are trying to activate entries at the same time.  
    We could use "SELECT FOR UPDATE ..." or the django-locking module, but I would rather wait for 
    http://code.djangoproject.com/ticket/2705 to be integrated into Django.
    """
    rows_activated = 0

    for entry in query_set:
      entry.activate()
      revision.user = request.user
      revision.comment = "Activation"

    if rows_activated > 0:
      message.info(request, '%i %s activated' % (rows_activated, 'entry' if rows_activated == 1 else 'entries'))
      #self.message_user(request, '%i %s activated' % (rows_activated, 'entry' if rows_activated == 1 else 'entries'))

  activate.short_description = 'Activate'

  def get_actions(self, request):
    actions = super(BaseSubmitAdmin, self).get_actions(request)
    
    if not request.user.has_perm(self.__class__.activate_perm):
      del actions['activate']

    return actions

  def save_formset(self, request, form, formset, change):
    if issubclass(formset.model, models.BaseSubmitModel):
        instances = formset.save(commit = False)

        for inst in instances:
          with reversion.revision:
            if not inst.submitted_by:
              inst.submitted_by = request.user
              
            inst.save()
            revision.user = request.user
            revision.comment = 'Submitted new data'

        formset.save_m2m()
    else:
      formset.save()

  actions = ('activate', )
  list_filter = ('active', 'submitted_by')

class BaseMainDataEntryAdmin(BaseSubmitAdmin):
  autocomplete_fields = { 'location' : ('name', 'autocomplete_label'), 'source' : ('name', ), 'primary_source_obj' : ('name', )}
  list_display = ('location', 'begin_date', 'end_date', 'active', 'submitted_by', 'datetime_created', )
  search_fields = ['location__name',]
  ordering = ('-datetime_created', )
  reuse_fields = ('source', 'location', 'begin_date', 'end_date', 'page_num', 'primary_source_text', 'primary_source_obj', 'remarks', )

  def change_view(self, request, object_id, extra_context=None):
    result = super(BaseMainDataEntryAdmin, self).change_view(request, object_id, extra_context)

    if (request.method == 'POST') and request.POST.has_key('_addanother'):
      request.session['reuse_values'] = dict(zip(self.reuse_fields, [request.POST[f] for f in self.reuse_fields]))

    return result

  def add_view(self, request, form_url = '', extra_context=None):
    if (request.method == 'GET') and request.session.has_key('reuse_values'):
      request.GET = request.GET.copy()
      request.GET.update(request.session['reuse_values'])
      del request.session['reuse_values']
    elif request.POST.has_key('_addanother'):
      request.session['reuse_values'] = dict(zip(self.reuse_fields, [request.POST[f] for f in self.reuse_fields]))

    result = super(BaseMainDataEntryAdmin, self).add_view(request, form_url, extra_context)

    return result


class MergeModelChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return "%s (%i)" % (unicode(obj), obj.pk)

class MergeSelectedForm(forms.Form):
  merge_into = MergeModelChoiceField(queryset = models.Location.objects.all(), empty_label = None)
  ct = forms.IntegerField(widget = forms.HiddenInput)
  ids = forms.CharField(widget = forms.HiddenInput)

def merge(merge_into, to_merge, user):
  rows_merged = 0

  for merge in to_merge:
    with reversion.revision:
      merge.merge_into(merge_into)
      revision.user = user
      revision.comment = "Merged into %s" % merge_into
    rows_merged += 1

  for merge in to_merge:
    with reversion.revision:
      merge.delete()
      revision.user = user
      revision.comment = "Deleted after merging"

  with reversion.revision:
    merge_into.save()
    revision.user = user
    revision.comment = "%i entries merged into this entry" % rows_merged

  return rows_merged

@transaction.commit_manually
def merge_selected(request):
  if request.method == "POST":
    """ 
    We should have a concurrency problem here if more than one person are trying to activate entries at the same time.  
    We could use "SELECT FOR UPDATE ..." or the django-locking module, but I would rather wait for 
    http://code.djangoproject.com/ticket/2705 to be integrated into Django.
    """
    form = MergeSelectedForm(request.POST)

    if True: #form.is_valid(): # Not relying on this because the form will not be valid for any models other than Location because it is the one
                               # used in the queryset argument of the ModelChoiceField.  I will rely instead on the POST values
      rows_merged = 0

      ct = ContentType.objects.get(pk = int(request.POST['ct']))
      ids = [int(objid) for objid in request.POST['ids'].split(',')]
      merge_into_pk = int(request.POST['merge_into'])

      #merge_into = form.cleaned_data['merge_into']
      merge_into = ct.model_class().objects.get(id = merge_into_pk)

      to_merge = ct.model_class().objects.filter(id__in = ids).exclude(id = merge_into.pk)

      try:
        rows_merged = merge(merge_into, to_merge, request.user)
      except models.LockedRowError:
        transaction.rollback()
        message.error(request, "One or more of the selected entries to merged is locked")
      else:
        transaction.commit()
        messages.info(request, "%i entries successfully merged" % rows_merged)

    return HttpResponseRedirect('/admin/%s/%s' % (ct.app_label, ct.model))
  else:
    ct = ContentType.objects.get(pk = int(request.GET['ct']))
    ids = [int(objid) for objid in request.GET['ids'].split(',')]
    form = MergeSelectedForm(initial = { 'ct' : request.GET['ct'], 'ids' : request.GET['ids'] })
    form.fields['merge_into'].queryset = ct.model_class().objects.filter(id__in = ids)

    transaction.commit()

    return render_to_response('admin/merge_selected.html', 
                              { 'form' : form, 'app_label' : ct.app_label, 'model' : ct.model, }, 
                              context_instance = RequestContext(request))

class BaseMergeableAdmin(VersionAdmin):
  actions = ('merge', )
  list_display = ('locked',)
  readonly_fields = ('locked',)

  def merge(self, request, query_set):
    if query_set.count() < 2:
      messages.error(request, "More than one entry needs to be selected")
      return 

    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(query_set.model)
    return HttpResponseRedirect("/admin/merge_selected/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))

  merge.short_description = 'Merge entries'

  def get_actions(self, request):
    actions = super(BaseMergeableAdmin, self).get_actions(request)

    if not request.user.has_perm(self.__class__.merge_perm):
      del actions['merge']

    return actions

class PoliticalUnitAdmin(BaseSubmitAdmin, BaseMergeableAdmin):
  list_display = ('__unicode__', 'pk', 'active', 'submitted_by') + BaseMergeableAdmin.list_display

  activate_perm = 'common.activate_polunit'
  merge_perm = 'common.merge_polunit'

  search_fields = ('name', )

  readonly_fields = BaseSubmitAdmin.readonly_fields + BaseMergeableAdmin.readonly_fields

  actions = BaseSubmitAdmin.actions + BaseMergeableAdmin.actions + ('nonbulk_delete', )

  def get_actions(self, request):
    actions1 = BaseSubmitAdmin.get_actions(self, request)
    actions2 = BaseMergeableAdmin.get_actions(self, request)

    actions1.update(actions2)

    if actions1.has_key('delete_selected'):
      del actions1['delete_selected']

    return actions1

  def nonbulk_delete(self, request, query_set):
    for loc in query_set.all():
      with reversion.revision:
        loc.delete()
        revision.user = request.user
        revision.comment = "Deleted political/geographic unit"

  nonbulk_delete.short_description = "Delete selected political/geographic units"

  
class GeoSubLocationInline(BaseSubmitTabularInline):
  model = models.Location 
  fields = ('full_name', 'active', 'submitted_by',)
  fk_name = 'geographically_in'
  extra = 0

  readonly_fields = ('active', 'submitted_by', 'full_name')

  activate_perm = 'common.activate_location'

class LocationAdmin(PoliticalUnitAdmin) :
  #list_display = ('__unicode__', 'active', 'submitted_by')
  exclude = ('full_name', )
  activate_perm = 'common.activate_location'
  merge_perm = 'common.merge_location'
  autocomplete_fields = { 'geographically_in' : ('full_name', 'autocomplete_label'), 'politically_in' : ('name', 'autocomplete_label'), }
  readonly_fields = PoliticalUnitAdmin.readonly_fields + ('geo_features',)

  inlines = [ GeoSubLocationInline, ]

  actions = PoliticalUnitAdmin.actions + ('convert_to_polunit', )

  fieldsets = [
      (None, 
        {'fields' : ['active', 'submitted_by', 'datetime_created', 'locked', ]}),

      ("General Information",
        {'fields' : ['name', 'geographically_in', 'politically_in', 'unit_type', 'geo_features', ]}),

      ("Coding",
        {'classes' : ['collapse', ],
         'fields' : ['wb_code', 'iso_3166_1_letter_code', 'iso_3166_1_num_code', 'iso_3166_2_code', 'polity_num_code', 'polity_letter_code', 'nato_code', 'fips_code', 'undp_code', 'ICAO_code', ]})
  ]

  def convert_to_polunit(self, request, query_set):
    for to_convert in query_set.all():
      with reversion.revision:
        to_convert.convert_to_polunit()
        revision.user = request.user
        revision.comment = 'Location to PoliticalUnit conversion'
        to_convert.delete()

  convert_to_polunit.short_description = 'Convert to political unit'

  def get_actions(self, request):
    actions = super(LocationAdmin, self).get_actions(request)

    if not request.user.has_perm('common.convert2polunit'):
      del actions['convert_to_polunit']

    return actions

class TemporalLocationAdmin(LocationAdmin):
  activate_perm = 'common.activate_temploc'
  merge_perm = 'common.merge_temploc'
  
class BaseCategoryAdmin(BaseSubmitAdmin):
  list_display = ('name', 'active', 'submitted_by', 'datetime_created', ) 
  readonly_fields = ('locked',)
  
class BaseMergeableCategoryAdmin(BaseCategoryAdmin, BaseMergeableAdmin):
  list_display = BaseCategoryAdmin.list_display + BaseMergeableAdmin.list_display
  actions = BaseCategoryAdmin.actions + BaseMergeableAdmin.actions 

  def get_actions(self, request):
    actions1 = BaseCategoryAdmin.get_actions(self, request)
    actions2 = BaseMergeableAdmin.get_actions(self, request)

    actions1.update(actions2)
    return actions1

class ReligionAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_religion'
  merge_perm = 'common.merge_religion'

class RaceAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_race'
  merge_perm = 'common.merge_race'

class EthnicityAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_ethnicity'
  merge_perm = 'common.merge_ethnicity'
  
class EthnicOriginAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_ethnic_origin'
  merge_perm = 'common.merge_ethnic_origin'

class LengthUnitAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_length_unit'
  merge_perm = 'common.merge_length_unit'

class WeightUnitAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_weight_unit'
  merge_perm = 'common.merge_weight_unit'

class PoliticalUnitTypeAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_polunittype'
  merge_perm = 'common.merge_polunittype'

class LanguageAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_language'
  merge_perm = 'common.merge_language'

class BaseGeoAdmin(geo_admin.GeoModelAdmin):
  list_display = ("ft_id", "point_x", "point_y", )

class GeoPointAdmin(BaseGeoAdmin):
  pass

class GeoPolygonAdmin(BaseGeoAdmin):
  list_display = BaseGeoAdmin.list_display + ("shape_leng", "shape_area", )

admin.site.register(models.PoliticalUnit, PoliticalUnitAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.TemporalLocation, TemporalLocationAdmin)
admin.site.register(models.Religion, ReligionAdmin)
admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.Ethnicity, EthnicityAdmin)
admin.site.register(models.EthnicOrigin, EthnicOriginAdmin)
admin.site.register(models.LengthUnit, LengthUnitAdmin)
admin.site.register(models.WeightUnit, WeightUnitAdmin)
admin.site.register(models.PoliticalUnitType, PoliticalUnitTypeAdmin)
admin.site.register(models.Language, LanguageAdmin)

admin.site.register(models.GeoPoint, GeoPointAdmin)
admin.site.register(models.GeoPolygon, GeoPolygonAdmin)
