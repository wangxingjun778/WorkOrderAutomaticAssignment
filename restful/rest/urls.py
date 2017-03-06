#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
admin.autodiscover()

from api import views

urlpatterns = [
    url(r'^para/$', views.para, name='para'),
    #url(r'^predict/$', views.predict, name='predict'),
    url(r'^admin/', admin.site.urls),
]
