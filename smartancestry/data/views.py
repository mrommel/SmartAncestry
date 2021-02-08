import io
import logging
import os
import subprocess
import urllib

from django.db.models import Q
from django.utils.encoding import smart_bytes
from django.utils.translation import ugettext as _
from operator import attrgetter
from random import randint

from django.utils.safestring import mark_safe

from .classes import GedcomExternPerson, GedcomExternMember, GedcomFamily
from .models import Person, Ancestry, Location, FamilyStatusRelation
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
            questions.append(mark_safe(question))

        for question in member.person.automatic_questions():
            questions.append(mark_safe(question))

    members = []
    for member in ancestry.members():
        template_value1 = ''
        if ancestry.featured:
            relation = ancestry_relation(member.person, ancestry.featured)

            if relation is not None:
                if template_value1 == '':
                    template_value1 = '%s %s %s' % (relation, _('of'), ancestry.featured.full_name())
                else:
                    template_value1 = template_value1 + '<br />' + '%s %s %s' % (relation, _('of'), ancestry.featured.full_name())

        member.person.template_value1 = mark_safe(template_value1)

        members.append(member)

    featured = ancestry.featured
    person_trees = ancestry.person_trees()
    ancestry_distributions = ancestry.distributions()
    ancestry_documents = ancestry.ancestry_documents()
    person_documents = ancestry.documents()

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    if request.GET.get('documents') is None:
        include_documents = False
    else:
        include_documents = True

    return HttpResponse(render_to_string('data/ancestry_export.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'member_list': members,
        'featured': featured,
        'person_trees': person_trees,
        'distributions': ancestry_distributions,
        'locations': ancestry.locations,
        'statistics': ancestry.statistics,
        'questions': questions,
        'ancestry_documents': ancestry_documents,
        'person_documents': person_documents,
        'include_css': include_css,
        'include_documents': include_documents,
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

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    return HttpResponse(render_to_string('data/ancestry_questions.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
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


def person_export(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    return HttpResponse(render_to_string('data/person_export.html', {
        'person': person,
        'include_css': include_css
    }))


def ancestry_gedcom(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    sorted_members = ancestry.members()
    sorted_members = sorted(sorted_members, key=attrgetter('person.first_name'))
    sorted_members = sorted(sorted_members, key=attrgetter('person.last_name'))

    # add extern parents as fake persons
    for member in sorted_members:
        if member.person.father_extern and not member.person.father_extern == '':
            name_parts = member.person.father_extern.split(' ')
            if len(name_parts) == 1:
                first_name = member.person.father_extern
                last_name = member.person.last_name
            elif len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                first_name = " ".join(name_parts[0:(len(name_parts) - 2)])
                last_name = name_parts[len(name_parts) - 1]

            fake_person = GedcomExternPerson(str(int(member.person.id) * 1000), 'M', first_name, last_name)
            fake_member = GedcomExternMember(fake_person)

            sorted_members.append(fake_member)

        if member.person.mother_extern and not member.person.mother_extern == '':
            name_parts = member.person.mother_extern.split(' ')
            if len(name_parts) == 1:
                first_name = member.person.mother_extern
                last_name = member.person.last_name
            elif len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                first_name = " ".join(name_parts[0:(len(name_parts) - 2)])
                last_name = name_parts[len(name_parts) - 1]

            fake_person = GedcomExternPerson(str(int(member.person.id) * 1000 + 1), 'F', first_name, last_name)
            fake_member = GedcomExternMember(fake_person)

            sorted_members.append(fake_member)

    relations = []
    fake_relations_counter = 3000
    for member in sorted_members:
        member_relations = []
        if member.person.sex == 'M':
            if not isinstance(member, GedcomExternMember):
                for relation in FamilyStatusRelation.objects.filter(man=member.person):
                    children_list = Person.objects.filter(Q(father=member.person) & Q(mother=relation.woman))
                    children_list = sorted(children_list, key=attrgetter('birth_date'), reverse=False)

                    member_relations.append(relation.id)

                    if relation.date:
                        if relation.date_only_year:
                            date_str = relation.date.strftime("%Y")
                        else:
                            date_str = relation.date.strftime("%d %b %Y")
                    else:
                        date_str = None
                    relations.append(GedcomFamily(relation.id, 'M', member.person, relation.woman, children_list, date_str, relation.location))

        member.ged_data = []

        member.ged_data.append('0 @P%s@ INDI' % member.person.id)
        if not member.person.birth_date_unclear:
            member.ged_data.append('1 BIRT')
            if member.person.birth_date_only_year:
                member.ged_data.append('2 DATE %s' % member.person.birth_date.strftime("%Y"))
            else:
                member.ged_data.append('2 DATE %s' % member.person.birth_date.strftime("%d %b %Y"))

            if member.person.birth_location:
                member.ged_data.append('2 PLAC %s' % member.person.birth_location)

        if member.person.death_date:
            member.ged_data.append('1 DEAT ')
            if member.person.death_date_only_year:
                member.ged_data.append('2 DATE %s' % member.person.death_year())
            else:
                member.ged_data.append('2 DATE %s' % member.person.death_date.strftime("%d %b %Y"))

            if member.person.death_location:
                member.ged_data.append('2 PLAC %s' % member.person.death_location)

        member.ged_data.append('1 SEX %s' % member.person.sex)

        if member.person.birth_name and len(member.person.birth_name) > 0:
            member.ged_data.append(
                '1 NAME %s /%s/' % (member.person.first_name.replace("_", ""), member.person.birth_name))
        else:
            member.ged_data.append(
                '1 NAME %s /%s/' % (member.person.first_name.replace("_", ""), member.person.last_name))

    # make sure also extern parents get families
    for member in sorted_members:
        if member.person.father_extern and not member.person.father_extern == '' and member.person.mother_extern and not member.person.mother_extern == '':
            name_parts = member.person.father_extern.split(' ')
            if len(name_parts) == 1:
                first_name = member.person.father_extern
                last_name = member.person.last_name
            elif len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                first_name = " ".join(name_parts[0:(len(name_parts) - 2)])
                last_name = name_parts[len(name_parts) - 1]

            fake_father = GedcomExternPerson(str(int(member.person.id) * 1000), 'M', first_name, last_name)

            name_parts = member.person.mother_extern.split(' ')
            if len(name_parts) == 1:
                first_name = member.person.mother_extern
                last_name = member.person.last_name
            elif len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                first_name = " ".join(name_parts[0:(len(name_parts) - 2)])
                last_name = name_parts[len(name_parts) - 1]

            fake_mother = GedcomExternPerson(str(int(member.person.id) * 1000 + 1), 'F', first_name, last_name)

            relations.append(GedcomFamily(fake_relations_counter, 'K', fake_father, fake_mother, [member.person], None,
                                          None))
            fake_relations_counter = fake_relations_counter + 1

    # add relation ref to each child
    # todo: consider external parents
    for relation in relations:
        for child in relation.children:
            for member in sorted_members:
                if child.id == member.person.id:
                    member.ged_data.append('1 FAMC @F%s@' % relation.id)

        for member in sorted_members:
            if relation.husband:
                if relation.husband.id == member.person.id:
                    member.ged_data.append('1 FAMS @F%s@' % relation.id)

            if relation.wife:
                if relation.wife.id == member.person.id:
                    member.ged_data.append('1 FAMS @F%s@' % relation.id)

    for relation in relations:
        relation.ged_data = []

        if relation.husband and relation.wife:

            relation.ged_data.append('0 @F%s@ FAM' % relation.id)
            relation.ged_data.append('1 HUSB @P%s@' % relation.husband.id)
            relation.ged_data.append('1 WIFE @P%s@' % relation.wife.id)

            for child in relation.children:
                relation.ged_data.append('1 CHIL @P%s@' % child.id)

            if relation.type == 'M':
                relation.ged_data.append('1 MARR')

            if relation.date:
                relation.ged_data.append('2 DATE %s' % relation.date)

                if relation.location:
                    relation.ged_data.append('2 PLAC %s' % relation.location)

    return HttpResponse(render_to_string('data/ancestry_gedcom.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'relations': relations
    }), content_type='application/x-gedcomx-v1+xml')


def dot_tree(request, person_id, max_level):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    relatives = person.relatives_parents(0, [], [], [], int(max_level))
    relatives = person.relatives_children(0, relatives.relatives, relatives.relations, relatives.connections)

    image_path = os.path.realpath(os.path.dirname(__file__))

    return HttpResponse(render_to_string('data/dot_tree.html', {
        'person_id': person_id,
        'max_level': max_level,
        'person': person,
        'relatives': relatives,
        'image_path': image_path
    }))


def tree_image(request, person_id, max_level):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    relatives = person.relatives_parents(0, [], [], [], int(max_level))
    relatives = person.relatives_children(0, relatives.relatives, relatives.relations, relatives.connections)

    image_path = os.path.realpath(os.path.dirname(__file__))

    # prepare the dot file - later used as input for dot shell script
    dot_tree_str = render_to_string('data/dot_tree.html', {
        'person_id': person_id,
        'max_level': max_level,
        'person': person,
        'relatives': relatives,
        'image_path': image_path
    })

    # runs graphviz dot in shell
    # feed the dot file into stdin
    # get png on stdou
    # /usr/local/bin/dot -Tpng < stdin > stdout
    process = subprocess.Popen(['/usr/local/bin/dot', '-Tpng'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    stdout, stderr = process.communicate(smart_bytes(str(dot_tree_str)))

    return HttpResponse(smart_bytes(stdout), content_type='image/png')


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
            questions.append(mark_safe(question))

        for question in member.person.automatic_questions():
            questions.append(mark_safe(question))

    members = []
    for member in ancestry.members():
        template_value1 = ''
        if ancestry.featured:
            relation = ancestry_relation(member.person, ancestry.featured)

            if relation is not None:
                if template_value1 == '':
                    template_value1 = '%s %s %s' % (relation, _('of'), ancestry.featured.full_name())
                else:
                    template_value1 = template_value1 + '<br />' + '%s %s %s' % (relation, _('of'), ancestry.featured.full_name())

        member.person.template_value1 = mark_safe(template_value1)

        members.append(member)

    featured = ancestry.featured
    person_trees = ancestry.person_trees()
    ancestry_distributions = ancestry.distributions()
    ancestry_documents = ancestry.ancestry_documents()
    person_documents = ancestry.documents()

    # pdf export is always without css
    include_css = False

    if request.GET.get('documents') is None:
        include_documents = False
    else:
        include_documents = True

    ancestry_export_str = render_to_string('data/ancestry_export.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'member_list': members,
        'featured': featured,
        'person_trees': person_trees,
        'distributions': ancestry_distributions,
        'locations': ancestry.locations,
        'statistics': ancestry.statistics,
        'questions': questions,
        'ancestry_documents': ancestry_documents,
        'person_documents': person_documents,
        'include_css': include_css,
        'include_documents': include_documents,
        'MEDIA_URL': 'media/'
    })

    css_path = 'http://127.0.0.1:7000/static/data/style_print.css'

    # The command-line must contain the name of the input file to process. An input filename consisting of a single
    # hyphen "-" will cause Prince to read from the standard input stream.
    # The output file name can be specified on the command-line using the -o command-line option.
    # An output filename consisting of a single hyphen "-" will cause Prince to write to the standard output stream.
    process = subprocess.Popen(
        ['prince', '--no-author-style', '--javascript', '-s', css_path, '-', '-o', '-', '--baseurl=http://127.0.0.1:7000/', '--log=prince.log'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate(smart_bytes(str(ancestry_export_str)))

    return HttpResponse(smart_bytes(stdout), content_type='application/pdf')


def export_questions(request, ancestry_id):

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

    ancestry_questions_str = render_to_string('data/ancestry_questions.html', {
        'ancestry': ancestry,
        'sorted_members': sorted_members,
        'include_css': include_css
    })

    css_path = 'http://127.0.0.1:7000/static/data/style_print.css'

    # The command-line must contain the name of the input file to process. An input filename consisting of a single
    # hyphen "-" will cause Prince to read from the standard input stream.
    # The output file name can be specified on the command-line using the -o command-line option.
    # An output filename consisting of a single hyphen "-" will cause Prince to write to the standard output stream.
    process = subprocess.Popen(
        ['prince', '--no-author-style', '--javascript', '-s', css_path, '-', '-o', '-'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate(smart_bytes(str(ancestry_questions_str)))

    return HttpResponse(smart_bytes(stdout), content_type='application/pdf')


def export_person(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    if request.GET.get('with') is not None:
        include_css = True
    else:
        include_css = False

    person_export_str = render_to_string('data/person_export.html', {
        'person': person,
        'include_css': include_css
    })

    css_path = 'http://127.0.0.1:7000/static/data/style_print.css'

    # The command-line must contain the name of the input file to process. An input filename consisting of a single
    # hyphen "-" will cause Prince to read from the standard input stream.
    # The output file name can be specified on the command-line using the -o command-line option.
    # An output filename consisting of a single hyphen "-" will cause Prince to write to the standard output stream.
    process = subprocess.Popen(
        ['prince', '--no-author-style', '--javascript', '-s', css_path, '-', '-o', '-'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate(smart_bytes(str(person_export_str)))

    return HttpResponse(smart_bytes(stdout), content_type='application/pdf')


def person_image(request, person_id, person2_id):
    person_id = person2_id

    try:
        person_obj = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    image_url = '/Users/michael.rommel/Prog/SmartAncestry/smartancestry/data%s' % person_obj.image.url
    image_url = image_url.replace('media/media', 'media')
    image_data = open(image_url, "rb").read()
    response = HttpResponse(image_data, content_type="image/png")

    return response


def missing_images(request, ancestry_id):
    try:
        ancestry_obj = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    persons_list = ancestry_obj.no_image()
    return HttpResponse(render_to_string('data/missing_images.html', {'persons_list': persons_list, }))


def person_tree(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    return HttpResponse(render_to_string('data/person_tree.html', {
        'person': person,
    }), content_type='image/svg+xml')


def monthly_birth_death_statistics(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    data1_str = ancestry.statistics().birth_per_month_str().replace(' ', '')
    data2_str = ancestry.statistics().death_per_month_str().replace(' ', '')
    axis_str = '[%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s]' % (_('January'), _('February'), _('March'), _('April'), _('May'),
                                                        _('June'), _('July'), _('August'), _('September'), _('October'),
                                                        _('November'), _('December'))
    base_path = os.path.realpath(os.path.dirname(__file__))
    script_path = '%s%s' % (base_path, '/static/data/ancestry_statistics/bar.js')

    # logger.warning('%s %s %s %s %s' % ('node', script_path, axis_str, data1_str, data2_str))

    process = subprocess.Popen(
        ['node', script_path, axis_str, data1_str, data2_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    return HttpResponse(smart_bytes(stdout), content_type='image/png')


def gender_statistics(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    gender_str = ancestry.statistics().gender_values_str().replace(' ', '')
    base_path = os.path.realpath(os.path.dirname(__file__))
    script_path = '%s%s' % (base_path, '/static/data/ancestry_statistics/pie.js')

    # logger.warning('%s %s %s' % ('node', script_path, gender_str))

    process = subprocess.Popen(
        ['node', script_path, gender_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    return HttpResponse(smart_bytes(stdout), content_type='image/png')


def birth_location_statistics(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    birth_locations_values_str = ancestry.statistics().birth_locations_values_str().replace(' ', '')
    base_path = os.path.realpath(os.path.dirname(__file__))
    script_path = '%s%s' % (base_path, '/static/data/ancestry_statistics/pie.js')

    # logger.warning('%s %s %s' % ('node', script_path, gender_str))

    process = subprocess.Popen(
        ['node', script_path, birth_locations_values_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    return HttpResponse(smart_bytes(stdout), content_type='image/png')


def children_statistics(request, ancestry_id):
    try:
        ancestry = Ancestry.objects.get(pk=ancestry_id)
    except Ancestry.DoesNotExist:
        raise Http404("Ancestry does not exist")

    children_values_str = ancestry.statistics().children_values_str().replace(' ', '')
    children_number_str = '[0,1,2,3,4,5,6,7,8,9,10]'
    base_path = os.path.realpath(os.path.dirname(__file__))
    script_path = '%s%s' % (base_path, '/static/data/ancestry_statistics/bar.js')

    # logger.warning('%s %s %s %s' % ('node', script_path, children_values_str, children_number_str))

    process = subprocess.Popen(
        ['node', script_path, children_number_str, children_values_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    return HttpResponse(smart_bytes(stdout), content_type='image/png')
