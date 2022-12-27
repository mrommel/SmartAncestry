#!/usr/bin/env python3

from django.urls import path

from . import views

urlpatterns = [
    # url(r'^$', RedirectView.as_view(url='/index/')),
    path('index/', views.index, name='data.views.index'),
    path('persons/', views.persons, name='data.views.persons'),
    path('person/<int:person_id>/', views.person, name='data.views.person'),
    path('ancestries/', views.ancestries, name='data.views.ancestries'),

    # problems
    path('ancestry/<int:ancestry_id>/missing/images', views.missing_images, name='data.views.missing_images'),

    # stammbaum
    path('ancestry/<int:ancestry_id>/(.*)', views.ancestry, name='data.views.ancestry'),

    # pdf export
    path('ancestry_export/<int:ancestry_id>/', views.ancestry_export, name='data.views.ancestry_export'),
    path('ancestry_questions/<int:ancestry_id>/', views.ancestry_questions, name='data.views.ancestry_questions'),
    path('ancestry_history/<int:ancestry_id>/', views.ancestry_history, name='data.views.ancestry_history'),
    path('ancestry_gedcom/<int:ancestry_id>/', views.ancestry_gedcom, name='data.views.ancestry_gedcom'),
    path('location/<int:location_id>/', views.location, name='data.views.location'),
    path('distributions/', views.distributions, name='data.views.distributions'),
    path('person_export/<int:person_id>/', views.person_export, name='data.views.person_export'),

    path('export/ancestry/<int:ancestry_id>/', views.export, name='data.views.export'),
    path(
        'export/ancestry_questions/<int:ancestry_id>/',
        views.export_questions,
        name='data.views.export_questions'
    ),
    path('export/person/<int:person_id>/', views.export_person, name='data.views.export_person'),

    path(
        'person/dot_tree/<int:person_id>/<int:max_level>/ancestry.dot',
        views.dot_tree,
        name='data.views.dot_tree'
    ),
    path(
        'person/tree_image/<int:person_id>/<int:max_level>/tree.png',
        views.tree_image,
        name='data.views.tree_image'
    ),
    path(
        'person_tree/<int:person_id>/tree.svg',
        views.person_tree,
        name='data.views.person_tree'
    ),

    path(
        'statistics/<int:ancestry_id>/gender.png',
        views.gender_statistics,
        name='data.views.gender_statistics'
    ),
    path(
        'statistics/<int:ancestry_id>/monthly_birth_death.png',
        views.monthly_birth_death_statistics,
        name='data.views.monthly_birth_death_statistics'
    ),
    path(
        'statistics/<int:ancestry_id>/birth_locations.png',
        views.birth_location_statistics,
        name='data.views.birth_location_statistics'
    ),
    path(
        'statistics/<int:ancestry_id>/children.png',
        views.children_statistics,
        name='data.views.children_statistics'
    ),
]
