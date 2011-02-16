from django.shortcuts import render_to_response
from government.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage


def	govtsearch(request):
	startdate = request.GET.get('startdate','')
	enddate = request.GET.get('enddate','')
	page = request.GET.get('page','')
	search = request.GET.get('search','')
	location = request.GET.get('location','')
	#locations = MainDataEntry.objects.select_related().get().values()
	if search and search == "Search date values":
	#	if not startdate or startdate == "":
	#		startdate = "1870-01-01"
	#	if not enddate or enddate == "":
	#		enddate = "2006-12-31"
		if startdate and enddate:
			qset = (Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate)))
			disp = MainDataEntry.objects.select_related().filter(qset).order_by('id')
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
#	if search == "Search location values":
#		if location:
			#qset = (Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate)))
			#disp = MainDataEntry.objects.select_related().filter(qset).values().order_by('id')
#			paginator = Paginator(disp,1)
#			try:
#				page = int(request.GET.get('page',1))
#			except ValueError:
#				page = 1
#			try:
#				disp = paginator.page(page)
#			except (EmptyPage, InvalidPage):
#				disp = paginator.page(paginator.num_pages)
#	else:
#		disp = []
	return render_to_response("government.html",{"results":disp,"sdate":startdate,"edate":enddate,"query":enddate,"location":location, "search":search,"locations":location})
