from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.db import models
from django.utils import simplejson
from django.shortcuts import get_object_or_404, get_list_or_404
from django.shortcuts import render_to_response
from economics.models import *
from django.db.models import Q

import types

def index(request):
  return render_to_response("mainindex.html")

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

def test(request):
	lsearch = request.GET.get('lsearch')
	
	if lsearch:
		linput = request.GET.get('locations')
		l1 = linput.split(", ")
		qs = ""	
		res = []
		for x in l1:
			res += Economics.MainDataEntry.objects.filter(Q(location__name="%s" % x)).select_related()
	else:
		res = []
		linput = ""
	return render_to_response("test.html",{"locations":linput,"res":res})
