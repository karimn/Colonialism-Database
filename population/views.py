from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import list_detail
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

import csv

import forms, models

def index(request):
  #return HttpResponseRedirect('query/')

  form = forms.MainPopulationQueryForm()
  return render_to_response('population/index.html', { 'form' : form, })

def query(request):
  #import pdb; pdb.set_trace()

  if 'new_query' in request.GET:
    form = forms.MainPopulationQueryForm(request.GET)

    if form.is_valid():
      query = models.MainDataEntry.objects.all()

      locations = form.cleaned_data['location']
      
      if len(locations) != 0:
        location_ids = models.Location.get_location_ids_in(locations)
        query = query.filter(location__in = location_ids)

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

      request.session['query'] = query

      page = request.GET.get('page', '1')
     
      return list_detail.object_list(
          request,
          queryset = query,
          template_name = 'population/query_results.html',
          template_object_name = 'data_entry',
          paginate_by = 50,
          page = page)
  else:
    page = request.GET.get('page', '1')

    #TODO Allow multiple queries per session
    return list_detail.object_list(
        request,
        queryset = request.session['query'], 
        template_name = 'population/query_results.html',
        template_object_name = 'data_entry',
        paginate_by = 50,
        page = page)

import codecs, cStringIO

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def download_data(request):
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=population_data.csv'

  writer = UnicodeWriter(response, delimiter = "\t")

  for data_entry in request.session['query'].values_list():
    writer.writerow(data_entry)

  return response

