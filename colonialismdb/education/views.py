from django.shortcuts import render_to_response
from education.models import *
from django.db.models import Q
from django.contrib import auth
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage


def	edusearch(request):
	startdate = request.GET.get('startdate','')
	enddate = request.GET.get('enddate','')
	page = request.GET.get('page','')
	#if not startdate or startdate == "":
	#	startdate = "1870-01-01"
	#if not enddate or enddate == "":
	#	enddate = "2006-12-31"
	if startdate and enddate:
		qset = (Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate)))
		disp = MainDataEntry.objects.selected_related().filter(qset).order_by('id')
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
	return render_to_response("education.html",{"results":disp,"sdate":startdate,"edate":enddate,"query":enddate})
