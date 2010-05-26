from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import list_detail
from django.db.models import Q

import forms, models

def index(request):
  return HttpResponseRedirect('query/')

def query(request):
  if 'submitted' in request.GET:
    form = forms.MainPopulationQueryForm(request.GET)

    if form.is_valid():
      query = models.MainDataEntry.objects.all()

      locations = form.cleaned_data['location']
      
      if len(locations) != 0:
        location_ids = models.Location.get_location_ids_in(locations)
        query = query.filter(location__in = location_ids)

      #import pdb; pdb.set_trace()

      if form.cleaned_data['begin_date']:
        query = query.filter(begin_date__gte=form.cleaned_data['begin_date'])

      if form.cleaned_data['end_date']:
        query = query.filter(end_date__lte=form.cleaned_data['end_date'])

      count_types = form.cleaned_data['count_type']

      if (len(count_types) > 1) or ((len(count_types) == 1) and count_types[0] != 'all'):
        if 'individ' in count_types:
          query = query.filter(individuals_population_value__isnull = False)

        if 'fam' in count_types:
          query = query.filter(families_population_value__isnull = False)

        if 'males' in count_types:
          query = query.filter(male_population_value__isnull = False)

        if 'females' in count_types:
          query = query.filter(female_population_value__isnull = False)
      
      return list_detail.object_list(
          request,
          queryset = query,
          template_name = 'population/query_results.html')

  else:
    form = forms.MainPopulationQueryForm()

  return render_to_response('population/index.html', { 'form' : form, })
