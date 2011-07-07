from django.shortcuts import render_to_response
from government.models import *
from django.db.models import Q
from django.http import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# Imports for the Ajax calls and the Jquery autocomplete plugin
from django.http import HttpResponse
from django.utils import simplejson
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Imports to aid in unicode string handling
from django.utils.encoding import smart_str, smart_unicode

from government.forms import GovernmentSearchForm
import csv

# Ajax call from template picks up matching locations with this function
def locationlookup(request):
    lresults = []
    temp = []
    if request.method == "GET":
        if request.GET.has_key(u'q'):
            value = request.GET[u'q']
            locations = Location.objects.filter(full_name__istartswith=value).distinct().values('name').order_by('name')
            for x in locations:
                lresults.append(x['name'])
    json = simplejson.dumps(lresults)
    return HttpResponse(json, mimetype='application/json')

# Search function for Government/Politics data
@login_required
def govtsearch(request):

    if request.GET.get('search'):
        print request.GET
        print request.GET.getlist('empire')
        form = GovernmentSearchForm(request.GET)
        search = request.GET.get('search')

        startdate = ''
        enddate = ''

        if 'all_time_frames' not in request.GET:
            startdate = "%s-%s-%s" % (request.GET.get('start_date_year'),
                                      request.GET.get('start_date_month'),
                                      request.GET.get('start_date_day'))
            enddate = "%s-%s-%s" % (request.GET.get('end_date_year'),
                                      request.GET.get('end_date_month'),
                                      request.GET.get('end_date_day'))


        if request.GET.get('sourceinput'):
            sourceinput = request.GET.get('sourceinput')
        else:
            sourceinput = ""


        locations_list = []
        results = []

        if startdate:
            datesourceresults = MainDataEntry.objects.filter(Q(begin_date__range=(startdate,enddate)) | Q(end_date__range=(startdate,enddate))).filter(Q(source__name__icontains=sourceinput)).select_related().order_by('id')
        else:
            datesourceresults = MainDataEntry.objects.filter(Q(source__name__icontains=sourceinput)).select_related().order_by('id')

        if request.GET.get('locations'):
            searchlocations = request.GET.get('locations')
            locations_list = searchlocations.split(", ")
            for x in locations_list:
                for y in datesourceresults.filter(location__name="%s"%x).select_related().order_by('id'):
                    results.append(y)
        else:
            searchlocations=""
            results = datesourceresults

        # check if they want to limit by any of the other fields:
        if request.GET.getlist('continent')[0] != '':
            print "Limiting by continent"
            results = results.filter(location__location__geographically_in__name__in=request.GET.getlist('continent'))

        if request.GET.getlist('empire')[0] != '':
            print "Limiting by empire"
            results = results.filter(location__location__pk__in=request.GET.getlist('empire'))

        if request.GET.getlist('nation_state')[0] != '':
            print "Limiting by nation_state"
            print request.GET.getlist('nation_state')
            results = results.filter(location__location__pk__in=request.GET.getlist('nation_state'))

        if request.GET.getlist('semi_sovereign')[0] != '':
            print "Limiting by semi_sveriegn"
            results = results.filter(location__location__pk__in=request.GET.getlist('semi_sovereign'))

        if request.GET.getlist('non_sovereign')[0] != '':
            print "Limiting by non_sveriegn"
            results = results.filter(location__location__pk__in=request.GET.getlist('non_sovereign'))

        result_start_date = None
        result_end_date = None

        result_start_date = results.order_by('begin_date')[0].begin_date
        result_end_date = results.order_by('end_date')[0].begin_date

        print result_start_date


        if 'export' in request.GET:
            if request.GET.get('export') == 'CSV':
                # Create the HttpResponse object with the appropriate CSV header.
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = 'attachment; filename=politic_results.csv'
                writer = csv.writer(response)
                writer.writerow(['ID', 'Source', 'Begin Date', 'End Date', 'Location'])
                for result in results:
                    print result.pk
                    writer.writerow([result.pk, result.source, result.begin_date, result.end_date, result.location])

                return response



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
                "result_start_date": result_start_date,
                "result_end_date": result_end_date,
                "locations_list":locations_list,
                "searchlocations":searchlocations,
                "startdate":startdate,
                "enddate":enddate,
                "sourceinput":sourceinput,
                "results":results,
                "search":search,
                "form": form,
                "paginator": paginator,
                "dataset": request.GET.get('dataset'),
                "show_continent": 'continent' in request.GET,
                "show_remarks": 'remarks' in request.GET,
                "show_confederation": 'confederation' in request.GET,
                "show_country_codes": 'country_codes' in request.GET,
                "show_placename": 'placename' in request.GET,
                "show_alternate_placenames": 'alternate_placenames' in request.GET,
                "show_uncertainty": 'uncertainty' in request.GET,
            },context_instance=RequestContext(request))

    else:
        form = GovernmentSearchForm()
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
    #    if not x.location.location.name in locations_list:
    #        locations_list.append(str(x.location.location.name))
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
