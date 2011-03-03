from django.http import HttpResponse, HttpResponseRedirect, Http404

from colonialismdb.local_settings import MEDIA_ROOT
from sources.models import *
from django.db.models import Q
from django.shortcuts import render_to_response

def open_src_file(request, path, ext):
  file_path = '%s/sources/%s.%s' % (MEDIA_ROOT, path, ext)

  #if ext.lower() == "pdf":
  return HttpResponse(open(file_path, 'rb').read(), mimetype='application/pdf')
  #else:
    
def sourceinfo(request):
	title = request.GET.get('source').replace("%20"," ").split(" ")
	results = []
	for x in 
	
	results = Source.objects.filter(name__icontains=title).select_related()
	#for x in title.split(" "):
	#	results.append(rs.filter(name__icontains=x).select_related())
	return render_to_response("sourceinfo.html",{"results":results,"title":title})
