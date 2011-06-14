from django.shortcuts import render_to_response
from government.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# Imports for the Ajax calls and the Jquery autocomplete plugin
from django.http import HttpResponse
from django.utils import simplejson
from django.template import RequestContext

# Imports to aid in unicode string handling
from django.utils.encoding import smart_str, smart_unicode

from government.forms import GovernmentSearchForm


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

# Search function for Government/Politics data
def	govtsearch(request):
    form = GovernmentSearchForm()

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
        paginator = Paginator(results,20)
        try:
            page = request.GET.get('page','1')
        except ValueError:
            page = 1
        try:
            results = paginator.page(page)
        except (EmptyPage, InvalidPage):
            results = paginator.page(paginator.num_pages)

        return render_to_response("government_search_results.html",
            {
                "locations_list":locations_list,
                "searchlocations":searchlocations,
                "startdate":startdate,
                "enddate":enddate,
                "sourceinput":sourceinput,
                "results":results,
                "search":search,
                "form": form,
            },context_instance=RequestContext(request))



    else:
        results = []
        locations_list = []
        searchlocations = ""
        startdate = ""
        enddate = ""
        sourceinput = ""
        search = ""


    return render_to_response("government.html",
        {
            "locations_list":locations_list,
            "searchlocations":searchlocations,
            "startdate":startdate,
            "enddate":enddate,
            "sourceinput":sourceinput,
            "results":results,
            "search":search,
            "form": form,
        },context_instance=RequestContext(request))






























"""

	locations_list = []
	#for x in MainDataEntry.objects.select_related():
	#	if not x.location.location.name in locations_list:
	#		locations_list.append(str(x.location.location.name))
	if request.GET.get('datesearch'):
		datesearch = request.GET.get('datesearch')
		startdate = request.GET.get('startdate')
		enddate = request.GET.get('enddate')
		qset = (Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate)))
		dateresults = MainDataEntry.objects.filter(qset).select_related().order_by('id')
		paginator = Paginator(dateresults,1)
		try:
			page = int(request.GET.get('page',1))
		except ValueError:
			page = 1
		try:
			dateresults = paginator.page(page)
		except (EmptyPage, InvalidPage):
			dateresults = paginator.page(paginator.num_pages)
	else:
		datesearch = ""
		startdate = ""
		enddate = ""
		dateresults = []
	if request.GET.get('locationsearch'):
		locationsearch = request.GET.get('locationsearch')
		searchlocations = request.GET.get("locations")
		if searchlocations:
			loclist = searchlocations.split(", ")
			qs = ""
			locresults = []
			for x in loclist:
				locresults += MainDataEntry.objects.filter(Q(location__name="%s" % x)).select_related().order_by('id')
			paginator = Paginator(locresults,1)
			try:
				page = request.GET.get('page','1')
			except ValueError:
				page = '1'
			try:
				locresults = paginator.page(page)
			except (EmptyPage, InvalidPage):
				locresults = paginator.page(paginator.num_pages)
	else:
		searchlocations = ""
		locationsearch = ""
		locresults = []
	if request.GET.get('sourcesearch'):
		sourcesearch = request.GET.get('sourcesearch')
		sourceinput = request.GET.get('sourceinput')
		sourceresults = MainDataEntry.objects.select_related().filter(Q(source__name__icontains=sourceinput)).order_by('id')
		paginator = Paginator(sourceresults,1)
		try:
			page = request.GET.get('page','1')
		except ValueError:
			page = '1'
		try:
			sourceresults = paginator.page(page)
		except (EmptyPage, InvalidPage):
			sourceresults = paginator.page(paginator.num_pages)
	else:
		sourcesearch = ""
		sourceinput = ""
		sourceresults = []

	return render_to_response("government.html",{"locations_list":locations_list,"searchlocations":searchlocations,"locresults":locresults,"locationsearch":locationsearch,"datesearch":datesearch,"startdate":startdate,"enddate":enddate,"dateresults":dateresults,"sourcesearch":sourcesearch,"sourceinput":sourceinput,"sourceresults":sourceresults})
"""
