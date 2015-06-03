from django.conf.urls import patterns, url

from data import views
from django.views.generic import RedirectView

urlpatterns = patterns('',
	url(r'^$', RedirectView.as_view(url='/index/')),
    url(r'^index/', views.index, name='data.views.index'),
    url(r'^persons/', views.persons, name='data.views.persons'),
    url(r'^person/(?P<person_id>\d+)/', views.person, name='data.views.person'),
    url(r'^ancestries/', views.ancestries, name='data.views.ancestries'),
    url(r'^ancestry/(?P<ancestry_id>\d+)/', views.ancestry, name='data.views.ancestry'),
    url(r'^ancestry_export/(?P<ancestry_id>\d+)/', views.ancestry_export, name='data.views.ancestry_export'),
    url(r'^location/(?P<location_id>\d+)/', views.location, name='data.views.location'),
    url(r'^distributions/', views.distributions, name='data.views.distributions'),
    url(r'^export/ancestry/(?P<ancestry_id>\d+)/', views.export, name='data.views.export'),
    url(r'^person/dot_tree/(?P<person_id>\d+)/', views.dot_tree, name='data.views.dot_tree'),
)