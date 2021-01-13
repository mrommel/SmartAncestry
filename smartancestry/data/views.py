import logging
import os
import urllib
from django.utils.translation import ugettext as _
from operator import attrgetter
from random import randint

from django.utils.safestring import mark_safe

from .models import Person, Ancestry, Location
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string

# Get an instance of a logger
from .tools import ancestry_relation

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse(render_to_string('data/index.html', {}))


def persons(request):
    persons_list = Person.objects.all
    return HttpResponse(render_to_string('data/persons.html', {'persons_list': persons_list, }))


def person(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    all_persons = Person.objects.all()
    random_person = all_persons[randint(0, len(all_persons) - 1)]
    female_persons = Person.objects.filter(sex='F')

    return HttpResponse(render_to_string('data/person.html', {
        'person': person,
        'random': random_person,
        'number_of_persons': len(all_persons),
        'number_of_female_persons': len(female_persons),
        'number_of_male_persons': len(all_persons) - len(female_persons)
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
        'locations': ancestry.locations,
        'statistics': ancestry.statistics,
    }))


def ancestry_export(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    sorted_members = ancestry.members()
    sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
    sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))

    questions = []
    for member in sorted_members:
        for question in member.person.questions():
            questions.append(question)

    members = []
    for member in ancestry.members():
        template_value1 = ''
        for featured_person in ancestry.featured():
            relation = ancestry_relation(member.person, featured_person.person)

            if relation is not None:
                if template_value1 == '':
                    template_value1 = '%s %s %s' % (relation, _('of'), featured_person.person.full_name())
                else:
                    template_value1 = template_value1 + '<br />' + '%s %s %s' % (relation, _('of'), featured_person.person.full_name())

        member.person.template_value1 = mark_safe(template_value1)

        members.append(member)

    featured = ancestry.featured()
    ancestry_distributions = ancestry.distributions()
    ancestry_documents = ancestry.ancestry_documents()
    person_documents = ancestry.documents()

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    return HttpResponse(render_to_string('data/ancestry_export.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'member_list': members,
        'featured': featured,
        'distributions': ancestry_distributions,
        'locations': ancestry.locations,
        'statistics': ancestry.statistics,
        'questions': questions,
        'ancestry_documents': ancestry_documents,
        'person_documents': person_documents,
        'include_css': include_css,
        'MEDIA_URL': 'media/'
    }))


def ancestry_questions(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    sorted_members = ancestry.members()
    sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
    sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))

    questions = []
    for member in sorted_members:
        for question in member.person.questions():
            questions.append(question)

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    return HttpResponse(render_to_string('data/ancestry_questions.html', {
        'ancestry': ancestry,
        'questions': questions,
        'include_css': include_css
    }))


def ancestry_history(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    sorted_members = ancestry.members()
    sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
    sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    return HttpResponse(render_to_string('data/ancestry_history.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'featured': ancestry.featured(),
        'distributions': ancestry.distributions(),
        'locations': ancestry.locations,
        'statistics': ancestry.statistics,
        'include_css': include_css
    }))


def ancestry_export_no_documents(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    sorted_members = ancestry.members()
    sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
    sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))

    members = []
    for member in ancestry.members():
        template_value1 = ''
        for featured_person in ancestry.featured():
            relation = ancestry_relation(member.person, featured_person.person)

            if relation is not None:
                if template_value1 == '':
                    template_value1 = '%s %s %s' % (relation, _('of'), featured_person.person.full_name())
                else:
                    template_value1 = template_value1 + '<br />' + '%s %s %s' % (relation, _('of'), featured_person.person.full_name())

        member.person.template_value1 = mark_safe(template_value1)

        members.append(member)

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    return HttpResponse(render_to_string('data/ancestry_export_no_documents.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'member_list': members,
        'featured': ancestry.featured(),
        'distributions': ancestry.distributions(),
        'locations': ancestry.locations,
        'statistics': ancestry.statistics,
        'include_css': include_css
    }))


def dot_tree(request, person_id, max_level):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    relatives = person.relatives_parents(0, [], [], [], int(max_level))
    relatives = person.relatives_children(0, relatives.relatives, relatives.relations, relatives.connections)

    return HttpResponse(render_to_string('data/dot_tree.html', {
        'person_id': person_id,
        'max_level': max_level,
        'person': person,
        'relatives': relatives,
    }))


def distributions(request):
    return HttpResponse(render_to_string('data/distributions.html', {}))


def location(request, location_id):
    try:
        location_obj = Location.objects.get(pk=location_id)
    except Location.DoesNotExist:
        raise Http404("Location does not exist")

    return HttpResponse(render_to_string('data/location.html', {
        'location': location_obj,
        'member_list': location_obj.members,
        'locations': Location.objects.all(),
    }))


def export(request, ancestry_id):
    os.system(
        "prince --no-author-style --javascript -s http://127.0.0.1:7000/static/data/style_print.css "
        "http://127.0.0.1:7000/data/ancestry_export/%s/Kliemank -o tmp.pdf" % ancestry_id)

    image_data = open('tmp.pdf', "rb").read()
    return HttpResponse(image_data, content_type='application/pdf')


def export_no_documents(request, ancestry_id):
    os.system(
        "prince --no-author-style --javascript -s http://127.0.0.1:7000/static/data/style_print.css "
        "http://127.0.0.1:7000/data/ancestry_export_no_documents/%s/Kliemank -o tmp.pdf" % ancestry_id)

    image_data = open('tmp.pdf', "rb").read()
    return HttpResponse(image_data, content_type='application/pdf')


def export_questions(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    path = "http://127.0.0.1:7000/data/ancestry_questions/%s/%s/ -o tmp.pdf" % (
    ancestry_id, urllib.quote(ancestry.name))

    # write html to tmp.pdf
    os.system(
        "prince --no-author-style --javascript -s http://127.0.0.1:7000/static/data/style_print.css %s" % path)

    pdf_data = open('tmp.pdf', "rb").read()
    return HttpResponse(pdf_data, content_type='application/pdf')


# def export_history

def person_image(request, person_id, person2_id):
    person_id = person2_id

    try:
        person_obj = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    image_url = '/Users/michael.rommel/Prog/SmartAncestry/smartancestry/data%s' % person_obj.image.url
    image_url = image_url.replace('media/media', 'media')
    logger.info('Load %s' % image_url)
    image_data = open(image_url, "rb").read()
    response = HttpResponse(image_data, content_type="image/png")

    return response


def missing_images(request, ancestry_id):
    try:
        ancestry_obj = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    persons_list = ancestry_obj.noImage()
    return HttpResponse(render_to_string('data/missing_images.html', {'persons_list': persons_list, }))
