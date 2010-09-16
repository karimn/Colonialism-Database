from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.db import models
from django.utils import simplejson

def autocomplete(request, from_applabel, from_model, to_applabel, to_model):
  query = request.GET['term']
  search_field = request.GET['search_field']

  model = models.get_model(to_applabel, to_model)

  try:
    data = [{ 'label' : f.__unicode__(), 'pk' : f.pk } for f in model.objects.filter(**{('%s__istartswith' % search_field) : query})[:10]]
  except FieldError:
    return HttpResponseServerError()

  return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')

def get_label(request, from_applabel, from_model, from_id, to_applabel, to_model):
  import pdb; pdb.set_trace()

  obj_id = request.GET['id']

  model = models.get_model(to_applabel, to_model)

  return model.objects.get(pk = obj_id)
