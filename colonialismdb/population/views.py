from django.shortcuts import render_to_response
from population.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.encoding import smart_str, smart_unicode

from django.http import HttpResponse
from django.utils import simplejson
from django.utils.encoding import smart_str, smart_unicode

def locationlookup(request):
	lresults = []
	temp = []
	if request.method == "GET":
		if request.GET.has_key(u'q'):
			value = request.GET[u'q']
			model_results = MainDataEntry.objects.filter(location__name__istartswith="%s" % value).select_related().distinct()
			#results = [ (x.__unicode__(), smart_str(x.location.location.name)) for x in model_results ]
			#results = [ x.location.location.name for x in model_results ]
			for x in MainDataEntry.objects.filter(location__name__istartswith=value).distinct()[:20]:
				if smart_str(x.location.location.name) not in lresults:
					lresults.append(smart_str(x.location.location.name))
	json = simplejson.dumps(lresults)
	return HttpResponse(json, mimetype='application/json')

def popsearch(request):

	if request.GET.get('search'):
		search = request.GET.get('search')
		if request.GET.get('startdate'):
			startdate = request.GET.get('startdate')
		else:
			startdate = "1870-01-01"
		if request.GET.get('minage'):
			minage = request.GET.get('minage')
		else:
			minage = 0
		if request.GET.get('maxage'):
			maxage = request.GET.get('maxage')
		else:
			maxage = 100
		if request.GET.get('genders'):
			if request.GET.get('genders') == 'e':
				genders = "e"
				genderfilter = ~Q(population_gender='None')
			else:
				genders = request.GET.get('genders')
				genderfilter = Q(population_gender=genders)
		else:
			genders = ""
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
		
		datefilter = Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate))
		sourcefilter = Q(source__name__icontains=sourceinput)
		agefilter = Q(age_start__isnull=False) & Q(age_end__isnull=False) & Q(age_start__gte=minage) & Q(age_end__lte=maxage)
		
		datesourceresults = MainDataEntry.objects.filter(datefilter).filter(sourcefilter).filter(agefilter).filter(genderfilter).select_related().order_by('id')

		if request.GET.get('locations'):
			searchlocations = request.GET.get('locations')
			locations_list = searchlocations.split(", ")
			for x in locations_list:
				for y in datesourceresults.filter(location__name="%s"%x).select_related().order_by('id'):
					results.append(y)
		else:
					searchlocations=""
					results = datesourceresults
			
		paginator = Paginator(results,1)
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
		genders = ""
		minage =""
		maxage = ""
	return render_to_response("population.html",{"locations_list":locations_list,"searchlocations":searchlocations,"startdate":startdate,"enddate":enddate,"sourceinput":sourceinput,"genders":genders,"minage":minage,"maxage":maxage,"results":results,"search":search})

"""
	locations_list = []
	#for x in MainDataEntry.objects.select_related():
	#	clocation = smart_unicode(x.location.location.name,encoding='utf-8',errors='ignore')
	#	if not  clocation in locations_list:
	#		#locations_list.append(smart_str(x.location.location.name))
	#		locations_list.append(clocation)
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
	if request.GET.get('agegendersearch'):
		genders = request.GET.get('gender')
		if request.GET.get('minage'):
			minage = int(request.GET.get('minage'))
		else:
			minage = 0
		if request.GET.get('maxage'):
			maxage = int(request.GET.get('maxage'))
		else:
			maxage = 100
		agegenderresults = MainDataEntry.objects.select_related().filter(Q(population_gender=genders) & Q(age_start__isnull=False) & Q(age_end__isnull=False) & Q(age_start__gte=minage) & Q(age_end__lte=maxage)).order_by('id')
		#for x in Source.objects.select_related()[:1]:

	else:
		genders = []
		agegenderresults = []
		minage = ''
		maxage = ''
	
	return render_to_response("population.html",{"locations_list":locations_list,"searchlocations":searchlocations,"locresults":locresults,"locationsearch":locationsearch,"datesearch":datesearch,"startdate":startdate,"enddate":enddate,"dateresults":dateresults,"sourcesearch":sourcesearch,"sourceinput":sourceinput,"sourceresults":sourceresults,"genders":genders,"agegenderresults":agegenderresults,"minage":minage,"maxage":maxage})
"""
