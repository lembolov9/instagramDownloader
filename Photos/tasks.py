import hashlib
import json
import zipfile
from datetime import timedelta
from io import BytesIO
from urllib.parse import quote_plus

import requests
from django.core.files.base import ContentFile
from django.utils import timezone

from instagramDownloader.celery import app
from Photos.constants import BASE_QUERY, QUERY_ID, USER_AGENT
from Photos.models import ProfilePhotos, Photo


@app.task()
def start_request(js_data, nickname):
    settings = {}
    settings['user_id'] = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
    settings['rhx_gis'] = js_data['rhx_gis']
    has_next_page = \
        js_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
            'has_next_page']
    photos_count = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
    file_object = ProfilePhotos(name=nickname, count=photos_count)
    file_object.save()
    settings['profile'] = file_object.pk
    download_photos.apply_async(args = [js_data['entry_data']['ProfilePage'][0]['graphql']
                                        ['user']['edge_owner_to_timeline_media']['edges'], settings['profile']])

    if has_next_page:
        settings['cursor'] = \
            js_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'][
                'page_info'][
                'end_cursor']
        get_urls.apply_async(args = [settings])

@app.task()
def get_urls(settings):
    var = json.dumps({"id": settings['user_id'], "first": 12, "after": settings['cursor']}, separators=(',', ':'))
    signature = hashlib.md5(f'{settings["rhx_gis"]}:{var}'.encode()).hexdigest()

    next_url = f'{BASE_QUERY}?query_hash={QUERY_ID}&variables=%7B%22id%22%3A%22{settings["user_id"]}' \
               f'%22%2C%22first%22%3A12%2C%22after%22%3A%22{quote_plus(settings["cursor"])}%22%7D'

    response = requests.get(next_url, headers={'x-instagram-gis': signature, 'x-requested-with': 'XMLHttpRequest','user-agent': USER_AGENT})
    print(response.status_code)
    if response.status_code == 200:
        js_data = response.json()
        download_photos.apply_async(args = [js_data['data']['user']['edge_owner_to_timeline_media']
                                            ['edges'],  settings['profile']])
        has_next_page = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        if has_next_page:
            settings['cursor'] = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            get_urls.apply_async(args = [settings])

@app.task()
def download_photos(data, user_pk):
    for i in data:
        p = requests.get(i['node']['display_url'])
        img = Photo(user_id=user_pk)
        img.img.save(img.user.name, content=ContentFile(p.content))

@app.task()
def make_zip(user):
    byte = BytesIO()
    zf = zipfile.ZipFile(byte, 'w')
    for f in Photo.objects.filter(user=user):
        zf.write(f.img.path, f.img.name.split('/')[-1])
    zf.close()
    ProfilePhotos.objects.get(id=user).zip.save(name=user, content=byte)

@app.task()
def download_complete_checker():
    profiles = ProfilePhotos.objects.filter(zip__exact='')
    for i in profiles:
        if Photo.objects.filter(user_id=i.pk).count() == i.count:
            make_zip.apply_async(args = [i.pk])

@app.task()
def delete_expired_photos():
    profiles = ProfilePhotos.objects.filter(add_date__lte=timezone.now() - timedelta(minutes=5))
    for profile in profiles:
        profile.delete()
