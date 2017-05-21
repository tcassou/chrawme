# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.local, name='index'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^local/$', views.local, name='local_default'),
    url(r'^local/(?P<path>[\/\w\-\s]+)/$', views.local, name='local'),
    url(r'^local/show/(?P<path>[\/\w\-\s]+)/image_id/(?P<image_id>[0-9]+)[\/]*$', views.local_show, name='local_show'),
    url(r'^hubic/$', views.hubic, name='hubic_default'),
    url(r'^hubic/(?P<path>[\/\w\-\s]+)/$', views.hubic, name='hubic'),
    url(r'^hubic/show/(?P<path>[\/\w\-\s]+)/image_id/(?P<image_id>[0-9]+)[\/]*$', views.hubic_show, name='hubic_show'),
]