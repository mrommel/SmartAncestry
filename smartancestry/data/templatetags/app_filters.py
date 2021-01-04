#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

import logging

# Get an instance of a logger
logger = logging.getLogger('data.models')

register = template.Library()


@register.filter(name='location_without_country')
def location_without_country(value):
    if value is None:
        return ''

    try:
        return value.city
    except:
        pass

    return ''


@stringfilter
@register.filter(name='encode_spaces')
def encode_spaces(value):
    return value.replace(' ', '')


@stringfilter
@register.filter(name='underline')
def underline(value):
    val = ' %s ' % value
    val = val.replace(' _', ' <u>')
    val = val.replace('_ ', '</u> ')
    return mark_safe(val.strip())


@stringfilter
@register.filter(name='remove_underlines')
def remove_underlines(value):
    value = value.replace('_', '')
    value = value.replace('_', '')
    return value.strip()


@stringfilter
@register.filter(name='replace_umlauts')
def replace_umlauts(value):
    value = value.replace('&auml;', u'ä')
    return value.strip()


@stringfilter
@register.filter(name='remove_media')
def remove_media(value):
    return value.replace('media/media', 'media')


@stringfilter
@register.filter(name='remove_persons_folder')
def remove_persons_folder(value):
    return value.replace('/media/media/persons/', '').replace('.JPG', '.jpg').replace('%C3%A4', 'ä')


@stringfilter
@register.filter(name='trim')
def trim(value):
    return value.strip()


@stringfilter
@register.filter(name='trim_hash')
def trim_hash(value):
    return value.replace('#', '').replace('\'', '')


@stringfilter
@register.filter(name='trim_and_unescape')
def trim_and_unescape(value):
    val = value.strip()
    val = val.replace('<u>', '')
    val = val.replace('</u>', '')
    # val = val.replace('&auml;', 'ae')
    val = val.replace('  ', ' ')
    val = val.replace('  ', ' ')
    return val


@stringfilter
@register.filter(name='html_encode')
def html_encode(value):
    val = value.replace('\xe4', '&auml;')
    return val


@stringfilter
@register.filter(name='underline_indices')
def underline_indices(value: object) -> object:
    val = value.strip()
    # val = val.replace('&auml;', 'ae')
    val = val.replace('  ', ' ')
    val = val.replace('  ', ' ')

    u_start = val.find('<u>')
    u_end = val.find('</u>')

    if u_start != -1:
        u_start = u_start + 2

    if u_end != -1:
        u_end = u_end - 1

    return '{start: %d, end: %d}' % (u_start, u_end)


@register.filter(needs_autoescape=True)
def initial_letter_filter(text, autoescape=None):
    first, other = text[0], text[1:]
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = '<strong>%s</strong>%s' % (esc(first), esc(other))
    return mark_safe(result)


@stringfilter
@register.filter(name='ellipses')
def ellipses(value, arg):
    original_string = value
    max_length = arg

    if len(original_string) <= max_length:
        return original_string
    else:
        return original_string[:max_length - 4] + " ..."
