from django.shortcuts import render

from django.http import HttpResponse, Http404
from data.models import Person, Ancestry, Location, RelativesInfo
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.utils import translation
from random import randint
from operator import attrgetter
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse(render_to_string('data/index.html', {}))
    
def persons(request):
    persons_list = Person.objects.all
    return HttpResponse(render_to_string('data/persons.html', {'persons_list': persons_list,}))
    
def person(request, person_id):
	try:
		person = Person.objects.get(pk=person_id)
	except Person.DoesNotExist:
		raise Http404("Person does not exist")
		
	all_persons = Person.objects.all()
	random_person = all_persons[randint(0, len(all_persons) - 1)]
	female_persons = Person.objects.filter(sex = 'F')
		
	return HttpResponse(render_to_string('data/person.html', {
		'person': person,
		'random': random_person,
		'number_of_persons' : len(all_persons),
		'number_of_female_persons' : len(female_persons),
		'number_of_male_persons' : len(all_persons) - len(female_persons)
		}))
	
def ancestries(request):
	ancestries_list = Ancestry.objects.all
	return HttpResponse(render_to_string('data/ancestries.html', {
		'ancestries_list': ancestries_list,
		}))
	
def ancestry(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")
		
	return HttpResponse(render_to_string('data/ancestry.html', {
		'ancestry': ancestry,
		'member_list': ancestry.members,
		'locations' : ancestry.locations,
		'statistics' : ancestry.statistics,
		}))

def ancestry_export(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")
		
	sorted_members = ancestry.members()
	sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
	sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))
		
	members = []
	for member in ancestry.members():
		member.person.template_value1 = member.person.relation_in_str(ancestry)
		
		members.append(member)
		
	return HttpResponse(render_to_string('data/ancestry_export.html', {
		'ancestry': ancestry,
		'sorted_members': sorted_members,
		'member_list': members,
		'featured': ancestry.featured(),
		'distributions': ancestry.distributions(),
		'locations' : ancestry.locations,
		'statistics' : ancestry.statistics,
		'documents' : ancestry.documents,
	}))

def dot_tree(request, person_id):
	try:
		person = Person.objects.get(pk=person_id)
	except Person.DoesNotExist:
		raise Http404("Person does not exist")
		
	all_persons = Person.objects.all()
	
	relatives = person.relatives_parents(0, [], [], [])
	relatives = person.relatives_children(0, relatives.relatives, relatives.relations, relatives.connections)

	return HttpResponse(render_to_string('data/dot_tree.html', {
		'person': person,
		'relatives': relatives,
	}))

def distributions(request):
	return HttpResponse(render_to_string('data/distributions.html', { }))

def location(request, location_id):
	try:
		location = Location.objects.get(pk=location_id)
	except Location.DoesNotExist:
		raise Http404("Location does not exist")

	return HttpResponse(render_to_string('data/location.html', {
		'location': location,
		'member_list': location.members,
		'locations': Location.objects.all(),
	}))
	
def export(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")
		
	import os
	os.system('prince --no-author-style --javascript -s http://127.0.0.1:7000/static/data/style_print.css http://127.0.0.1:7000/data/ancestry_export/%s/Kliemank -o tmp.pdf' % ancestry_id)
		
	image_data = open('tmp.pdf', "rb").read()
	return HttpResponse(image_data, content_type='application/pdf')
	
def person_image(request, person_id, person2_id):
	person_id = person2_id

	try:
		person = Person.objects.get(pk=person_id)
	except Person.DoesNotExist:
		raise Http404("Person does not exist")
	
	image_url = '/Users/michael.rommel/Prog/SmartAncestry/smartancestry/data%s' % (person.image.url)
	image_url = image_url.replace('media/media', 'media')
	logger.info('Load %s' % (image_url))
	image_data = open(image_url, "rb").read()
	response = HttpResponse(image_data, content_type="image/png")

	return response
		
def missing_images(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")

	persons_list = ancestry.noImage()
	return HttpResponse(render_to_string('data/missing_images.html', { 'persons_list': persons_list, }))