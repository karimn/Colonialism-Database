import csv

from django.http import HttpResponse
from government.models import *
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

from economics.models import *
from common.forms import GeneralSearchForm

from django.utils import simplejson

def about(request):
    return render_to_response('about.html',
        {
        },context_instance=RequestContext(request))


@login_required
def search(request):
    if request.GET:
        form = GeneralSearchForm(request.GET)
        if form.is_valid():
            if request.GET.get('startdate'):
                startdate = request.GET.get('startdate')
            else:
                startdate = "1870-01-01"
            if request.GET.get('enddate'):
                enddate = request.GET.get('enddate')
            else:
                enddate = "2006-12-31"
            if request.GET.get('sourceinput'):
                sourceinput = request.GET.get('sourceinput')
            else:
                sourceinput = ""
            locations_list = []
            results = []

            # they want to limit the timeframe search
            if not form.cleaned_data['all_time_frames']:
                # find the start date
                startdate = "%s-%s-%s" % (form.cleaned_data['start_date_year'], form.cleaned_data['start_date_month'],
                                          form.cleaned_data['start_date_day'])
                enddate = "%s-%s-%s" % (form.cleaned_data['end_date_year'], form.cleaned_data['end_date_month'],
                                          form.cleaned_data['end_date_day'])


            datesourceresults = MainDataEntry.objects.filter(Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate))).filter(Q(source__name__icontains=sourceinput)).select_related().order_by('id')

            if request.GET.get('locations'):
                searchlocations = request.GET.get('locations')
                locations_list = searchlocations.split(", ")
                for x in locations_list:
                    for y in datesourceresults.filter(location__name="%s"%x).select_related().order_by('id'):
                        results.append(y)
            else:
                results = datesourceresults

            return render_to_response("general_search_results.html",
                {
                    "locations_list":locations_list,
                    "results":results,
                    "paginator": paginator,
                    "search":search,
                    "form": form,
                },context_instance=RequestContext(request))
    else:
        form = GeneralSearchForm()

    return render_to_response('search.html',
        {
            'form': form,
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
