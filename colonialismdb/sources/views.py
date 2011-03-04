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
	source = str(request.GET.get('source').replace("%20"," ").replace("'",""))	
	s1 = source.split(" (")
	results = []
	
	for x in Source.objects.select_related().filter(name__icontains=s1[0]):
		if cmp(str(x.source),source) == 0:
			results.append(x)

	return render_to_response("sourceinfo.html",{"results":results,"title":source})
