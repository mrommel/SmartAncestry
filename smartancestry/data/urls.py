#!/usr/bin/env python3

from django.conf.urls import *
from . import views

# from django.views.generic import RedirectView

urlpatterns = [
    # url(r'^$', RedirectView.as_view(url='/index/')),
    url(r'^index/', views.index, name='data.views.index'),
    url(r'^persons/$', views.persons, name='data.views.persons'),
    url(r'^person/(?P<person_id>\d+)/', views.person, name='data.views.person'),
    url(r'^ancestries/', views.ancestries, name='data.views.ancestries'),

    # problems
    url(r'^ancestry/(?P<ancestry_id>\d+)/missing/images', views.missing_images, name='data.views.missing_images'),

    # stammbaum
    url(r'^ancestry/(?P<ancestry_id>\d+)/(.*)$', views.ancestry, name='data.views.ancestry'),

    # pdf export
    url(r'^ancestry_export/(?P<ancestry_id>\d+)/', views.ancestry_export, name='data.views.ancestry_export'),
    url(r'^ancestry_export_no_documents/(?P<ancestry_id>\d+)/', views.ancestry_export_no_documents, name='data.views.ancestry_export_no_documents'),
    url(r'^ancestry_questions/(?P<ancestry_id>\d+)/', views.ancestry_questions, name='data.views.ancestry_questions'),
    url(r'^ancestry_history/(?P<ancestry_id>\d+)/', views.ancestry_history, name='data.views.ancestry_history'),
    url(r'^ancestry_gedcom/(?P<ancestry_id>\d+)/', views.ancestry_gedcom, name='data.views.ancestry_gedcom'),
    url(r'^location/(?P<location_id>\d+)/', views.location, name='data.views.location'),
    url(r'^distributions/', views.distributions, name='data.views.distributions'),

    url(r'^export/ancestry/(?P<ancestry_id>\d+)/', views.export, name='data.views.export'),
    url(r'^export/ancestry_no_documents/(?P<ancestry_id>\d+)/', views.export_no_documents, name='data.views.export_no_documents'),
    url(r'^export/ancestry_questions/(?P<ancestry_id>\d+)/', views.export_questions, name='data.views.export_questions'),
    #url(r'^export/ancestry_history/(?P<ancestry_id>\d+)/', views.export_history, name='data.views.export_history'),

    url(r'^person/dot_tree/(?P<person_id>\d+)/(?P<max_level>\d+)/ancestry\.dot', views.dot_tree,
        name='data.views.dot_tree'),
    url(r'person_tree/(?P<person_id>\d+)/tree.svg', views.person_tree, name='data.views.person_tree'),
]
