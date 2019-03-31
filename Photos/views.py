import json
import re

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import requests

from bs4 import BeautifulSoup as bs

from Photos.constants import BASE, USER_AGENT
from Photos.models import ProfilePhotos, Photo
from Photos.tasks import start_request


class requestView(View):
    def get(self, request):
        return render(request, 'request.html')

    def post(self, request):
        if ProfilePhotos.objects.filter(name=request.POST['nickname']).exists():
            return render(request, 'response.html', context={'nickname': request.POST['nickname']})
        response = requests.get(f'{BASE}{request.POST["nickname"]}/', headers={'user-agent': USER_AGENT})
        if response.status_code == 200:
            soup = bs(response.text, 'html.parser')
            js_data = json.loads(soup.find(text=re.compile('window._shared'))[20:-1])
            start_request.apply_async(args = [js_data, request.POST['nickname']])
            return render(request, 'response.html', context={'nickname': request.POST['nickname']})
        else:
            return HttpResponse('invalid nickname')

def get_archive(request, profile_nickname):
    profile = ProfilePhotos.objects.get(name=profile_nickname)
    resp = HttpResponse( profile.zip.file, content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = f'attachment; filename={profile.zip.path.split("/")[-1]}'
    return resp

def get_status(request):
    if request.is_ajax():
        data = {}
        profile = ProfilePhotos.objects.get(name=request.POST['nickname'])
        data['count'] = profile.count
        data['downloaded'] = len(Photo.objects.filter(user__name=request.POST['nickname']))
        if (profile.zip):
            data['zip'] = 'true'
        data = json.dumps(data)
    else:
        data = 'This is not ajax request'
    return HttpResponse(data, content_type='application/json')

def lab_3(request):
    return render(request, 'lab3.html')