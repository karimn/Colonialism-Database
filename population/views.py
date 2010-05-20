from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import list_detail

import forms, models

def index(request):
  return HttpResponseRedirect('query/')

def query(request):
  if 'location' in request.GET:
    form = forms.MainPopulationQueryForm(request.GET)

    if form.is_valid():
      try:
        # TODO Handle multiple selections
        location = models.Location.objects.get(pk = form.cleaned_data['location'])
      except models.Location.DoesNotExist:
        raise Http404

      return list_detail.object_list(
          request,
          queryset = models.MainDataEntry.objects.filter(location=location), #TODO Not necessarily the immediate location...
          template_name = 'population/query_results.html')

  form = forms.MainPopulationQueryForm()

  return render_to_response('population/index.html', { 'form' : form, })
