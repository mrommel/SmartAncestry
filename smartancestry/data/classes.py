from operator import attrgetter

from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# constants type: Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
# str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
# str, str, str, str, str, str, str]
from .tools import trim_and_unescape, ellipses, underline_indices

COLORS = (
    "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2",
    "#557fe2", "#e25a55", "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8",
    "#55dde2", "#55aee2", "#557fe2", "#e25a55", "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a",
    "#55e289", "#55e2b8", "#55dde2", "#55aee2", "#557fe2", "#e25a55", "#e28955", "#e2b855", "#dde255", "#aee255",
    "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2", "#557fe2", "#e25a55")


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

    def __init__(self, birth_per_month, death_per_month, gender, birth_locations, children, specials):
        self.birth_per_month = birth_per_month
        self.death_per_month = death_per_month
        self.gender = gender
        self.birth_locations = birth_locations
        self.children = children
        self.specials = specials

    def birth_per_month_str(self):
        return str(self.birth_per_month)

    def death_per_month_str(self):
        return str(self.death_per_month)

    def gender_values_str(self):
        return str(self.gender.values())

    def gender_names_str(self):
        return str(self.gender.names())

    def birth_locations_values_str(self):
        return str(self.birth_locations.values())

    def birth_locations_colors_str(self):
        return str(self.birth_locations.colors())

    def children_values_str(self):
        return str(self.children.values())


class LocationInfo(object):

    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

    def lon_lat(self):
        return "{:10.4f}".format(self.lon) + ", " + "{:10.4f}".format(self.lat)


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
            return u'♂'
        else:
            return u'♀'


class MarriageInfo(object):
    def __init__(self, level, id, text):
        self.id = id
        self.level = level
        self.text = text


class PersonEventInfo(object):

    def __init__(self, date, age, title, summary, location):
        self.date = date
        self.age = age
        self.title = title
        self.summary = summary
        self.location = location


class TimelineInfo(object):
    def __init__(self, date, date_unclear, title, description, image):
        self.date = date
        self.date_unclear = date_unclear
        self.title = mark_safe((' ' + title + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip())
        self.description = description
        self.image = image
