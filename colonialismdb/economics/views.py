from django.shortcuts import render_to_response
from economics.models import *
from government.models import *
from education.models import *
from population.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils import simplejson

import json


def	econsearch(request):
	startdate = request.GET.get('startdate','')
	enddate = request.GET.get('enddate','')
	page = request.GET.get('page','')
	search = request.GET.get('search','')
	location = request.GET.get('location','')
	locations2 = []

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
	"""
	if search == "Search location values":
		if location:
			qset = (Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate)))
			disp = AggregateTradeDataEntry.objects.filter(qset).values().order_by('id')
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
	"""

	"""Source search
	for x in AggregateTradeDataEntry.objects.select_related():
		l.append(str(x.source.source.source.source))
	"""


	return render_to_response("economics.html",{"results":disp,"sdate":startdate,"edate":enddate,"query":enddate,"location":location, "search":search, "locations":locations})
