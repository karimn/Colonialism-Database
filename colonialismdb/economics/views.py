from django.shortcuts import render_to_response
from economics.models import *
from government.models import *
from education.models import *
from population.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def test(request):
	locations2 = []
	for x in AggregateTradeDataEntry.objects.select_related():
		if not x.location.location.name in locations2:
			locations2.append(str(x.location.location.name))
	
	locations = str(locations2)
	lsearch = request.GET.get('lsearch')
	res = []
	if lsearch:
		linput = request.GET.get('slocations')
		l1 = linput.split(", ")
		qs = ""	
		res = []
		for x in l1:
			res += MainDataEntry.objects.filter(Q(location__name="%s" % x)).select_related()
	else:
		linput = ""
		res = []
	
	return render_to_response("test.html",{"slocations":request.GET.get('slocations'),"results":res,"locations":locations})


def	econsearch(request):
	startdate = request.GET.get('startdate','')
	enddate = request.GET.get('enddate','')
	page = request.GET.get('page','')
	search = request.GET.get('search','')
	location = request.GET.get('location','')
	locations2 = []
	ldisp = []

	for x in AggregateTradeDataEntry.objects.select_related():
		if not x.location.location.name in locations2:
			locations2.append(str(x.location.location.name))
	
	locations = str(locations2)


	if search == "Search date values":
	#	if not startdate or startdate == "":
	#		startdate = "1870-01-01"
	#	if not enddate or enddate == "":
	#		enddate = "2006-12-31"
		if startdate and enddate:
			qset = (Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate)))
			disp = AggregateTradeDataEntry.objects.filter(qset).select_related().order_by('id')
			paginator = Paginator(disp,1)
			try:
				page = int(request.GET.get('page',1))
			except ValueError:
				page = 1
			try:
				disp = paginator.page(page)
			except (EmptyPage, InvalidPage):
				disp = paginator.page(paginator.num_pages)
	else:
		disp = []
	
	lsearch = request.GET.get('lsearch','')
	if lsearch == "Search locations":
		linput = request.GET.get('locations')
		l1 = linput.split(", ")
		qs = ""	
		res = []
		for x in l1:
			res = res + AggregateTradeDataEntry.objects.filter(Q(location__name="%s" % x)).select_related()
			paginator = Paginator(disp,1)
			try:
				page = int(request.GET.get('page',1))
			except ValueError:
				page = 1
			try:
				res = paginator.page(page)
			except (EmptyPage, InvalidPage):
				res = paginator.page(paginator.num_pages)
	else:
		res = []

	"""Source search
	for x in AggregateTradeDataEntry.objects.select_related():
		l.append(str(x.source.source.source.source))
	"""


	return render_to_response("economics.html",{"results":disp,"sdate":startdate,"edate":enddate,"query":enddate, "search":search, "locations":locations, "lresults":res})
	
#return render_to_response("test.html",{"locations":linput,"res":res})
