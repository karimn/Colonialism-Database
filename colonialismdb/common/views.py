from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.db import models
from django.utils import simplejson
from django.shortcuts import get_object_or_404, get_list_or_404

import types


def autocomplete(request, from_applabel, from_model, to_applabel, to_model):
  query = request.GET['term']
  search_field = request.GET['search_field']
  label_method = request.GET['label_method']

  model = models.get_model(to_applabel, to_model)
  data = [{ 'label' : '[None]', 'pk' : '' }]
  
  if label_method:
    label_method_attr = getattr(model, label_method)
    data.extend([{ 'label' : label_method_attr(f), 'pk' : f.pk } for f in get_list_or_404(model, **{('%s__istartswith' % search_field) : query})[:25]])
  else:
    data.extend([{ 'label' : f.__unicode__(), 'pk' : f.pk } for f in get_list_or_404(model, **{('%s__istartswith' % search_field) : query})[:25]])

  return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')

def get_label(request, from_applabel, from_model, from_id, to_applabel, to_model):
  obj_id = request.GET['id']

  model = models.get_model(to_applabel, to_model)

  return get_object_or_404(model, pk = obj_id)
