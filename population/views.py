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
      
      return list_detail.object_list(
          request,
          queryset = query,
          template_name = 'population/query_results.html')

  else:
    form = forms.MainPopulationQueryForm()

  return render_to_response('population/index.html', { 'form' : form, })
