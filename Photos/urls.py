from django.conf.urls import url
from django.urls import path

from Photos.views import requestView, get_archive, get_status, lab_3

urlpatterns = [
    path('', requestView.as_view(), name='start'),
    path('get-archive/<str:profile_nickname>/', get_archive, name='get_archive'),
    path('get-status/', get_status, name='get_status'),
    path('lab3/', lab_3, name= 'lab_3')
]