#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import date
from itertools import chain, groupby
from operator import attrgetter

from django.db import models
from django.db.models import Q, CharField
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext
from typing import Tuple

from .tools import calculate_age, ancestry_relation, trim_and_unescape, underline_indices, ellipses, is_empty, nice_date

# Get an instance of a logger
logger = logging.getLogger(__name__)


class LocationInfo(object):

    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

    def lon_lat(self):
        return "{:10.4f}".format(self.lon) + ", " + "{:10.4f}".format(self.lat)


class Distribution(models.Model):
    """
		class of a distribution
	"""
    family_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/distributions', blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.family_name

    def __str__(self):
        return '%s' % self.family_name


class Location(models.Model):
    """
		class of a location with city, state and country

		meta information: image, longitude, latitude
	"""
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/locations', blank=True, null=True)
    lon = models.FloatField(default=0)
    lat = models.FloatField(default=0)

    def members(self):
        """
			list of all persons that share the same location
			- born here
			- died here
			- married etc here
		"""
        result_list = []
        for person in Person.objects.filter(birth_location=self):
            result_list.append(person)

        for person in Person.objects.filter(death_location=self):
            if person not in result_list:
                result_list.append(person)

        for familyStatusRelation in FamilyStatusRelation.objects.filter(location=self):
            if familyStatusRelation.man not in result_list:
                result_list.append(familyStatusRelation.man)

            if familyStatusRelation.woman not in result_list:
                result_list.append(familyStatusRelation.woman)

        return result_list

    def coordinate(self):
        return ('%f#%f' % (self.lat, self.lon)).replace(',', '.').replace('#', ',')

    def has_image(self):
        if self.image:
            return True
        return False

    def thumbnail(self):
        return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % (
            (self.image.name, self.image.name))

    thumbnail.allow_tags = True

    def map(self):
        return '<img border="0" alt="" src="https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static/pin-m-star+A6BCC6(%s)/%s,6/750x262@2x?access_token=pk.eyJ1IjoibXJvbW1lbDgyIiwiYSI6ImNramVtNzFrcTJsb2YycXJ1MnJkZjNtanIifQ._XmEx_GVTa9BZS4IppCJfg" height="262" width="750" />' % (
            (self.coordinate(), self.coordinate()))

    map.allow_tags = True

    # @models.permalink
    def get_absolute_url(self):
        return 'data.views.location', [str(self.id)]

    def __unicode__(self):
        return '%s (%s)' % (self.city, self.country)

    def __str__(self):
        return '%s (%s)' % (self.city, self.country)


class TreeInfo(object):
    def __init__(self, level, person, selected):
        self.level = level
        self.person = person
        self.selected = selected

    def info(self):
        id = self.person.id
        selected = self.selected
        sign = self.person.gender_sign()
        tmp = self.person.full_name()
        tmp = tmp.replace(u'\xe4', '&auml;')
        name = trim_and_unescape(str(tmp))
        indices = underline_indices(str(tmp))

        # born str construction
        if self.person.birth_date is not None:
            born = str('%s: %02d.%02d.%04d' % (
                _('Born'), self.person.birth_date.day, self.person.birth_date.month, self.person.birth_date.year))
        else:
            born = str('%s: ' % _('Born'))
        if self.person.birth_location is not None:
            born = born + ' ' + self.person.birth_location.city.encode('utf-8')
        born = ellipses(born, 32)

        # died str construction
        died = str('%s: ' % _('Died'))
        if self.person.death_date is not None:
            died = died + (' %02d.%02d.%04d' % (
                self.person.death_date.day, self.person.death_date.month, self.person.death_date.year))
        if self.person.death_location is not None:
            died = died + ' ' + self.person.death_location.city.encode('utf-8')
        died = ellipses(died, 32)

        return '{%d,%d,%d,\'%s %s\',%s,%s,%s}' % (id, self.level, selected, sign, name, indices, born, died)


class PartnerInfo(object):
    def __init__(self, status, partner, partner_name, location, date, date_year_only, state):
        self.status = status
        self.partner = partner
        self.partner_name = partner_name
        self.location = location
        self.date = date
        self.date_year_only = date_year_only
        self.state = state

    def date_str(self):
        if self.date_year_only:
            return self.date.year
        else:
            return '%02d.%02d.%04d' % (self.date.day, self.date.month, self.date.year)

    def __unicode__(self):
        return '[PartnerInfo: %s - dyo=%d,date:=%s' % (self.partner, self.date_year_only, self.date)

    def __str__(self):
        return '[PartnerInfo: %s - dyo=%d,date:=%s' % (self.partner, self.date_year_only, self.date)


class RelativesInfo(object):
    def __init__(self, relatives, relations, connections):
        self.relatives = relatives
        self.relations = relations
        self.connections = connections


class RelationsInfo(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination


class PersonInfo(object):
    def __init__(self, id, name, gender):
        self.id = id
        self.name = name
        self.sex = gender
        self.birth_date = None
        self.birth_location = None
        self.death_date = None
        self.death_location = None

    def full_name(self):
        return self.name.strip()

    def last_name(self):
        return self.name.strip()

    def gender_sign(self):
        if self.sex == 'M':
            return "♂"
        else:
            return "♀"


class MarriageInfo(object):
    def __init__(self, level, id, text):
        self.id = id
        self.level = level
        self.text = text


def name_of_ancestry(x):
    name = u'%s' % x.ancestry.name
    name = name.replace(u'ä', '&auml;')
    return mark_safe(name)


class PersonEventInfo(object):

    def __init__(self, date, age, title, summary, location):
        self.date = date
        self.age = age
        self.title = title
        self.summary = summary
        self.location = location


class Person(models.Model):
    """
		class of persons
	"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_name = models.CharField(max_length=50, blank=True, null=True)
    sex = models.CharField(max_length=1, choices=(('M', _('Male')), ('F', _('Female'))), verbose_name=_('Gender'))
    birth_date = models.DateField(_('date of birth'))
    birth_date_only_year = models.BooleanField(default=False)
    birth_date_unclear = models.BooleanField(default=False)
    birth_location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='birth_location')
    death_date = models.DateField(_('date of death'), null=True, blank=True)
    death_date_only_year = models.BooleanField(default=False)
    death_location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='death_location')
    cause_of_death = models.CharField(max_length=100, blank=True, null=True)
    already_died = models.NullBooleanField(default=False, blank=True, null=True)
    profession = models.CharField(max_length=50, blank=True, null=True)
    father = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True,
                               related_name='children_father')
    father_extern = models.CharField(max_length=200, blank=True, null=True)
    mother = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True,
                               related_name='children_mother')
    mother_extern = models.CharField(max_length=200, blank=True, null=True)
    children_extern = models.CharField(max_length=600, blank=True, null=True)
    siblings_extern = models.CharField(max_length=600, blank=True, null=True)  # type: CharField
    notes = models.CharField(max_length=500, blank=True, null=True)
    external_identifier = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='media/persons', blank=True, null=True)

    def user_name(self):
        return str(self)

    user_name.short_description = _('Name')

    def first_name_short(self):
        if not ' ' in self.first_name:
            return self.first_name

        result_list = self.first_name.split(' ')

        for x in range(0, len(result_list)):
            if not '_' in result_list[x] and len(result_list[x]) > 0:
                result_list[x] = result_list[x][0] + '.'

        return ' '.join(result_list)

    def first_name_nice(self):
        first = self.first_name_short()
        first = first.replace(u'\xfc', '&uuml;')
        first = first.replace(u'\xf6', '&ouml;')
        first = first.replace(u'\xe4', '&auml;')
        first = first.replace('0xc3', 'A')
        return ('%s' % (' ' + str(first) + ' ').replace(" _", " <u>").replace("_ ", "</u> ")).strip()

    def full_name(self):
        first = self.first_name_short()
        first = first.replace(u'\xfc', '&uuml;')
        first = first.replace(u'\xf6', '&ouml;')
        first = first.replace(u'\xe4', '&auml;')
        first = first.replace('0xc3', 'A')
        return ('%s %s' % (
            (' ' + str(first) + ' ').replace(" _", " <u>").replace("_ ", "</u> "), self.last_name)).strip()

    def female(self):
        return self.sex == 'F'

    def male(self):
        return self.sex == 'M'

    def gender_sign(self):
        if self.sex == 'M':
            return "♂"
        else:
            return "♀"

    def birth(self):
        if self.birth_date_unclear:
            birth_date_str = '???'
        else:
            birth_date_str = nice_date(self.birth_date, self.birth_date_only_year)

        birth_str = self.birth_location
        if birth_str is None:
            birth_str = '---'
        return mark_safe('%s<br>%s' % (birth_date_str, birth_str))

    def birth_no_year(self):
        if self.birth_date_unclear:
            return ''
        if self.birth_date is None:
            return ''
        return "%s.%s." % ('{0.day:02d}'.format(self.birth_date), '{0.month:02d}'.format(self.birth_date))

    def birth_year(self):
        if self.birth_date_unclear:
            return '???'
        if self.birth_date is None:
            return '---'
        return '{0.year:4d}'.format(self.birth_date)

    def birth_summary(self):

        birth_date_str = nice_date(self.birth_date, self.birth_date_only_year)

        if self.birth_date_unclear:
            birth_date_str = '???'

        if self.father and self.mother:
            age_father = calculate_age(self.father.birth_date, self.birth_date)
            age_mother = calculate_age(self.mother.birth_date, self.birth_date)

            if self.male():
                if self.birth_location:
                    first_sentence = _(
                        '%s was born on %s in %s as son of %s (%s years old) and his mother %s (%s years old).') % (
                                         self.full_name(), birth_date_str, self.birth_location,
                                         self.father.first_name_nice(),
                                         age_father, self.mother.first_name_nice(), age_mother)
                else:
                    first_sentence = _(
                        '%s was born on %s as son of %s (%s years old) and his mother %s (%s years old).') % (
                                         self.full_name(), birth_date_str, self.father.first_name_nice(), age_father,
                                         self.mother.first_name_nice(), age_mother)
            else:
                if self.birth_location:
                    first_sentence = _(
                        '%s was born on %s in %s as daughter of %s (%s years old) and her mother %s (%s years old).') % (
                                         self.full_name(), birth_date_str, self.birth_location,
                                         self.father.first_name_nice(),
                                         age_father, self.mother.first_name_nice(), age_mother)
                else:
                    first_sentence = _(
                        '%s was born on %s as daughter of %s (%s years old) and her mother %s (%s years old).') % (
                                         self.full_name(), birth_date_str, self.father.first_name_nice(), age_father,
                                         self.mother.first_name_nice(), age_mother)
        else:
            father_name_str = self.father_name()
            mother_name_str = self.mother_name()

            if father_name_str and mother_name_str:
                if self.male():
                    if self.birth_location:
                        first_sentence = _('%s was born as son of %s and %s on %s in %s.') % (
                            self.full_name(), father_name_str, mother_name_str, birth_date_str, self.birth_location)
                    else:
                        first_sentence = _('%s was born as son of %s and %s on %s.') % (
                            self.full_name(), father_name_str, mother_name_str, birth_date_str)
                else:
                    if self.birth_location:
                        first_sentence = _('%s was born as daughter of %s and %s on %s in %s.') % (
                            self.full_name(), father_name_str, mother_name_str, birth_date_str, self.birth_location)
                    else:
                        first_sentence = _('%s was born as daughter of %s and %s on %s.') % (
                            self.full_name(), father_name_str, mother_name_str, birth_date_str)
            else:
                if self.birth_location:
                    first_sentence = _('%s was born on %s in %s.') % (
                        self.full_name(), birth_date_str, self.birth_location)
                else:
                    first_sentence = _('%s was born on %s.') % (self.full_name(), birth_date_str)

        return mark_safe(first_sentence)

    def death(self):

        if self.death_date is None:
            date_str = '-'
        else:
            date_str = nice_date(self.death_date, self.death_date_only_year)

        death_str = self.death_location
        if death_str is None:
            death_str = '-'
        age_str = self.age()
        if age_str is None:
            age_str = '-'
        return mark_safe('%s<br />%s<br />%s %s' % (date_str, death_str, age_str, _('years')))

    def death_no_year(self):
        if self.death_date is None:
            return ''
        return "%s.%s." % ('{0.day:02d}'.format(self.death_date), '{0.month:02d}'.format(self.death_date))

    def death_year(self):
        if self.death_date is None and self.already_died:
            return '???'

        if self.death_date is None:
            return ''

        return '{0.year:4d}'.format(self.death_date)

    def show_dead(self):
        if self.already_died:
            return True

        if self.death_date is not None:
            return True

        return False

    def father_name(self):
        if self.father is not None:
            return str(self.father)
        else:
            return self.father_extern

    def father_name_linked(self):
        if self.father is not None:
            return self.father_link()
        else:
            return self.father_extern

    def mother_name(self):
        if self.mother is not None:
            return str(self.mother)
        else:
            return self.mother_extern

    def mother_name_linked(self):
        if self.mother is not None:
            return self.mother_link()
        else:
            return self.mother_extern

    def thumbnail(self):
        if self.image.name is not None and self.image.name != '':
            return mark_safe('<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % (
                (self.image.name, self.image.name)))
        else:
            return mark_safe('<img border="0" alt="" src="/static/data/images/Person-icon-grey.JPG" height="40" />')

    thumbnail.allow_tags = True

    def admin_url(self):
        return mark_safe('<a href="%s">%s</a>' % (self.id, self.full_name))

    admin_url.allow_tags = True

    def father_link(self):
        if self.father is not None:
            return mark_safe('<a href="/admin/data/person/%s/">%s</a>' % (self.father.id, str(self.father)))
        else:
            return ''

    father_link.allow_tags = True

    def mother_link(self):
        if self.mother is not None:
            return mark_safe('<a href="/admin/data/person/%s/">%s</a>' % (self.mother.id, str(self.mother)))
        else:
            return ''

    mother_link.allow_tags = True

    def tree_link(self):
        short_tree_link = '<a href="http://127.0.0.1:4446/ancestry.png?person=%s&max_level=2" target="_blank">Short Tree</a>' % self.id
        full_tree_link = '<a href="http://127.0.0.1:4446/ancestry.png?person=%s&max_level=8" target="_blank">Full Tree</a>' % self.id
        raw_tree_link = '<a href="view-source:http://127.0.0.1:8000/data/person/dot_tree/%s/2/ancestry.dot" target="_blank">Raw Tree</a>' % self.id
        return mark_safe('%s / %s / %s' % (short_tree_link, full_tree_link, raw_tree_link))

    tree_link.allow_tags = True

    def events(self):

        event_list = []

        # birth
        if not self.birth_date_unclear:
            event_list.append(
                PersonEventInfo(self.birth_date, -1, _("Birth"), self.birth_summary(), self.birth_location))

        # birth/death of children
        for child in self.children():
            age = calculate_age(self.birth_date, child.birth_date)
            if child.male():
                birth_child_title = _('Birth of son')
                if child.birth_location:
                    if self.male():
                        birth_child_summary = _('His son %s was born %s in %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year),
                            child.birth_location)
                    else:
                        birth_child_summary = _('Her son %s was born %s in %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year),
                            child.birth_location)
                else:
                    if self.male():
                        birth_child_summary = _('His son %s was born %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year))
                    else:
                        birth_child_summary = _('Her son %s was born %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year))
            else:
                birth_child_title = _('Birth of daughter')
                if child.birth_location:
                    if self.male():
                        birth_child_summary = _('His daughter %s was born %s in %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year),
                            child.birth_location)
                    else:
                        birth_child_summary = _('Her daughter %s was born %s in %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year),
                            child.birth_location)
                else:
                    if self.male():
                        birth_child_summary = _('His daughter %s was born %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year))
                    else:
                        birth_child_summary = _('Her daughter %s was born %s.') % (
                            child.first_name_nice(), nice_date(child.birth_date, child.birth_date_only_year))

            event_list.append(
                PersonEventInfo(child.birth_date, age, birth_child_title, mark_safe(birth_child_summary),
                                child.birth_location))

            show_death_of_child = False
            if child.death_date:
                show_death_of_child = True
            age = -1
            if self.death_date and child.death_date:
                if child.death_date > self.death_date:
                    show_death_of_child = False
                else:
                    age = calculate_age(self.birth_date, child.death_date)

            if show_death_of_child:
                if child.male():
                    death_child_title = _('Death of son')
                    death_date_str = nice_date(child.death_date, child.death_date_only_year)
                    if child.death_location:
                        if self.male():
                            death_child_summary = _('His son %s died at %s in %s.') % (
                                child.first_name_nice(), death_date_str, child.death_location)
                        else:
                            death_child_summary = _('Her son %s died at %s in %s.') % (
                                child.first_name_nice(), death_date_str, child.death_location)
                    else:
                        if self.male():
                            death_child_summary = _('His son %s died at %s.') % (
                                child.first_name_nice(), death_date_str)
                        else:
                            death_child_summary = _('Her son %s died at %s.') % (
                                child.first_name_nice(), death_date_str)
                else:
                    death_child_title = _('Death of daughter')
                    if child.death_location:
                        if self.male():
                            death_child_summary = _('His daughter %s died at %s in %s.') % (
                                child.first_name_nice(), death_date_str, child.death_location)
                        else:
                            death_child_summary = _('Her daughter %s died at %s in %s.') % (
                                child.first_name_nice(), death_date_str, child.death_location)
                    else:
                        if self.male():
                            death_child_summary = _('His daughter %s died at %s.') % (
                                child.first_name_nice(), death_date_str)
                        else:
                            death_child_summary = _('Her daughter %s died at %s.') % (
                                child.first_name_nice(), death_date_str)

                event_list.append(
                    PersonEventInfo(child.death_date, age, death_child_title, mark_safe(death_child_summary),
                                    child.death_location))

        # birth/death of siblings
        for sibling in self.siblings():
            age = calculate_age(self.birth_date, sibling.birth_date)
            sibling_birth_date_str = nice_date(sibling.birth_date, sibling.birth_date_only_year)

            if sibling.male():
                sibling_title = _('Birth of brother')

                if self.birth_location:
                    if self.male():
                        sibling_summary = _("His brother %s was born at %s in %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, sibling.birth_location,
                            self.first_name_nice(), age)
                    else:
                        sibling_summary = _("Her brother %s was born at %s in %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, sibling.birth_location,
                            self.first_name_nice(), age)
                else:
                    if self.male():
                        sibling_summary = _("His brother %s was born at %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, self.first_name_nice(), age)
                    else:
                        sibling_summary = _("Her brother %s was born at %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, self.first_name_nice(), age)
            else:
                sibling_title = _('Birth of sister')

                if self.birth_location:
                    if self.male():
                        sibling_summary = _("His sister %s was born at %s in %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, sibling.birth_location,
                            self.first_name_nice(), age)
                    else:
                        sibling_summary = _("Her sister %s was born at %s in %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, sibling.birth_location,
                            self.first_name_nice(), age)
                else:
                    if self.male():
                        sibling_summary = _("His sister %s was born at %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, sibling.first_name_nice(), age)
                    else:
                        sibling_summary = _("Her sister %s was born at %s, when %s was %d years old.") % (
                            sibling.first_name_nice(), sibling_birth_date_str, sibling.first_name_nice(), age)

            event_list.append(PersonEventInfo(sibling.birth_date, age, sibling_title, mark_safe(sibling_summary),
                                              sibling.birth_location))

            show_death_of_sibling = False
            if sibling.death_date:
                show_death_of_sibling = True
            age = -1
            if self.death_date and sibling.death_date:
                if sibling.death_date > self.death_date:
                    show_death_of_sibling = False
                else:
                    age = calculate_age(self.birth_date, sibling.death_date)

            if show_death_of_sibling:
                sibling_death_date_str = nice_date(sibling.death_date, sibling.death_date_only_year)

                if sibling.male():
                    sibling_title = _('Death of brother')

                    if self.death_location:
                        if self.male():
                            sibling_summary = _('His brother %s died at %s in %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, sibling.death_location,
                                self.first_name_nice(), age)
                        else:
                            sibling_summary = _('Her brother %s died at %s in %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, sibling.death_location,
                                self.first_name_nice(), age)
                    else:
                        if self.male():
                            sibling_summary = _('His brother %s died at %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, self.first_name_nice(), age)
                        else:
                            sibling_summary = _('Her brother %s died at %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, self.first_name_nice(), age)

                else:
                    sibling_title = _('Death of sister')

                    if self.death_location:
                        if self.male():
                            sibling_summary = _('His sister %s died at %s in %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, sibling.death_location,
                                self.first_name_nice(), age)
                        else:
                            sibling_summary = _('Her sister %s died at %s in %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, sibling.death_location,
                                self.first_name_nice(), age)
                    else:
                        if self.male():
                            sibling_summary = _('His sister %s died at %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, self.first_name_nice(), age)
                        else:
                            sibling_summary = _('Her sister %s died at %s, when %s was %d years old.') % (
                                sibling.first_name_nice(), sibling_death_date_str, self.first_name_nice(), age)

                event_list.append(
                    PersonEventInfo(sibling.death_date, age, sibling_title, mark_safe(sibling_summary),
                                    sibling.death_location))

        # marriage
        for familyStatusRelation in FamilyStatusRelation.objects.filter(
                Q(man=self) & Q(status='M') & (Q(ended=False) | Q(ended=None))):
            if familyStatusRelation.date:
                age = calculate_age(self.birth_date, familyStatusRelation.date)

                marriage_title = _('marriage')
                marriage_date_str = nice_date(familyStatusRelation.date, familyStatusRelation.date_only_year)

                if familyStatusRelation.location:
                    marriage_summary = _('%s married %s on %s at %s when he was %d years old.') % (
                        self.full_name(), familyStatusRelation.woman.full_name(), marriage_date_str,
                        familyStatusRelation.location, age)
                else:
                    marriage_summary = _('%s married %s on %s when he was %d years old.') % (
                        self.full_name(), familyStatusRelation.woman.full_name(), marriage_date_str, age)

                event_list.append(
                    PersonEventInfo(familyStatusRelation.date, age, marriage_title, mark_safe(marriage_summary),
                                    familyStatusRelation.location))

        for familyStatusRelation in FamilyStatusRelation.objects.filter(
                Q(woman=self) & Q(status='M') & (Q(ended=False) | Q(ended=None))):
            if familyStatusRelation.date:
                age = calculate_age(self.birth_date, familyStatusRelation.date)

                marriage_title = _('marriage')
                marriage_date_str = nice_date(familyStatusRelation.date, familyStatusRelation.date_only_year)

                if familyStatusRelation.location:
                    marriage_summary = _('%s married %s on %s at %s when she was %d years old.') % (
                        self.full_name(), familyStatusRelation.man.full_name(), marriage_date_str,
                        familyStatusRelation.location, age)
                else:
                    marriage_summary = _('%s married %s on %s when she was %d years old.') % (
                        self.full_name(), familyStatusRelation.man.full_name(), marriage_date_str, age)

            event_list.append(
                PersonEventInfo(familyStatusRelation.date, age, marriage_title, mark_safe(marriage_summary),
                                familyStatusRelation.location))

        # death of parents
        if self.father:
            show_death_of_father = False
            if self.father.death_date:
                show_death_of_father = True

            if self.death_date and self.father.death_date:
                if self.father.death_date > self.death_date:
                    show_death_of_father = False

            if show_death_of_father:
                death_father_title = _('Death of father')
                death_father_str = nice_date(self.father.death_date, self.father.death_date_only_year)
                age = calculate_age(self.birth_date, self.father.death_date)

                if self.father.death_location:
                    if self.male():
                        death_father_summary = _('His father %s died at %s in %s, when %s was %d years old.') % (
                            self.father.first_name_nice(), death_father_str, self.father.death_location,
                            self.first_name_nice(),
                            age)
                    else:
                        death_father_summary = _('Her father %s died at %s in %s, when %s was %d years old.') % (
                            self.father.first_name_nice(), death_father_str, self.father.death_location,
                            self.first_name_nice(),
                            age)
                else:
                    if self.male():
                        death_father_summary = _('His father %s died at %s, when %s was %d years old.') % (
                            self.father.first_name_nice(), death_father_str, self.first_name_nice(), age)
                    else:
                        death_father_summary = _('Her father %s died at %s, when %s was %d years old.') % (
                            self.father.first_name_nice(), death_father_str, self.first_name_nice(), age)

                event_list.append(
                    PersonEventInfo(self.father.death_date, age, death_father_title, mark_safe(death_father_summary),
                                    self.father.death_location))
        if self.mother:
            show_death_of_mother = False
            if self.mother.death_date:
                show_death_of_mother = True

            if self.death_date and self.mother.death_date:
                if self.mother.death_date > self.death_date:
                    show_death_of_mother = False

            if show_death_of_mother:
                death_mother_title = _('Death of mother')
                death_mother_str = nice_date(self.mother.death_date, self.mother.death_date_only_year)
                age = calculate_age(self.birth_date, self.mother.death_date)

                if self.mother.death_location:
                    if self.male():
                        death_mother_summary = _('His mother %s died at %s in %s, when %s was %d years old.') % (
                            self.mother.first_name_nice(), death_mother_str, self.mother.death_location,
                            self.first_name_nice(),
                            age)
                    else:
                        death_mother_summary = _('Her mother %s died at %s in %s, when %s was %d years old.') % (
                            self.mother.first_name_nice(), death_mother_str, self.mother.death_location,
                            self.first_name_nice(),
                            age)
                else:
                    if self.male():
                        death_mother_summary = _('His mother %s died at %s, when %s was %d years old.') % (
                            self.mother.first_name_nice(), death_mother_str, self.first_name_nice(), age)
                    else:
                        death_mother_summary = _('Her mother %s died at %s, when %s was %d years old.') % (
                            self.mother.first_name_nice(), death_mother_str, self.first_name_nice(), age)

                event_list.append(
                    PersonEventInfo(self.mother.death_date, age, death_mother_title, mark_safe(death_mother_summary),
                                    self.mother.death_location))

        # death
        if self.death_date:
            age = calculate_age(self.birth_date, self.death_date)

            death_title = _('Death')
            death_date_str = nice_date(self.death_date, self.death_date_only_year)

            if self.death_location:
                death_summary = _('%s died at %s in %s at the age of %d years.') % (
                    self.full_name(), death_date_str, self.death_location, age)
            else:
                death_summary = _('%s died at %s at the age of %d years.') % (self.full_name(), death_date_str, age)

            event_list.append(
                PersonEventInfo(self.death_date, age, death_title, mark_safe(death_summary), self.death_location))

        event_list = sorted(event_list, key=attrgetter('date'))

        return event_list

    def age(self):

        if self.birth_date_unclear:
            return None

        if self.death_date is None and not self.already_died:
            return calculate_age(self.birth_date, date.today())

        if self.death_date is None and self.already_died:
            return None

        return calculate_age(self.birth_date, self.death_date)

    def age_at_marriage(self):

        date_married = self.married_at()

        if date_married is None:
            return None

        return calculate_age(self.birth_date, date_married)

    def partner_relations(self):
        if self.sex == 'M':
            try:
                partners = []
                for relation in FamilyStatusRelation.objects.filter(man=self):
                    if relation.woman is not None:
                        partners.append(
                            PartnerInfo(relation.status_name, relation.woman, "", relation.location, relation.date,
                                        relation.date_only_year, relation.status))
                    else:
                        partners.append(PartnerInfo(relation.status_name, None, relation.wife_extern, relation.location,
                                                    relation.date, relation.date_only_year, relation.status))
                return partners
            except FamilyStatusRelation.DoesNotExist:
                pass

        if self.sex == 'F':
            try:
                partners = []
                for relation in FamilyStatusRelation.objects.filter(woman=self):
                    if relation.man is not None:
                        partners.append(
                            PartnerInfo(relation.status_name, relation.man, "", relation.location, relation.date,
                                        relation.date_only_year, relation.status))
                    else:
                        partners.append(
                            PartnerInfo(relation.status_name, None, relation.husband_extern, relation.location,
                                        relation.date, relation.date_only_year, relation.status))
                return partners
            except FamilyStatusRelation.DoesNotExist:
                pass

        return None

    def partner_names_linked(self):
        result = ''

        for partner_info in self.partner_relations():
            name_str = ''
            date_str = ''
            location_str = ''

            if partner_info.date:
                date_str = ' - ' + nice_date(partner_info.date, partner_info.date_year_only)

            if partner_info.partner is not None:
                name_str = mark_safe(
                    '<a href="/admin/data/person/%s/">%s</a>' % (partner_info.partner.id, str(partner_info.partner)))
            else:
                name_str = partner_info.partner_name

            if partner_info.location:
                location_str = ' - ' + str(partner_info.location)

            result = result + name_str + date_str + location_str + ", "

        return result

    partner_names_linked.allow_tags = True

    def siblings(self):
        if self.mother is None and self.father is None:
            return []

        if self.mother is None:
            return Person.objects.filter(father=self.father).exclude(id=self.id)

        if self.father is None:
            return Person.objects.filter(mother=self.mother).exclude(id=self.id)

        siblings_list = []
        siblings_list_mother = list(Person.objects.filter(mother=self.mother))
        siblings_list_father = list(Person.objects.filter(father=self.father))

        for sibling in chain(siblings_list_mother, siblings_list_father):
            if sibling not in siblings_list and sibling.id != self.id:
                siblings_list.append(sibling)

        siblings_list = sorted(siblings_list, key=attrgetter('birth_date'), reverse=False)

        return siblings_list

    def siblings_extern_list(self):
        if self.siblings_extern is not None and self.siblings_extern != '':
            return self.siblings_extern.split(',')

        return None

    def siblings_text(self):
        siblings_text_var = ''

        for sibling_item in self.siblings():
            siblings_text_var = "%s, %s" % (siblings_text_var, sibling_item.get_admin_url())

        if self.siblings_extern is not None:
            siblings_text_var = "%s, %s" % (siblings_text_var, self.siblings_extern)

        siblings_text_var = "$%s$" % siblings_text_var
        siblings_text_var = siblings_text_var.replace("$, ", "")
        siblings_text_var = siblings_text_var.replace(", $", "")
        siblings_text_var = siblings_text_var.replace("$", "")

        return mark_safe(siblings_text_var)

    siblings_text.allow_tags = True

    def children(self):
        children_list = Person.objects.filter(Q(father=self) | Q(mother=self))
        children_list = sorted(children_list, key=attrgetter('birth_date'), reverse=False)
        return children_list

    def children_extern_list(self):
        if self.children_extern == '-':
            return None

        if self.children_extern is not None and self.children_extern != '':
            return self.children_extern.split(',')

        return None

    def children_text(self):
        children_str = ''

        for children_item in self.children():
            children_str = "%s, %s" % (children_str, children_item.get_admin_url())

        if self.children_extern is not None:
            children_str = "%s, %s" % (children_str, self.children_extern)

        children_str = "$%s$" % (children_str)
        children_str = children_str.replace("$, ", "")
        children_str = children_str.replace(", $", "")
        children_str = children_str.replace("$", "")

        return mark_safe(children_str)

    children_text.allow_tags = True

    def children_count(self):
        count = len(self.children())

        if self.children_extern_list() is not None:
            count = count + len(self.children_extern_list())

        return count

    def ancestries(self):
        return AncestryRelation.objects.filter(person=self)

    def ancestry_names(self):
        ancestry_names_var = ''

        for item in map(name_of_ancestry, AncestryRelation.objects.filter(person=self)):
            ancestry_names_var = '%s, %s' % (ancestry_names_var, item)

        ancestry_names_var = "$%s$" % ancestry_names_var
        ancestry_names_var = ancestry_names_var.replace("$, ", "")
        ancestry_names_var = ancestry_names_var.replace(", $", "")
        ancestry_names_var = ancestry_names_var.replace("$", "")

        if ancestry_names_var == '':
            ancestry_names_var = '<span style="color: red;">%s</span>' % _("no ancestry")

        return mark_safe(ancestry_names_var)

    def has_ancestry(self, ancestry_id):
        for ancestryRelation in AncestryRelation.objects.filter(person=self):
            if ancestryRelation.id == ancestry_id:
                return True

        return False

    def married_to(self):
        """
			Returns the current partner (wife or husband) or None
		"""
        if self.sex == 'M':
            try:
                for husbandRelation in FamilyStatusRelation.objects.get(
                        Q(man=self) & Q(status='M') & (Q(ended=False) | Q(ended=None))):
                    return husbandRelation.woman
            except FamilyStatusRelation.DoesNotExist:
                pass

        if self.sex == 'F':
            try:
                for wifeRelation in FamilyStatusRelation.objects.get(
                        Q(woman=self) & Q(status='M') & (Q(ended=False) | Q(ended=None))):
                    return wifeRelation.man
            except FamilyStatusRelation.DoesNotExist:
                pass

        return None

    def wife(self):
        """
			Returns the current wife of the person or None
		"""
        if self.sex == 'M':
            for husbandRelation in FamilyStatusRelation.objects.filter(
                    Q(man=self) & Q(status='M') & (Q(ended=False) | Q(ended=None))):
                return husbandRelation.woman

        return None

    def husband(self):
        """
			Returns the current husband of the person or None
		"""
        if self.sex == 'F':
            for husbandRelation in FamilyStatusRelation.objects.filter(
                    Q(woman=self) & Q(status='M') & (Q(ended=False) | Q(ended=None))):
                return husbandRelation.man

        return None

    def partnership(self, partner):
        """
			Returns the partnership to partner or None if none exists
		"""
        for partnerRelation in FamilyStatusRelation.objects.filter(Q(woman=self) & Q(man=partner)):
            return partnerRelation

        for partnerRelation in FamilyStatusRelation.objects.filter(Q(woman=partner) & Q(man=self)):
            return partnerRelation

        return None

    def married_at(self):
        """
			Returns the date of the current partner relation
		"""
        relation = None

        if self.sex == 'M':
            relation_list = FamilyStatusRelation.objects.filter(
                Q(man=self) & Q(status='M') & (Q(ended=False) | Q(ended=None)))
            if len(relation_list) > 0:
                relation = relation_list[0]

        if self.sex == 'F':
            relation_list = FamilyStatusRelation.objects.filter(
                Q(woman=self) & Q(status='M') & (Q(ended=False) | Q(ended=None)))
            if len(relation_list) > 0:
                relation = relation_list[0]

        if relation is not None:
            return relation.date

        return None

    def relatives_parents(self, level, relatives_list, relations_list, connection_list, max_level):
        """
			iterate (with recursion) through the parents
		"""
        if len(list(filter(lambda x: x.person.id == self.id, relatives_list))) == 0:
            relatives_list.append(TreeInfo(level, self, 0))

        for partner in self.partner_relations():
            if partner.partner is not None and (
                    len(list(filter(lambda x: x.person == partner.partner, relatives_list))) == 0):
                partner.partner.relatives_parents(level, relatives_list, relations_list, connection_list, max_level)

                if self.sex == 'M':
                    marriage_id = "marriage_%s_%s" % (self.id, partner.partner.id)
                else:
                    marriage_id = "marriage_%s_%s" % (partner.partner.id, self.id)

                partnership = self.partnership(partner.partner)

                if partnership.date is not None:
                    relations_list.append(MarriageInfo(level, marriage_id, "∞ %s" % partnership.date))
                else:
                    relations_list.append(MarriageInfo(level, marriage_id, ""))

                if len(list(
                        filter(lambda x: x.source == self.id and x.destination == marriage_id, connection_list))) == 0:
                    connection_list.append(RelationsInfo(self.id, marriage_id))

                if (len(list(filter(lambda x: x.source == partner.partner.id and x.destination == marriage_id,
                                    connection_list))) == 0):
                    connection_list.append(RelationsInfo(partner.partner.id, marriage_id))

        if self.father is not None and level < max_level:
            self.father.relatives_parents(level + 1, relatives_list, relations_list, connection_list, max_level)

        if self.mother is not None and level < max_level:
            self.mother.relatives_parents(level + 1, relatives_list, relations_list, connection_list, max_level)

        if self.mother is not None and self.father is not None and level < max_level:
            marriage_id = "marriage_%s_%s" % (self.father.id, self.mother.id)

            if len(list(filter(lambda x: x.source == marriage_id and x.destination == self.id, connection_list))) == 0:
                connection_list.append(RelationsInfo(marriage_id, self.id))

        return RelativesInfo(relatives_list, relations_list, connection_list)

    def relatives_children(self, level, relatives_list, relations_list, connection_list):
        """
			iterate (with recursion) through the children
		"""
        if len(list(filter(lambda x: x.person.id == self.id, relatives_list))) == 0:
            relatives_list.append(TreeInfo(level, self, 0))

        for child in self.children():
            child.relatives_children(level - 1, relatives_list, relations_list, connection_list)

        for partner in self.partner_relations():
            if partner.partner is not None and (
                    len(list(filter(lambda x: x.person == partner.partner, relatives_list))) == 0):

                if len(list(filter(lambda x: x.person.id == partner.partner.id, relatives_list))) == 0:
                    relatives_list.append(TreeInfo(level, partner.partner, 0))

                if self.sex == 'M':
                    marriage_id = "marriage_%s_%s" % (self.id, partner.partner.id)
                else:
                    marriage_id = "marriage_%s_%s" % (partner.partner.id, self.id)

                partnership = self.partnership(partner.partner)

                if partnership.date is not None:
                    relations_list.append(MarriageInfo(level, marriage_id, "∞ %s" % partnership.date))
                else:
                    relations_list.append(MarriageInfo(level, marriage_id, ""))

                connection_list.append(RelationsInfo(self.id, marriage_id))
                connection_list.append(RelationsInfo(partner.partner.id, marriage_id))

        if self.father is not None and self.mother is not None:
            marriage_id = "marriage_%s_%s" % (self.father.id, self.mother.id)

            if len(list(filter(lambda x: x.source == marriage_id and x.destination == self.id, connection_list))) == 0:
                connection_list.append(RelationsInfo(marriage_id, self.id))

        return RelativesInfo(relatives_list, relations_list, connection_list)

    def relatives(self):
        """
			provides a list of relative as well as links between them
		"""
        relatives_list = []  # persons
        relations_list = []  # marriages
        connection_list = []  # links
        external_id = 1000

        if self.father is not None:
            if self.father.father is not None:
                relatives_list.append(TreeInfo(0, self.father.father, 0))
                connection_list.append(RelationsInfo(self.father.father.id, self.father.id))
            if self.father.mother is not None:
                relatives_list.append(TreeInfo(0, self.father.mother, 0))
                connection_list.append(RelationsInfo(self.father.mother.id, self.father.id))

            relatives_list.append(TreeInfo(1, self.father, 0))
            connection_list.append(RelationsInfo(self.father.id, self.id))

        if self.mother is not None:
            if self.mother.father is not None:
                relatives_list.append(TreeInfo(0, self.mother.father, 0))
                connection_list.append(RelationsInfo(self.mother.father.id, self.mother.id))
            if self.mother.mother is not None:
                relatives_list.append(TreeInfo(0, self.mother.mother, 0))
                connection_list.append(RelationsInfo(self.mother.mother.id, self.mother.id))

            relatives_list.append(TreeInfo(1, self.mother, 0))
            connection_list.append(RelationsInfo(self.mother.id, self.id))

        if self.mother_extern is not None and self.mother_extern != '':
            relatives_list.append(TreeInfo(1, PersonInfo(external_id, self.mother_extern, 'F'), 0))
            connection_list.append(RelationsInfo(external_id, self.id))
            external_id = external_id + 1

        if self.father_extern is not None and self.father_extern != '':
            relatives_list.append(TreeInfo(1, PersonInfo(external_id, self.father_extern, 'M'), 0))
            connection_list.append(RelationsInfo(external_id, self.id))
            external_id = external_id + 1

        relatives_list.append(TreeInfo(2, self, 1))

        for partner in self.partner_relations():

            if partner.partner is None:
                relatives_list.append(TreeInfo(2, PersonInfo(external_id, partner.partner_name, 'M'), 0))
                external_id = external_id + 1
            else:
                relatives_list.append(TreeInfo(2, partner.partner, 0))

                """ 
					check if partner is mother / father of children of current person 
				"""
                for partner_child in partner.partner.children():
                    for child in self.children():
                        if partner_child.id == child.id:
                            connection_list.append(RelationsInfo(partner.partner.id, child.id))

                if partner.partner.mother is not None:
                    if partner.partner.mother.father is not None:
                        relatives_list.append(TreeInfo(0, partner.partner.mother.father, 0))
                        connection_list.append(
                            RelationsInfo(partner.partner.mother.father.id, partner.partner.mother.id))
                    if partner.partner.mother.mother is not None:
                        relatives_list.append(TreeInfo(0, partner.partner.mother.mother, 0))
                        connection_list.append(
                            RelationsInfo(partner.partner.mother.mother.id, partner.partner.mother.id))

                    relatives_list.append(TreeInfo(1, partner.partner.mother, 0))
                    connection_list.append(RelationsInfo(partner.partner.mother.id, partner.partner.id))

                if partner.partner.father is not None:
                    if partner.partner.father.father is not None:
                        relatives_list.append(TreeInfo(0, partner.partner.father.father, 0))
                        connection_list.append(
                            RelationsInfo(partner.partner.father.father.id, partner.partner.father.id))
                    if partner.partner.father.mother is not None:
                        relatives_list.append(TreeInfo(0, partner.partner.father.mother, 0))
                        connection_list.append(
                            RelationsInfo(partner.partner.father.mother.id, partner.partner.father.id))

                    relatives_list.append(TreeInfo(1, partner.partner.father, 0))
                    connection_list.append(RelationsInfo(partner.partner.father.id, partner.partner.id))

        for child in self.children():
            relatives_list.append(TreeInfo(3, child, 0))
            connection_list.append(RelationsInfo(self.id, child.id))

            for grandchild in child.children():
                relatives_list.append(TreeInfo(4, grandchild, 0))
                connection_list.append(RelationsInfo(child.id, grandchild.id))

        return RelativesInfo(relatives_list, relations_list, connection_list)

    # create list of relations for tree
    # [(1,2);(3,1)]
    def relations_str(self):
        result_list = []
        for item in self.relatives().relations:
            result_list.append('%d+%d' % (item.source, item.destination))
        return str(result_list).replace(',', ';').replace('+', ',').replace(' ', '').replace('[\'', '[(').replace(
            '\';\'', ');(').replace('\']', ')]')

    def relatives_str(self):
        """
        creates a list of relatives for tree
        :return:
        """

        result_list = []
        for item in self.relatives().relatives:
            result_list.append(item.info())
        return mark_safe(str(result_list).replace('"', '').replace('}, {', '};{').replace(' ', '%20'))

    def relation_to_str(self, featured_person):

        return mark_safe(
            '%s %s %s' % (ancestry_relation(self, featured_person.person), _('of'), featured_person.person))

    relation_to_str.allow_tags = True

    def relation_in_str(self, ancestry):

        featured_person = ancestry.featured()[0]
        relation = ancestry_relation(self, featured_person.person)

        if relation is None:
            return None

        return mark_safe('%s %s %s' % (relation, _('of'), featured_person.person.full_name()))

    relation_in_str.allow_tags = True

    def relation_str(self):

        str_value = ''

        for ancestry in self.ancestries():
            if len(ancestry.ancestry.featured()) > 0:
                featured_person = ancestry.ancestry.featured()[0]
                str_value = '%s %s %s %s (%s %s)<br />' % (
                    str_value, ancestry_relation(self, featured_person.person), _('of'),
                    featured_person.person.get_admin_url(),
                    _('ancestry'), ancestry.ancestry)

        return mark_safe(str_value)

    relation_str.allow_tags = True

    # @models.permalink
    def get_absolute_url(self):
        return 'data.views.person', [str(self.id)]

    def get_admin_url(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a href="%s">%s</a>' % (url, self.__unicode__())

    def export_pdf(self):
        """
			todo: return a pdf of the persons cv
		"""
        pass

    def appendices(self):
        return DocumentRelation.objects.filter(person=self)

    def number_of_questions(self):
        return '%d / %d' % (
            len(Question.objects.filter(person=self).exclude(answer=None)), len(Question.objects.filter(person=self)))

    def questions(self):
        return Question.objects.filter(person=self)

    def automatic_questions(self):

        question_list = []

        if self.birth_date_only_year:
            if self.male():
                question_list.append(gettext(
                    "The exact birth date of %s is missing day and month. It is only clear that he was born in %s.") % (
                                         self.full_name(), self.birth_year()))
            else:
                question_list.append(gettext(
                    "The exact birth date of %s is missing day and month. It is only clear that she was born in %s.") % (
                                         self.full_name(), self.birth_year()))

        if self.birth_date_unclear:
            question_list.append(gettext("The birth date of %s is completely unclear. It is currently assumed ca. %s.") % (
                self.full_name(), self.birth_year()))

        if self.birth_location is None:
            question_list.append(gettext("The birth location of %s could not be determined.") % (self.full_name()))

        if self.father is None and self.father_extern == '':
            question_list.append(gettext("The father of %s could not be determined.") % (self.full_name()))

        if self.mother is None and self.mother_extern == '':
            question_list.append(gettext("The mother of %s could not be determined.") % (self.full_name()))

        # check if parents are in a relation
        if self.father is not None and self.mother is not None:
            found_link = False
            for _ in FamilyStatusRelation.objects.filter(Q(woman=self.mother) & Q(man=self.father)):
                found_link = True

            if not found_link:
                question_list.append(gettext("The parents of %s (%s and %s) are not linked.") % (
                    self.full_name(), self.father.full_name(), self.mother.full_name()))

        if self.death_date is None and self.already_died:
            question_list.append(gettext("The death date of %s is completely unclear.") % (self.full_name()))

        if self.death_date is not None or self.already_died:
            if self.death_location is None:
                question_list.append(gettext("The death location of %s could not be determined.") % (self.full_name()))

        if self.partner_relations():  # can be empty => None
            for relation in self.partner_relations():
                if relation.state == 'M':
                    if relation.partner:
                        partner_name = relation.partner.full_name()
                    else:
                        partner_name = relation.partner_name

                    if relation.date_year_only:
                        question_list.append(
                            gettext("The exact date of the marriage of %s and %s is unclear. It happened in %d.") % (
                                self.full_name(), partner_name, relation.date.year))

                    if relation.location is None:
                        question_list.append(
                            gettext("The location of the marriage of %s and %s is unclear.") % (
                                self.full_name(), partner_name))

        return question_list

    def automatic_questions_list(self):
        value = '<ul>'

        for automatic_question in self.automatic_questions():
            value = value + '<li>' + automatic_question + '</li>'

        value = value + '</ul>'

        return mark_safe(value)

    automatic_questions_list.allow_tags = True

    def is_alive(self):
        if self.already_died:
            return False

        if self.death_date is not None:
            return False

        return True

    def __unicode__(self):
        first = self.first_name
        first = first.replace(u'\xfc', '&uuml;')
        first = first.replace(u'\xf6', '&ouml;')
        first = first.replace(u'\xe4', '&auml;')

        if self.is_alive():
            date_str = '(geb. %s)' % self.birth_year()
        else:
            date_str = '(%s-%s)' % (self.birth_year(), self.death_year())

        return mark_safe('%s %s %s' % (
            (' ' + str(first) + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip(), self.last_name, date_str))

    def __str__(self):
        first = self.first_name
        first = first.replace(u'\xfc', '&uuml;')
        first = first.replace(u'\xf6', '&ouml;')
        first = first.replace(u'\xe4', '&auml;')

        if self.is_alive():
            date_str = '(geb. %s)' % self.birth_year()
        else:
            date_str = '(%s-%s)' % (self.birth_year(), self.death_year())

        return mark_safe('%s %s %s' % (
            (' ' + str(first) + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip(), self.last_name, date_str))


class TimelineInfo(object):
    def __init__(self, date, date_unclear, title):
        self.date = date
        self.date_unclear = date_unclear
        self.title = mark_safe((' ' + title + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip())


class GroupedTimelineInfo(object):
    def __init__(self, year, list):
        self.year = year
        self.list = list


class StatisticsItemInfo(object):
    def __init__(self, name, value, color):
        self.name = name
        self.value = value
        self.color = color

    def name_prefix(self):
        return mark_safe(self.name.split(',')[0])

    def name_suffix(self):
        return mark_safe(self.name.split(',')[1])


COLORS = (
    "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2",
    "#557fe2",
    "#e25a55",
    "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2",
    "#557fe2",
    "#e25a55",
    "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2",
    "#557fe2",
    "#e25a55",
    "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2",
    "#557fe2",
    "#e25a55")  # type: Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str]


class StatisticsListInfo(object):
    def __init__(self):
        self.list = []

    def increment(self, name):
        has_item = False
        for item in self.list:
            if item.name == name:
                item.value = item.value + 1
                has_item = True

        if not has_item:
            self.list.append(StatisticsItemInfo(name, 1, COLORS[len(self.list)]))

    def add(self, name, value):
        self.list.append(StatisticsItemInfo(name, value, COLORS[len(self.list)]))

    def limit(self, amount):
        result_list = sorted(self.list, key=attrgetter('value'), reverse=True)
        result_list = result_list[:10]
        rest_value = 0

        for item in self.list[10:]:
            rest_value = rest_value + item.value
        result_list.append(StatisticsItemInfo(_('Rest'), rest_value, COLORS[len(self.list)]))

        # re-apply colors
        index = 0
        for item in result_list:
            item.color = COLORS[index]
            index = index + 1

        self.list = result_list

    def values(self):
        result_list = []

        for item in self.list:
            result_list.append(item.value)

        return result_list

    def colors(self):
        result_list = []

        for item in self.list:
            result_list.append(item.color)

        return result_list

    def names(self):
        result_list = []

        for item in self.list:
            result_list.append(item.name)

        return result_list

    def __unicode__(self):
        return 'StatisticsListInfo: %s' % len(self.list)

    def __str__(self):
        return 'StatisticsListInfo: %s' % len(self.list)


class StatisticsInfo(object):
    def __init__(self, birthPerMonth, deathPerMonth, gender, birthLocations, children, specials):
        self.birthPerMonth = birthPerMonth
        self.deathPerMonth = deathPerMonth
        self.gender = gender
        self.birthLocations = birthLocations
        self.children = children
        self.specials = specials

    def birthPerMonthStr(self):
        return str(self.birthPerMonth)

    def deathPerMonthStr(self):
        return str(self.deathPerMonth)

    def genderValuesStr(self):
        return str(self.gender.values())

    def genderNamesStr(self):
        return str(self.gender.names())

    def birthLocationsValuesStr(self):
        return str(self.birthLocations.values())

    def birthLocationsColorsStr(self):
        return str(self.birthLocations.colors())

    def childrenValuesStr(self):
        return str(self.children.values())


class Ancestry(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/ancestries', blank=True, null=True)
    map = models.ImageField(upload_to='media/maps', blank=True, null=True)

    def thumbnail(self):
        return mark_safe('<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % (
            (self.image.name, self.image.name)))

    thumbnail.allow_tags = True

    def number_of_members(self):
        return '%d persons' % len(AncestryRelation.objects.filter(ancestry=self))

    def exports(self):
        return mark_safe(
            self.export() + '&nbsp;|&nbsp;' + self.export_no_documents() + '&nbsp;|&nbsp;' + self.export_questions() + '&nbsp;|&nbsp;' + self.export_raw() + '&nbsp;|&nbsp;' + self.export_gedcom())

    exports.allow_tags = True

    def export(self):
        return mark_safe(
            '<a href="/data/export/ancestry/%d/%s.pdf" target="_blank">PDF</a>' % (self.id, self.name))

    export.allow_tags = True

    def export_questions(self):
        return mark_safe(
            '<a href="/data/export/ancestry_questions/%d/%s_questions.pdf" target="_blank">Questions</a>' % (
                self.id, self.name))

    export_questions.allow_tags = True

    def export_no_documents(self):
        return mark_safe(
            '<a href="/data/export/ancestry_no_documents/%d/%s_no_doc.pdf" target="_blank">PDF (no doc)</a>' % (
                self.id, self.name))

    export_no_documents.allow_tags = True

    def export_raw(self):
        return mark_safe('<a href="/data/ancestry_export/%d/%s.html?with=style" target="_blank">Raw</a>' % (
            self.id, self.name))

    export_raw.allow_tags = True

    def export_gedcom(self):
        return mark_safe('<a href="/data/ancestry_gedcom/%d/%s.ged" target="_blank">GEDCOM</a>' % (
            self.id, self.name))

    export_gedcom.allow_tags = True

    def members(self):
        """
			Returns a list of persons in order of birth desc
		"""
        result_list = AncestryRelation.objects.filter(ancestry=self)
        result_list = sorted(result_list, key=attrgetter('person.birth_date'), reverse=True)
        return result_list

    def noImage(self):
        """
			Returns a list of persons without an image assigned in order of birth desc
		"""
        tmp_list = AncestryRelation.objects.filter(ancestry=self)
        tmp_list = sorted(tmp_list, key=attrgetter('person.birth_date'), reverse=True)

        result_list = []

        for ancestryPerson in tmp_list:
            person = ancestryPerson.person

            if person.image.name is None or person.image.name == '':
                result_list.append(person)

        return result_list

    def featured(self):
        """
			Returns the list of featured persons in this ancestry
		"""
        result_list = AncestryRelation.objects.filter(ancestry=self).filter(featured=True)
        result_list = sorted(result_list, key=attrgetter('person.birth_date'), reverse=True)
        return result_list

    def featured_str(self):
        """
			Returns the list of featured person
		"""
        str = '<ul>'
        for item in self.featured():
            str = '%s<li>%s</li>' % (str, item.person)
        str = '%s</ul>' % str

        return mark_safe(str)

    def locations(self):
        """
			Returns the locations of this ancestry (with duplicates)
		"""
        result_list = []

        for ancestryPerson in AncestryRelation.objects.filter(ancestry=self):
            person = ancestryPerson.person

            if person.birth_location is not None:
                result_list.append(LocationInfo(person.birth_location.lon, person.birth_location.lat))

            if person.death_location is not None:
                result_list.append(LocationInfo(person.death_location.lon, person.death_location.lat))

        return result_list

    def statistics(self):
        """
			Returns the statistics of this ancestry
		"""
        birth_per_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        death_per_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        gender = StatisticsListInfo()
        birth_locations = StatisticsListInfo()
        children = StatisticsListInfo()
        for i in range(0, 10):
            children.add('%d' % (i), 0)

        specials = StatisticsListInfo()
        oldest_person = None
        oldest_age = 0
        youngest_person = None
        youngest_age = 100
        latest_marriage_age = 0
        latest_marriage_person = None
        youngest_marriage_age = 100
        youngest_marriage_person = None
        most_children_count = 0
        most_children_person = None

        for ancestryPerson in AncestryRelation.objects.filter(ancestry=self):
            person = ancestryPerson.person

            if person.birth_date is not None and not person.birth_date_unclear and not person.birth_date_only_year:
                birth_per_month[person.birth_date.month - 1] = birth_per_month[person.birth_date.month - 1] + 1

            if person.death_date is not None:
                death_per_month[person.death_date.month - 1] = death_per_month[person.death_date.month - 1] + 1

            if person.birth_location is not None:
                birth_locations.increment(person.birth_location.city)

            if person.sex == 'F':
                gender.increment(_("Women"))
            else:
                gender.increment(_("Men"))

            if person.age() is not None and person.age() < youngest_age:
                youngest_age = person.age()
                youngest_person = person

            if person.age() is not None and person.age() > oldest_age:
                oldest_age = person.age()
                oldest_person = person

            if person.age_at_marriage() is not None and person.age_at_marriage() > latest_marriage_age:
                latest_marriage_age = person.age_at_marriage()
                latest_marriage_person = person

            if person.age_at_marriage() is not None and person.age_at_marriage() < youngest_marriage_age:
                youngest_marriage_age = person.age_at_marriage()
                youngest_marriage_person = person

            if person.children_count() > most_children_count:
                most_children_count = person.children_count()
                most_children_person = person

            children.increment('%d' % person.children_count())

        # sort & limit birth location to 10 (+rest)
        birth_locations.limit(10)

        specials.add("%s:,%s" % (_("Youngest person"), youngest_person), "%s %s" % (youngest_age, _("Years")))
        specials.add("%s:,%s" % (_("Oldest person"), oldest_person), "%s %s" % (oldest_age, _("Years")))
        specials.add("%s:,%s" % (_("Latest marriage"), latest_marriage_person),
                     "%s %s" % (latest_marriage_age, _("Years")))
        specials.add("%s:,%s" % (_("Youngest marriage"), youngest_marriage_person),
                     "%s %s" % (youngest_marriage_age, _("Years")))
        specials.add("%s:,%s" % (_("Most Children"), most_children_person),
                     "%s %s" % (most_children_count, _("Children")))

        return StatisticsInfo(birth_per_month, death_per_month, gender, birth_locations, children, specials)

    def timeline(self):
        """
			Returns timeline events of this ancestry
		"""
        result_list = []

        for ancestryPerson in AncestryRelation.objects.filter(ancestry=self):
            person = ancestryPerson.person
            if person.birth_date is not None:
                if person.birth_location is not None:
                    if person.birth_name is not None and person.birth_name != '':
                        result_list.append(TimelineInfo(person.birth_date, person.birth_date_unclear,
                                                        _('%s %s (born %s) was born in %s') % (
                                                            person.first_name, person.last_name, person.birth_name,
                                                            person.birth_location)))
                    else:
                        result_list.append(TimelineInfo(person.birth_date, person.birth_date_unclear,
                                                        _('%s %s was born in %s') % (
                                                            person.first_name, person.last_name,
                                                            person.birth_location)))
                else:
                    result_list.append(TimelineInfo(person.birth_date, person.birth_date_unclear,
                                                    _('%s %s was born') % (person.first_name, person.last_name)))

            if ancestryPerson.person.death_date is not None:
                if person.death_location is not None:
                    result_list.append(TimelineInfo(person.death_date, False, _('%s %s has died in %s') % (
                        person.first_name, person.last_name, person.death_location)))
                else:
                    result_list.append(TimelineInfo(person.death_date, False,
                                                    _('%s %s has died') % (person.first_name, person.last_name)))

            for familyStatusRelation in FamilyStatusRelation.objects.filter(woman=person):
                if familyStatusRelation.date is not None:
                    if familyStatusRelation.status == 'M':
                        if familyStatusRelation.location is not None:
                            result_list.append(TimelineInfo(familyStatusRelation.date, False,
                                                            _('marriage of %s and %s in %s') % (
                                                                familyStatusRelation.husband_name(),
                                                                familyStatusRelation.wife_name(),
                                                                familyStatusRelation.location)))
                        else:
                            result_list.append(TimelineInfo(familyStatusRelation.date, False,
                                                            _('marriage of %s and %s') % (
                                                                familyStatusRelation.husband_name(),
                                                                familyStatusRelation.wife_name())))
                    else:
                        result_list.append(TimelineInfo(familyStatusRelation.date, False, _('divorce of %s and %s') % (
                            familyStatusRelation.husband_name(), familyStatusRelation.wife_name())))

        result_list = sorted(result_list, key=attrgetter('date'), reverse=True)
        grouped_list = [list(g) for k, g in groupby(result_list, key=lambda x: x.date.year)]

        final_list = []
        for grouped_item in grouped_list:
            final_list.append(GroupedTimelineInfo(grouped_item[0].date.year, grouped_item))

        return final_list

    def documents(self):
        """
			Returns appendices (documents that are related to persons) of this ancestry
			- newest documents first
		"""

        document_list = []
        for documentRelation in DocumentRelation.objects.all():
            # check if document belongs to a person this ancestry
            if not is_empty(AncestryRelation.objects.filter(ancestry=self, person=documentRelation.person)):
                if documentRelation.document not in document_list:
                    document_list.append(documentRelation.document)

        document_list = sorted(document_list, key=attrgetter('date'), reverse=True)

        return document_list

    def ancestry_documents(self):
        """
			Returns appendices (documents that are related to this ancestry) of this ancestry
			- newest documents first
		"""
        document_list = []
        for documentRelation in DocumentAncestryRelation.objects.filter(ancestry=self):
            # check if document belongs to a person this ancestry
            if documentRelation.document not in document_list:
                document_list.append(documentRelation.document)

        document_list = sorted(document_list, key=attrgetter('date'), reverse=True)

        return document_list

    def distributions(self):
        """
			Returns the list of distributions of this ancestry
			- basically images of distributions
		"""
        return DistributionRelation.objects.filter(ancestry=self)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class DistributionRelation(models.Model):
    """
		class that links ancestry with distribution
	"""
    distribution = models.ForeignKey(Distribution, on_delete=models.DO_NOTHING)
    ancestry = models.ForeignKey(Ancestry, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return '%s - %s' % (self.ancestry.name, self.distribution.family_name)

    def __str__(self):
        return '%s - %s' % (self.ancestry.name, self.distribution.family_name)


ORIENTATION_TYPES = (
    ('P', _('Portrait')),
    ('L', _('Landscape')),
)


class Document(models.Model):
    """
		class that holds a document (as image) along with a date and a description
		- persons can be linked via DocumentRelation
	"""
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(_('date of creation'))
    image = models.ImageField(upload_to='media/documents', blank=True, null=True)
    type = models.CharField(max_length=1, choices=ORIENTATION_TYPES, default='L')

    def persons(self):
        """
			Returns a list of person linked to this document
		"""
        person_arr = []

        for documentRelation in DocumentRelation.objects.filter(document=self):
            person_arr.append(documentRelation.person)

        return person_arr

    def person_names(self):
        """
			Returns a comma separated list of person related to this document
		"""
        return mark_safe(', '.join(map(str, self.persons())))

    def ancestries(self):
        """
			Returns a list of ancestries linked to this document
		"""
        ancestry_arr = []

        for ancestryRelation in DocumentAncestryRelation.objects.filter(document=self):
            ancestry_arr.append(ancestryRelation.ancestry)

        return ancestry_arr

    def css_class(self):
        """
			Returns the appropriate css class for portrait or landscape mode
		"""
        if self.type == 'L':
            return 'landscape'
        else:
            return 'portrait'

    def ancestry_names(self):
        """
			Returns a comma separated list of ancestries related to this document
		"""
        return mark_safe(','.join(map(str, self.ancestries())))

    def thumbnail(self):
        """
			Returns a clickable thumbnail of the document for the admin area
		"""
        return mark_safe('<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % (
            (self.image.name, self.image.name)))

    thumbnail.allow_tags = True

    def __unicode__(self):
        return '%s - %s - %s' % (self.date, self.name, self.person_names())

    def __str__(self):
        return '%s - %s - %s' % (self.date, self.name, self.person_names())


class DocumentRelation(models.Model):
    """
		class that links a Document to a person
	"""
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ('document__date',)

    def __unicode__(self):
        return mark_safe(u'%s - %s - %s' % (self.document.date, self.document.name, self.person))

    def __str__(self):
        return mark_safe(u'%s - %s - %s' % (self.document.date, self.document.name, self.person))


class DocumentAncestryRelation(models.Model):
    """
		class that links a Document with an ancestry
	"""
    ancestry = models.ForeignKey(Ancestry, on_delete=models.DO_NOTHING)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return mark_safe(u'%s - %s' % (self.ancestry, self.document.name))

    def __str__(self):
        return mark_safe(u'%s - %s' % (self.ancestry, self.document.name))


class Question(models.Model):
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100, null=True, blank=True)  # type: CharField
    date = models.DateField(_('date of answer'), null=True, blank=True)
    source = models.CharField(max_length=30, null=True, blank=True)

    def open(self):
        if len(self.answer) == 0:
            return True
        else:
            return False

    def __unicode__(self):
        first = mark_safe(u' %s ' % self.person.first_name)
        first = mark_safe(first.replace(" _", " <u>").replace("_ ", "</u> "))
        return mark_safe((u' %s %s - %s' % (first, self.person.last_name, self.question)).strip())

    def __str__(self):
        first = mark_safe(u' %s ' % self.person.first_name)
        first = mark_safe(first.replace(" _", " <u>").replace("_ ", "</u> "))
        return mark_safe((u' %s %s - %s' % (first, self.person.last_name, self.question)).strip())


class AncestryRelation(models.Model):
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    ancestry = models.ForeignKey(Ancestry, on_delete=models.DO_NOTHING)
    featured = models.NullBooleanField(default=False, blank=True, null=True)

    def relation(self):
        featured_person = self.ancestry.featured()[0]
        return ancestry_relation(self.person, featured_person.person)

    def __unicode__(self):
        return u'%s' % self.ancestry.name

    def __str__(self):
        return u'%s' % self.ancestry.name


class FamilyStatusRelation(models.Model):
    status = models.CharField(max_length=1,
                              choices=(
                                  ('M', _('Marriage')), ('P', _('Partnership')),
                                  ('A', _('Adoption'))))  # type: CharField
    date = models.DateField(_('date of marriage or divorce'), null=True, blank=True)
    date_only_year = models.BooleanField(default=False)
    man = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name=_('husband'), blank=True, null=True)
    woman = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name=_('wife'), blank=True, null=True)
    husband_extern = models.CharField(max_length=50, blank=True, null=True)
    wife_extern = models.CharField(max_length=50, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True)
    ended = models.NullBooleanField(default=False, blank=True, null=True)

    def husband_name(self):
        if self.man is not None:
            return '%s %s' % (self.man.first_name, self.man.last_name)
        else:
            return self.husband_extern

    def husband_link(self):
        if self.man is not None:
            return mark_safe('<a href="/admin/data/person/%s/">%s</a>' % (self.man.id, str(self.man)))

        return self.husband_extern

    husband_link.allow_tags = True

    def wife_name(self):
        if self.woman is not None:
            return '%s %s' % (self.woman.first_name, self.woman.last_name)
        else:
            return self.wife_extern

    def wife_link(self):
        if self.woman is not None:
            return mark_safe('<a href="/admin/data/person/%s/">%s</a>' % (self.woman.id, str(self.woman)))

        return self.wife_extern

    wife_link.allow_tags = True

    def status_name(self):
        """
			Returns the family relation as adjective
		"""
        switcher = {
            'M': _("married"),
            'P': _("partnership"),
            'A': _("adopted"),
        }

        return switcher.get(self.status, '---')

    def __unicode__(self):
        husband_str = self.husband_name()
        wife_str = self.wife_name()

        switcher = {
            'M': _('Marriage %s and %s') % (husband_str, wife_str),
            'P': _('Partnership %s and %s') % (husband_str, wife_str),
            'A': _('Adoption of %s and %s') % (husband_str, wife_str),
        }

        return mark_safe(
            (' ' + switcher.get(self.status, '') + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip())

    def __str__(self):
        husband_str = self.husband_name()
        wife_str = self.wife_name()

        switcher = {
            'M': _('Marriage %s and %s') % (husband_str, wife_str),
            'P': _('Partnership %s and %s') % (husband_str, wife_str),
            'A': _('Adoption of %s and %s') % (husband_str, wife_str),
        }

        return mark_safe(
            (' ' + switcher.get(self.status, '') + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip())


EVENT_TYPES = (
    ('T', _('Baptism')),
    ('B', _('Funeral')),
    ('C', _('Confirmation')),
    ('S', _('Settlement')),
)


class PersonEvent(models.Model):
    """
		additional events for persons
	"""
    type = models.CharField(max_length=1, choices=EVENT_TYPES)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank=True, null=True)
    date = models.DateField(_('date of marriage or divorce'), null=True, blank=True)
    date_only_year = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def event_type(self):
        switcher = {
            'T': _('Baptism'),
            'B': _('Funeral'),
            'C': _('Confirmation'),
            'S': _('Settlement'),
        }

        return switcher.get(self.type, '')

    def first_name(self):
        return self.person.first_name

    def last_name(self):
        return self.person.last_name

    def __unicode__(self):
        return u'%s - %s - %s' % (self.date, self.type, self.person)

    def __str__(self):
        return u'%s - %s - %s' % (self.date, self.type, self.person)
