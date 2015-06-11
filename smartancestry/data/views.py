from django.shortcuts import render

from django.http import HttpResponse
from data.models import Person, Ancestry, Location
from django.template import RequestContext, loader
from django.utils import translation
from random import randint
from operator import attrgetter
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def index(request):
    template = loader.get_template('data/index.html')
    context = RequestContext(request, { })
    return HttpResponse(template.render(context))
    
def persons(request):
    persons_list = Person.objects.all
    template = loader.get_template('data/persons.html')
    context = RequestContext(request, {
        'persons_list': persons_list,
    })
    return HttpResponse(template.render(context))
    
def person(request, person_id):
	try:
		person = Person.objects.get(pk=person_id)
	except Person.DoesNotExist:
		raise Http404("Person does not exist")
		
	all_persons = Person.objects.all()
	random_person = all_persons[randint(0, len(all_persons) - 1)]
	female_persons = Person.objects.filter(sex = 'F')
		
	template = loader.get_template('data/person.html')
	context = RequestContext(request, {
		'person': person,
		'random': random_person,
		'number_of_persons' : len(all_persons),
		'number_of_female_persons' : len(female_persons),
		'number_of_male_persons' : len(all_persons) - len(female_persons)
	})
	return HttpResponse(template.render(context))
	
def ancestries(request):
	ancestries_list = Ancestry.objects.all
	template = loader.get_template('data/ancestries.html')
	context = RequestContext(request, {
		'ancestries_list': ancestries_list,
	})
	return HttpResponse(template.render(context))
	
def ancestry(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")
		
	template = loader.get_template('data/ancestry.html')
	context = RequestContext(request, {
		'ancestry': ancestry,
		'member_list': ancestry.members,
		'locations' : ancestry.locations,
		'statistics' : ancestry.statistics,
	})
	return HttpResponse(template.render(context))

def ancestry_export(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")
		
	sorted_members = ancestry.members()
	sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
	sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))
		
	template = loader.get_template('data/ancestry_export.html')
	context = RequestContext(request, {
		'ancestry': ancestry,
		'sorted_members': sorted_members,
		'member_list': ancestry.members(),
		'featured': ancestry.featured(),
		'distributions': ancestry.distributions(),
		'locations' : ancestry.locations,
		'statistics' : ancestry.statistics,
		'appendices' : ancestry.appendices,
	})
	return HttpResponse(template.render(context))

def dot_tree(request, person_id):
	try:
		person = Person.objects.get(pk=person_id)
	except Person.DoesNotExist:
		raise Http404("Person does not exist")
		
	all_persons = Person.objects.all()
		
	template = loader.get_template('data/dot_tree.html')
	context = RequestContext(request, {
		'person': person,
		'relatives': person.relatives(),
	})
	return HttpResponse(template.render(context))

def distributions(request):
	template = loader.get_template('data/distributions.html')
	context = RequestContext(request, { })
	return HttpResponse(template.render(context))

def location(request, location_id):
	try:
		location = Location.objects.get(pk=location_id)
	except Location.DoesNotExist:
		raise Http404("Location does not exist")
		
	template = loader.get_template('data/location.html')
	context = RequestContext(request, {
		'location': location,
		'member_list': location.members,
		'locations': Location.objects.all(),
	})
	return HttpResponse(template.render(context))
	
def export(request, ancestry_id):
	try:
		ancestry = Ancestry.objects.get(pk=ancestry_id)
	except Ancestry.DoesNotExist:
		raise Http404("Ancestry does not exist")
		
	import os
	os.system('prince --no-author-style --javascript -s http://127.0.0.1:8000/static/data/style_print.css http://127.0.0.1:8000/data/ancestry_export/%s/Kliemank -o tmp.pdf' % ancestry_id)
		
	image_data = open('tmp.pdf', "rb").read()
	return HttpResponse(image_data, content_type='application/pdf')
	
def person_image(request, person_id, person2_id):
	person_id = person2_id

	try:
		person = Person.objects.get(pk=person_id)
	except Person.DoesNotExist:
		raise Http404("Person does not exist")
	
	image_url = '/Users/mrommel/Prog/SmartAncestry/smartancestry/data%s' % (person.image.url)
	image_url = image_url.replace('media/media', 'media')
	logger.info('Load %s' % (image_url))
	image_data = open(image_url, "rb").read()
	response = HttpResponse(image_data, content_type="image/png")

	return response
		