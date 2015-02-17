from django.shortcuts import render

from django.http import HttpResponse
from data.models import Person, Ancestry, Location
from django.template import RequestContext, loader
from django.utils import translation
from random import randint

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
		