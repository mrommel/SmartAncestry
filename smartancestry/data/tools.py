#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True


def ellipses(original_string, max_length):
    if len(original_string) <= max_length:
        return original_string
    else:
        return original_string[:max_length - 4] + " ..."


def trimAndUnescape(value):
    val = value.strip()
    val = val.replace('<u>', '')
    val = val.replace('</u>', '')
    val = val.replace('  ', ' ')
    val = val.replace('  ', ' ')
    return val


def underlineIndices(value):
    val = value.strip()
    val = val.replace('  ', ' ')
    val = val.replace('  ', ' ')

    u_start = val.find('<u>')
    u_end = val.find('</u>')

    if u_start != -1:
        u_start = u_start + 2

    if u_end != -1:
        u_end = u_end - 1

    return '%d,%d' % (u_start, u_end)


def calculate_age(born, death):
    return death.year - born.year - ((death.month, death.day) < (born.month, born.day))


def nice_date(date, year_only):

    date_str = date.strftime("%d.%m.%Y")

    if year_only:
        date_str = '{0.year:4d}'.format(date)

    return date_str

def name_of_ancestry(x):
    name = u'%s' % x.ancestry.name
    name = name.replace(u'ä', '&auml;')
    return mark_safe(name)


def ancestry_relation(from_person, to_person):
    """
		derives the relation status from person from_person to to_person
	"""
    if from_person.father == to_person or from_person.mother == to_person:
        if from_person.female():
            return _('daughter')
        else:
            return _('son')

    if from_person.father is not None:
        if from_person.father.mother == to_person or from_person.father.father == to_person:
            if from_person.female():
                return _('granddaughter')
            else:
                return _('grandson')

    if from_person.mother is not None:
        if from_person.mother.mother == to_person or from_person.mother.father == to_person:
            if from_person.female():
                return _('granddaughter')
            else:
                return _('grandson')

    if to_person.wife() == from_person:
        return _('wife')

    if to_person.wife() is not None:
        if to_person.wife().father == from_person:
            return _('father in law')

        if to_person.wife().mother == from_person:
            return _('mother in law')

    if to_person.husband() == from_person:
        return _('husband')

    if to_person.husband() is not None:
        if to_person.husband().father == from_person:
            return _('father in law')

        if to_person.husband().mother == from_person:
            return _('mother in law')

    if to_person.father == from_person:
        return _('father')

    if to_person.father is not None:
        for fathers_sibling in to_person.father.siblings():
            if fathers_sibling == from_person:
                if from_person.female():
                    return _('aunt')
                else:
                    return _('uncle')

            if fathers_sibling.wife() == from_person:
                return _('aunt')

            if fathers_sibling.husband() == from_person:
                return _('uncle')

            for fathers_sibling_child in fathers_sibling.children():
                if fathers_sibling_child == from_person:
                    if from_person.female():
                        return _('girl cousin')
                    else:
                        return _('boy cousin')

                for fathers_sibling_child_child in fathers_sibling_child.children():
                    if fathers_sibling_child_child == from_person:
                        if from_person.female() and fathers_sibling_child.female():
                            return _('girl cousins daughter')
                        if from_person.female() and fathers_sibling_child.male():
                            return _('boy cousins daughter')
                        if from_person.male() and fathers_sibling_child.female():
                            return _('girl cousins son')
                        else:
                            return _('boy cousins son')

        if to_person.father.father == from_person:
            return _('grandfather')

        if to_person.father.father is not None:
            if to_person.father.father.father is not None:
                if to_person.father.father.father == from_person:
                    return _('great grandfather')

                if to_person.father.father.father.father is not None:

                    if to_person.father.father.father.father == from_person:
                        return _('great great grandfather')

                    if to_person.father.father.father.father.father == from_person:
                        return _('great great great grandfather')

                    if to_person.father.father.father.father.mother == from_person:
                        return _('great great great grandmother')

                if to_person.father.father.father.mother is not None:

                    if to_person.father.father.father.mother == from_person:
                        return _('great great grandmother')

                    if to_person.father.father.father.mother.father == from_person:
                        return _('great great great grandfather')

                    if to_person.father.father.father.mother.mother == from_person:
                        return _('great great great grandmother')

            if to_person.father.father.mother is not None:
                if to_person.father.father.mother == from_person:
                    return _('great grandmother')

                if to_person.father.father.mother.father is not None:

                    if to_person.father.father.mother.father == from_person:
                        return _('great great grandfather')

                    if to_person.father.father.mother.father.father == from_person:
                        return _('great great great grandfather')

                    if to_person.father.father.mother.father.mother == from_person:
                        return _('great great great grandmother')

                if to_person.father.father.mother.mother is not None:

                    if to_person.father.father.mother.mother == from_person:
                        return _('great great grandmother')

                    if to_person.father.father.mother.mother.father == from_person:
                        return _('great great great grandfather')

                    if to_person.father.father.mother.mother.mother == from_person:
                        return _('great great great grandmother')

        if to_person.father.mother == from_person:
            return _('grandmother')

        if to_person.father.mother is not None:
            if to_person.father.mother.father is not None:
                if to_person.father.mother.father == from_person:
                    return _('great grandfather')

                if to_person.father.mother.father.father == from_person:
                    return _('great great grandfather')

                if to_person.father.mother.father.mother == from_person:
                    return _('great great grandmother')

            if to_person.father.mother.mother is not None:
                if to_person.father.mother.mother == from_person:
                    return _('great grandmother')

                if to_person.father.mother.mother.father == from_person:
                    return _('great great grandfather')

                if to_person.father.mother.mother.mother == from_person:
                    return _('great great grandmother')

    if to_person.mother == from_person:
        return _('mother')

    if to_person.mother is not None:
        for mothers_sibling in to_person.mother.siblings():
            if mothers_sibling == from_person:
                if from_person.female():
                    return _('aunt')
                else:
                    return _('uncle')

            if mothers_sibling.wife() == from_person:
                return _('aunt')

            if mothers_sibling.husband() == from_person:
                return _('uncle')

            for mothers_sibling_child in mothers_sibling.children():
                if mothers_sibling_child == from_person:
                    if from_person.female():
                        return _('girl cousin')
                    else:
                        return _('boy cousin')

                for mothers_sibling_child_child in mothers_sibling_child.children():
                    if mothers_sibling_child_child == from_person:
                        if from_person.female() and mothers_sibling_child.female():
                            return _('girl cousins daughter')
                        if from_person.female() and mothers_sibling_child.male():
                            return _('boy cousins daughter')
                        if from_person.male() and mothers_sibling_child.female():
                            return _('girl cousins son')
                        else:
                            return _('boy cousins son')

        if to_person.mother.father == from_person:
            return _('grandfather')

        if to_person.mother.father is not None:
            if to_person.mother.father.father is not None:
                if to_person.mother.father.father == from_person:
                    return _('great grandfather')

                if to_person.mother.father.father.father == from_person:
                    return _('great great grandfather')

                if to_person.mother.father.father.mother == from_person:
                    return _('great great grandmother')

            if to_person.mother.father.mother is not None:
                if to_person.mother.father.mother == from_person:
                    return _('great grandmother')

                if to_person.mother.father.mother.father == from_person:
                    return _('great great grandfather')

                if to_person.mother.father.mother.mother == from_person:
                    return _('great great grandmother')

        if to_person.mother.mother == from_person:
            return _('grandmother')

        if to_person.mother.mother is not None:
            if to_person.mother.mother.father is not None:
                if to_person.mother.mother.father == from_person:
                    return _('great grandfather')

                if to_person.mother.mother.father.father == from_person:
                    return _('great great grandfather')

                if to_person.mother.mother.father.mother == from_person:
                    return _('great great grandmother')

            if to_person.mother.mother.mother is not None:
                if to_person.mother.mother.mother == from_person:
                    return _('great grandmother')

                if to_person.mother.mother.mother.father == from_person:
                    return _('great great grandfather')

                if to_person.mother.mother.mother.mother == from_person:
                    return _('great great grandmother')

    if from_person.wife() is not None:
        if from_person.wife().father == to_person or from_person.wife().mother == to_person:
            return _('son in law')

    if from_person.husband() is not None:
        if from_person.husband().father == to_person or from_person.husband().mother == to_person:
            return _('daughter in law')

    if from_person in to_person.siblings():
        if from_person.female():
            return _('sister')
        else:
            return _('brother')

    for sibling in to_person.siblings():
        if sibling.wife() == from_person:
            return _('sister in law')

        if sibling.husband() == from_person:
            return _('brother in law')

        for sibling_child in sibling.children():
            if sibling_child == from_person:
                if from_person.female():
                    return _('niece')
                else:
                    return _('nephew')

            for sibling_child_child in sibling_child.children():
                if sibling_child_child == from_person:
                    if from_person.female():
                        return _('great niece')
                    else:
                        return _('great nephew')

    return None
