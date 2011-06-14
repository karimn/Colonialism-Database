import csv
import types

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

from economics.models import *



from django.utils import simplejson

def about(request):
    return render_to_response('about.html',
        {
        },context_instance=RequestContext(request))


def search(request):

    return render_to_response('search.html',
        {
        },context_instance=RequestContext(request))



def index(request):
    return render_to_response('index.html',
        {
        },context_instance=RequestContext(request))
  #return render_to_response("mainindex.html")


def exportcsv(request):
	rset = request.GET['rset']
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=export.csv'
	writer = csv.writer(response)
	rrow = []
	for x in rset[:1]:
		#rrow.append(x)
		#rrow.append(x.submitted_by)
		writer.writerow(x)
	t = type(rset)
	return HttpResponse(t)

def autocomplete(request, from_applabel, from_model, to_applabel, to_model):
  query = request.GET['term']
  search_field = request.GET['search_field']
  label_method = request.GET['label_method']

  model = models.get_model(to_applabel, to_model)

  if label_method:
    label_method_attr = getattr(model, label_method)
    data = [{ 'label' : label_method_attr(f), 'pk' : f.pk } for f in get_list_or_404(model, **{('%s__istartswith' % search_field) : query})[:25]]
  else:
    data = [{ 'label' : f.__unicode__(), 'pk' : f.pk } for f in get_list_or_404(model, **{('%s__istartswith' % search_field) : query})[:25]]

  data.append({ 'label' : '[None]', 'pk' : '' })

  return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')

def get_label(request, from_applabel, from_model, from_id, to_applabel, to_model):
  obj_id = request.GET['id']

  model = models.get_model(to_applabel, to_model)

  return get_object_or_404(model, pk = obj_id)
