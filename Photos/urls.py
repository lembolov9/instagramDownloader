from django.conf.urls import url
from django.urls import path

from Photos.views import requestView, get_archive, get_status

urlpatterns = [
    path('', requestView.as_view(), name='start'),
    path('get-archive/<str:profile_nickname>/', get_archive, name='get_archive'),
    path('get-status/', get_status, name='get_status')
]