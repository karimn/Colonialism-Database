from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import list_detail
from django.db.models import Q

import forms, models

def index(request):
  return HttpResponseRedirect('query/')

def query(request):
  if 'location' in request.GET:
    form = forms.MainPopulationQueryForm(request.GET)

    if form.is_valid():
            
      locations = form.cleaned_data['location']

      if len(locations) == 0:
        return list_detail.object_list(
            request,
            queryset = models.MainDataEntry.objects.all(),
            template_name = 'population/query_results.html')

      #import pdb; pdb.set_trace()

      location_ids = models.Location.get_location_ids_in(locations)
      
      return list_detail.object_list(
          request,
          queryset = models.MainDataEntry.objects.filter(location__in = location_ids),
          template_name = 'population/query_results.html')

  form = forms.MainPopulationQueryForm()

  return render_to_response('population/index.html', { 'form' : form, })
