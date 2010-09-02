from django.http import HttpResponse, HttpResponseRedirect, Http404

from colonialismdb.local_settings import MEDIA_ROOT

def open_src_file(request, path, ext):
  file_path = '%s/sources/%s.%s' % (MEDIA_ROOT, path, ext)

  #if ext.lower() == "pdf":
  return HttpResponse(open(file_path, 'rb').read(), mimetype='application/pdf')
  #else:
    

