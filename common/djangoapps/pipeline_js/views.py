"""
Views for returning XModule JS (used by requirejs)
"""
import json
from django.conf import settings
from django.http import HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from edxmako.shortcuts import render_to_response


def get_xmodule_urls():
    """
    Returns a list of the URLs to hit to grab all the XModule JS
    """
    if settings.DEBUG:
        paths = [path.replace(".coffee", ".js") for path in
                 settings.PIPELINE_JS['module-js']['source_filenames']]
    else:
        paths = [settings.PIPELINE_JS['module-js']['output_filename']]
    return [staticfiles_storage.url(path) for path in paths]


def xmodule_js_files(request):
    """
    View function that returns XModule URLs as a JSON list; meant to be used
    as an API
    """
    urls = get_xmodule_urls()
    return HttpResponse(json.dumps(urls), content_type="application/json")


def requirejs_xmodule(request):
    """
    View function that returns a requirejs-wrapped Javascript file that
    loads all the XModule URLs; meant to be loaded via requireJS
    """
    return render_to_response(
        "xmodule.js",
        {"urls": get_xmodule_urls()},
        content_type="text/javascript",
    )
