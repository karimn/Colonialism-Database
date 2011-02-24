from django.shortcuts import render_to_response
from population.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.encoding import smart_str, smart_unicode

def popsearch(request):
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
			minage = request.GET.get('minage')
		else:
			minage = 0
		if request.GET.get('maxage'):
			maxage = request.GET.get('maxage')
		else:
			maxage = 100
		agegenderresults = MainDataEntry.objects.select_related().filter(Q(population_gender=genders) & Q(age_start__isnull=False) & Q(age_end__isnull=False) & Q(age_start__lt=minage) & Q(age_end__lt=maxage)).order_by('id')
		
		#filter(Q(age_start__lt=12))
	else:
		genders = []
		agegenderresults = []
		minage = ''
		maxage = ''
	
	return render_to_response("population.html",{"locations_list":locations_list,"searchlocations":searchlocations,"locresults":locresults,"locationsearch":locationsearch,"datesearch":datesearch,"startdate":startdate,"enddate":enddate,"dateresults":dateresults,"sourcesearch":sourcesearch,"sourceinput":sourceinput,"sourceresults":sourceresults,"genders":genders,"agegenderresults":agegenderresults,"minage":minage,"maxage":maxage})
