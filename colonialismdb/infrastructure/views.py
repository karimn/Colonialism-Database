from django.shortcuts import render_to_response
from infrastructure.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from sources.models import *

# Imports for the Ajax calls and the Jquery autocomplete plugin
from django.http import HttpResponse
from django.utils import simplejson

# Imports to aid in unicode string handling
from django.utils.encoding import smart_str, smart_unicode

# Ajax call from template picks up matching locations with this function
def locationlookup(request):
	lresults = []
	temp = []
	if request.method == "GET":
		if request.GET.has_key(u'q'):
			value = request.GET[u'q']
			model_results = MainDataEntry.objects.filter(location__name__istartswith="%s" % value).select_related().distinct()
			for x in MainDataEntry.objects.filter(location__name__istartswith=value).distinct():
				if smart_str(x.location.location.name) not in lresults:
					lresults.append(smart_str(x.location.location.name))

	json = simplejson.dumps(lresults)
	return HttpResponse(json, mimetype='application/json')

# Search function for Infrastructure data
def	infrasearch(request):
	if request.GET.get('search'):
		search = request.GET.get('search')
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
		souceresults = Source.objects.filter(name__icontains='%s'%sourceinput).select_related()

		datesourceresults = MainDataEntry.objects.filter(Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate))).filter(Q(source__name__icontains=sourceinput)).select_related().order_by('id')
		
		if request.GET.get('locations'):
			searchlocations = request.GET.get('locations')
			locations_list = searchlocations.split(", ")
			for x in locations_list:
				for y in datesourceresults.filter(location__name="%s"%x).select_related().order_by('id'):
					results.append(y)
		else:
					searchlocations=""
					results = datesourceresults
		rset =  results
		paginator = Paginator(results,20)
		try:
			page = request.GET.get('page','1')
		except ValueError:
			page = 1
		try:
			results = paginator.page(page)
		except (EmptyPage, InvalidPage):
			results = paginator.page(paginator.num_pages)
			
	else:
		results = []
		locations_list = []
		searchlocations = ""
		startdate = ""
		enddate = ""
		sourceinput = ""
		search = ""
		sourceresults = []
		rset = []
	#return render_to_response("sourceinfo.html",{"sourceresults":sourceresults})
	return render_to_response("infrastructure.html",{"locations_list":locations_list,"searchlocations":searchlocations,"startdate":startdate,"enddate":enddate,"sourceinput":sourceinput,"results":results,"search":search,"rset":rset})
