#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from django.db import models
from django.db.models import Q
from itertools import chain, groupby
from operator import attrgetter
from datetime import date
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sets import Set
import logging
from django.core.urlresolvers import reverse

# Get an instance of a logger
logger = logging.getLogger(__name__)

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

def ellipses(original_string, max_length):
    if len(original_string) <= max_length:
        return original_string
    else:
        return original_string[:max_length-4] + " ..."

def trimAndUnescape(value):
	val = value.strip()
	val = val.replace('<u>', '')
	val = val.replace('</u>', '')
	# val = val.replace('ä', u'ä')
	val = val.replace('  ', ' ')
	val = val.replace('  ', ' ')
	return val
	
def underlineIndices(value):
	val = value.strip()
	#val = val.replace('&auml;', 'ae')
	val = val.replace('  ', ' ')
	val = val.replace('  ', ' ')
	
	u_start = val.find('<u>')
	u_end = val.find('</u>')
	
	if u_start <> -1:
		u_start = u_start + 2
	
	if u_end <> -1:
		u_end = u_end - 1
	
	return '%d,%d' % (u_start, u_end)
	
def calculate_age(born, death):
	return death.year - born.year - ((death.month, death.day) < (born.month, born.day))

class LocationInfo(object):
	def __init__(self, lon, lat):
		self.lon = lon
		self.lat = lat
		
	def lon_lat(self):
		return "{:10.4f}".format(self.lon) + ", " + "{:10.4f}".format(self.lat)

"""
	class of a distribution
"""
class Distribution(models.Model):
	family_name = models.CharField(max_length=50)
	image = models.ImageField(upload_to='media/distributions', blank=True, null=True)

	def __unicode__(self):			  
		return '%s' % (self.family_name)

"""
	class of a location with city, state and country
	
	meta information: image, longitude, latitude
"""
class Location(models.Model):
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	country = models.CharField(max_length=50)
	image = models.ImageField(upload_to='media/locations', blank=True, null=True)
	lon = models.FloatField(default=0)
	lat = models.FloatField(default=0)
	
	"""
		list of all persons that share the same location
	"""
	def members(self):
		result_list = []
		for person in Person.objects.filter(birth_location = self):
			result_list.append(person)
			
		for person in Person.objects.filter(death_location = self):
			if person not in result_list:
				result_list.append(person)
				
		for familyStatusRelation in FamilyStatusRelation.objects.filter(location = self):
			if familyStatusRelation.man not in result_list:
				result_list.append(familyStatusRelation.man)
			
			if familyStatusRelation.woman not in result_list:
				result_list.append(familyStatusRelation.woman)
			
		return result_list
		
	def has_image(self):
		if self.image:
			return True
		return False
		
	def thumbnail(self):
		return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
		
	@models.permalink
	def get_absolute_url(self):
		return ('data.views.location', [str(self.id)])
	
	def __unicode__(self):			  
		return '%s (%s)' % (self.city, self.country)

class TreeInfo(object):
	def __init__(self, level, person, selected):
		self.level = level
		self.person = person
		self.selected = selected
		
	# {4,3,0,%22%E2%99%82%20Marcel%20Rommel%22,-1,-1,%27Geb.:%2013.11.2006%20Berlin%27,%27Gest.:%20%27}	
	def info(self):			  
		id = self.person.id
		selected = self.selected
		sign = self.person.gender_sign()
		tmp = self.person.full_name()
		tmp = tmp.replace(u'\xe4', '&auml;')
		name = trimAndUnescape(str(tmp))
		indices = underlineIndices(str(tmp))
		
		# born str construction
		if self.person.birth_date is not None:
			born = str('%s: %02d.%02d.%04d' % (_('Born'), self.person.birth_date.day, self.person.birth_date.month, self.person.birth_date.year))
		else:
			born = str('%s: ' % _('Born'))
		if self.person.birth_location is not None:
			born = born + ' ' + self.person.birth_location.city.encode('utf-8')
		born = ellipses(born, 32)
			
		# died str construction
		died = str('%s: ' % _('Died'))
		if self.person.death_date is not None:
			died = died + (' %02d.%02d.%04d' % (self.person.death_date.day, self.person.death_date.month, self.person.death_date.year))
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
			return '%d.%d.%d' % (self.date.day, self.date.month, self.date.year) 
		
	def __unicode__(self):
		return '[PartnerInfo: %s - dyo=%d,date:=%s' % (self.partner, self.date_year_only, self.date) 
		
class RelativesInfo(object):
	def __init__(self, relatives, relations):
		self.relatives = relatives
		self.relations = relations
		
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

def name_of_ancestry(x):
	name = u'%s' % x.ancestry.name
	name = name.replace(u'ä', '&auml;')
	return mark_safe(name)

"""
	class of persons
"""
class Person(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	birth_name = models.CharField(max_length=50, blank=True, null=True)
	sex = models.CharField(max_length=1, choices=(('M', _('Male')), ('F', _('Female'))), verbose_name=_('Gender'))
	birth_date = models.DateField(_('date of birth'))
	birth_date_only_year = models.BooleanField(default=False)
	birth_location = models.ForeignKey(Location, blank=True, null=True, related_name='birth_location') 
	death_date = models.DateField(_('date of death'), null=True, blank=True)
	death_date_only_year = models.BooleanField(default=False)
	death_location = models.ForeignKey(Location, blank=True, null=True, related_name='death_location')
	cause_of_death = models.CharField(max_length=100, blank=True, null=True)
	already_died = models.NullBooleanField(default=False, blank=True, null=True)
	profession = models.CharField(max_length=50, blank=True, null=True)
	father = models.ForeignKey('self', blank=True, null=True, related_name='children_father')
	father_extern = models.CharField(max_length=50, blank=True, null=True)
	mother = models.ForeignKey('self', blank=True, null=True, related_name='children_mother')
	mother_extern = models.CharField(max_length=50, blank=True, null=True)
	children_extern = models.CharField(max_length=200, blank=True, null=True)
	siblings_extern = models.CharField(max_length=200, blank=True, null=True)
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
	
	def full_name(self):
		first = self.first_name_short()
		first = first.replace(u'\xfc', '&uuml;')
		first = first.replace(u'\xf6', '&ouml;')
		first = first.replace(u'\xe4', '&auml;')
		return ('%s %s' % ((' ' + str(first) + ' ').replace(" _", " <u>").replace("_ ", "</u> "), self.last_name)).strip()
	
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
		birth_str = self.birth_location
		if birth_str is None:
			birth_str = '-'
		return mark_safe('%s<br>%s' % (self.birth_date, birth_str))
		
	def birth_year(self):
		if self.birth_date is None:
			return '---'
		return '{0.year:4d}'.format(self.birth_date)
	
	def death(self):
		date_str = self.death_date
		if date_str is None:
			date_str = '-'
		death_str = self.death_location
		if death_str is None:
			death_str = '-'
		return mark_safe('%s<br>%s' % (date_str, death_str))
		
	def death_year(self):
		if self.death_date is None and self.already_died:
			return '???'
			
		if self.death_date is None:
			return ''
			
		#return self.death_date.strftime('%Y')
		return '{0.year:4d}'.format(self.death_date)
	
	def father_name(self):
		if self.father is not None:
			return str(self.father)
		else:
			return self.father_extern
			
	def mother_name(self):
		if self.mother is not None:
			return str(self.mother)
		else:
			return self.mother_extern
		
	def thumbnail(self):
		if self.image.name is not None and self.image.name <> '':
			return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
		else:
			return '<img border="0" alt="" src="/static/data/images/Person-icon-grey.JPG" height="40" />'
	thumbnail.allow_tags = True
	
	def admin_url(self):
		return mark_safe('<a href="%s">%s</a>' % (self.id, self.full_name))
	admin_url.allow_tags = True
	
	def father_link(self):
		if self.father is not None:
			return '<a href="/admin/data/person/%s/">%s</a>' % (self.father.id, str(self.father))
		else:
			return ''
	father_link.allow_tags = True
	
	def mother_link(self):
		if self.mother is not None:
			return '<a href="/admin/data/person/%s/">%s</a>' % (self.mother.id, str(self.mother))
		else:
			return ''
	mother_link.allow_tags = True
	
	def tree_link(self):
		return '<a href="http://127.0.0.1:4446/?person=%s" target="_blank">Tree</a> / <a href="view-source:http://127.0.0.1:8000/data/person/dot_tree/%s/ancestry.dot" target="_blank">Raw Tree</a>' % (self.id, self.id)
	tree_link.allow_tags = True
	
	def age(self):
		if self.death_date is None and self.already_died == False:
			return calculate_age(self.birth_date, date.today())
		
		if self.death_date is None and self.already_died == True:
			return None
		
		return calculate_age(self.birth_date, self.death_date)
	
	def ageAtMarriage(self):
		date_married = self.married_at()
		
		if date_married is None:
			return None
		
		return calculate_age(self.birth_date, date_married)
	
	def partner_relations(self):
		if self.sex == 'M':
			try:
				partners = []
				for relation in FamilyStatusRelation.objects.filter(man = self):
					if relation.woman is not None:
						partners.append(PartnerInfo(relation.status_name, relation.woman, "", relation.location, relation.date, relation.date_only_year, relation.status))
					else:
						partners.append(PartnerInfo(relation.status_name, None, relation.wife_extern, relation.location, relation.date, relation.date_only_year, relation.status))
				return partners
			except FamilyStatusRelation.DoesNotExist:
				pass
		
		if self.sex == 'F':
			try:
				partners = []
				for relation in FamilyStatusRelation.objects.filter(woman = self):
					if relation.man is not None:
						partners.append(PartnerInfo(relation.status_name, relation.man, "", relation.location, relation.date, relation.date_only_year, relation.status))
					else:
						partners.append(PartnerInfo(relation.status_name, None, relation.husband_extern, relation.location, relation.date, relation.date_only_year, relation.status))
				return partners
			except FamilyStatusRelation.DoesNotExist:
				pass
		
		return None
	
	def siblings(self):
		if self.mother is None and self.father is None:
			return []
		
		if self.mother is None:
			return Person.objects.filter(father = self.father).exclude(id = self.id)
			
		if self.father is None:
			return Person.objects.filter(mother = self.mother).exclude(id = self.id)
		
		siblings_list = []
		siblings_list_mother = list(Person.objects.filter(mother = self.mother))
		siblings_list_father = list(Person.objects.filter(father = self.father))
		
		for sibling in chain(siblings_list_mother, siblings_list_father):
			if sibling not in siblings_list and sibling.id <> self.id:
				siblings_list.append(sibling)
	
		siblings_list = sorted(siblings_list, key=attrgetter('birth_date'), reverse=False)
	
		return siblings_list
		
	def siblings_extern_list(self):
		if self.siblings_extern is not None and self.siblings_extern <> '':
			return self.siblings_extern.split(',')
			
		return None
		
	def siblings_text(self):
		str = ''
		
		for sibling_item in self.siblings():
			str = "%s, %s" % (str, sibling_item.get_admin_url())
			
		if self.siblings_extern is not None:
			str = "%s, %s" % (str, self.siblings_extern)
		
		str = "$%s$" % (str)
		str = str.replace("$, ", "")
		str = str.replace(", $", "")
		str = str.replace("$", "")
		
		return str
	siblings_text.allow_tags = True
		
	def children(self):
		children_list = Person.objects.filter(Q(father = self) | Q(mother = self))
		children_list = sorted(children_list, key=attrgetter('birth_date'), reverse=False)
		return children_list
		
	def children_extern_list(self):
		if self.children_extern is not None and self.children_extern <> '':
			return self.children_extern.split(',')
			
		return None
		
	def childen_text(self):
		str = ''
		
		for children_item in self.children():
			str = "%s, %s" % (str, children_item.get_admin_url())
			
		if self.children_extern is not None:
			str = "%s, %s" % (str, self.children_extern)
		
		str = "$%s$" % (str)
		str = str.replace("$, ", "")
		str = str.replace(", $", "")
		str = str.replace("$", "")
		
		return str
	childen_text.allow_tags = True
		
	def children_count(self):
		count = len(self.children())
		
		if self.children_extern_list() is not None:
			count = count + len(self.children_extern_list())
		
		return count
		
	def ancestries(self):
		return AncestryRelation.objects.filter(person = self) 

	def ancestry_names(self):
		str = ''
		
		for item in map(name_of_ancestry, AncestryRelation.objects.filter(person = self)):
			str = '%s, %s' % (str, item)
		
		str = "$%s$" % (str)
		str = str.replace("$, ", "")
		str = str.replace(", $", "")
		str = str.replace("$", "")
		
		return mark_safe(str)
	
	def has_ancestry(self, ancestry_id):
		for ancestryRelation in AncestryRelation.objects.filter(person = self):
			if ancestryRelation.id == ancestry_id:
				return True
				
		return False
	
	def married_to(self):
		"""
			TODO: FIXME - no divorce handling here
		"""
		if self.sex == 'M':
			try:
				for husbandRelation in FamilyStatusRelation.objects.get(man = self):
					return husbandRelation.woman
			except FamilyStatusRelation.DoesNotExist:
				pass
		
		if self.sex == 'F':
			try:
				for wifeRelation in FamilyStatusRelation.objects.get(woman = self):
					return wifeRelation.man
			except FamilyStatusRelation.DoesNotExist:
				pass
		
		return None
		
	def wife(self):
		"""
			FIXME: divorce not handled
		"""
		if self.sex == 'M':
			for husbandRelation in FamilyStatusRelation.objects.filter(Q(man = self) & Q(status = 'M')):
				return husbandRelation.woman
				
		return None
	
	def husband(self):
		"""
			FIXME: divorce not handled
		"""
		if self.sex == 'F':
			for husbandRelation in FamilyStatusRelation.objects.filter(Q(woman = self) & Q(status = 'M')):
				return husbandRelation.man
				
		return None
	
	def married_at(self):
		relation = None
		
		if self.sex == 'M':
			relationList = FamilyStatusRelation.objects.filter(man = self)
			if len(relationList) > 0:
				relation = relationList[0]
		
		if self.sex == 'F':
			relationList = FamilyStatusRelation.objects.filter(woman = self)
			if len(relationList) > 0:
				relation = relationList[0]
			
		if relation is not None:
			return relation.date
			
		return None
	
	""" 
		provides a list of relative as well as links between them
	""" 
	def relatives(self):
		relatives_list = []
		relations_list = []
		external_id = 1000
		
		if self.father is not None:
			if self.father.father is not None:
				relatives_list.append(TreeInfo(0, self.father.father, 0))	
				relations_list.append(RelationsInfo(self.father.father.id, self.father.id))
			if self.father.mother is not None:
				relatives_list.append(TreeInfo(0, self.father.mother, 0))
				relations_list.append(RelationsInfo(self.father.mother.id, self.father.id))
				
			relatives_list.append(TreeInfo(1, self.father, 0))
			relations_list.append(RelationsInfo(self.father.id, self.id))
		
		if self.mother is not None:
			if self.mother.father is not None:
				relatives_list.append(TreeInfo(0, self.mother.father, 0))	
				relations_list.append(RelationsInfo(self.mother.father.id, self.mother.id))	
			if self.mother.mother is not None:
				relatives_list.append(TreeInfo(0, self.mother.mother, 0))
				relations_list.append(RelationsInfo(self.mother.mother.id, self.mother.id))
				
			relatives_list.append(TreeInfo(1, self.mother, 0))
			relations_list.append(RelationsInfo(self.mother.id, self.id))
		
		if self.mother_extern is not None and self.mother_extern <> '':
			relatives_list.append(TreeInfo(1, PersonInfo(external_id, self.mother_extern, 'F'), 0))
			relations_list.append(RelationsInfo(external_id, self.id))
			external_id = external_id + 1
			
		if self.father_extern is not None and self.father_extern <> '':
			relatives_list.append(TreeInfo(1, PersonInfo(external_id, self.father_extern, 'M'), 0))
			relations_list.append(RelationsInfo(external_id, self.id))
			external_id = external_id + 1
		
		relatives_list.append(TreeInfo(2, self, 1))
		
		for partner in self.partner_relations():
		
			if partner.partner is None:
				relatives_list.append(TreeInfo(2, PersonInfo(external_id, partner.partner_name, 'M'), 0))
				#relations_list.append(RelationsInfo(external_id, self.id))
				external_id = external_id + 1
			else:
				relatives_list.append(TreeInfo(2, partner.partner, 0))
				
				""" 
					check if partner is mother / father of childs of current person 
				"""
				for partner_child in partner.partner.children():
					for child in self.children():
						if partner_child.id == child.id:
							relations_list.append(RelationsInfo(partner.partner.id, child.id))
				
				if partner.partner.mother is not None:
					if partner.partner.mother.father is not None:
						relatives_list.append(TreeInfo(0, partner.partner.mother.father, 0))	
						relations_list.append(RelationsInfo(partner.partner.mother.father.id, partner.partner.mother.id))	
					if partner.partner.mother.mother is not None:
						relatives_list.append(TreeInfo(0, partner.partner.mother.mother, 0))
						relations_list.append(RelationsInfo(partner.partner.mother.mother.id, partner.partner.mother.id))
				
					relatives_list.append(TreeInfo(1, partner.partner.mother, 0))
					relations_list.append(RelationsInfo(partner.partner.mother.id, partner.partner.id))
				
				if partner.partner.father is not None:
					if partner.partner.father.father is not None:
						relatives_list.append(TreeInfo(0, partner.partner.father.father, 0))	
						relations_list.append(RelationsInfo(partner.partner.father.father.id, partner.partner.father.id))
					if partner.partner.father.mother is not None:
						relatives_list.append(TreeInfo(0, partner.partner.father.mother, 0))
						relations_list.append(RelationsInfo(partner.partner.father.mother.id, partner.partner.father.id))
				
					relatives_list.append(TreeInfo(1, partner.partner.father, 0))
					relations_list.append(RelationsInfo(partner.partner.father.id, partner.partner.id))
		
		for child in self.children():
			relatives_list.append(TreeInfo(3, child, 0))
			relations_list.append(RelationsInfo(self.id, child.id))
			
			for grandchild in child.children():
				relatives_list.append(TreeInfo(4, grandchild, 0))
				relations_list.append(RelationsInfo(child.id, grandchild.id))
		
		return RelativesInfo(relatives_list, relations_list)
	
	# create list of relations for tree
	# [(1,2);(3,1)]
	def relations_str(self):
		result_list = []
		for item in self.relatives().relations:
			result_list.append('%d+%d' % (item.source, item.destination))
		return str(result_list).replace(',', ';').replace('+', ',').replace(' ', '').replace('[\'', '[(').replace('\';\'',');(').replace('\']', ')]')
	
	# creates a list of relatives for tree
	# [{4,3,0,%22%E2%99%82%20Marcel%20Rommel%22,-1,-1,%27Geb.:%2013.11.2006%20Berlin%27,%27Gest.:%20%27}]
	# .replace('&#39;', '\'')
	def relatives_str(self):
		result_list = []
		for item in self.relatives().relatives:
			result_list.append(item.info())
		return mark_safe(str(result_list).replace('"', '').replace('}, {', '};{').replace(' ', '%20'))
	
	def relation_to_str(self, person):
		return '%s %s %s' % (ancestry_relation(self, featured_person.person), _('of'), featured_person.person)
	
	def relation_in_str(self, ancestry):
		featured_person = ancestry.featured()[0]
		relation = ancestry_relation(self, featured_person.person)
		
		if relation is None:
			return None
		
		return mark_safe('%s %s %s' % (relation, _('of'), featured_person.person.full_name()))
	relation_in_str.allow_tags = True
	
	def relation_str(self):
		
		str = ''
		
		for ancestry in self.ancestries():
			featured_person = ancestry.ancestry.featured()[0]
			str = '%s %s %s %s (%s %s)<br />' % (str, ancestry_relation(self, featured_person.person), _('of'), featured_person.person.get_admin_url(), _('ancestry'),ancestry.ancestry)
		
		return str
	relation_str.allow_tags = True
	
	@models.permalink
	def get_absolute_url(self):
		return ('data.views.person', [str(self.id)])
		
	def get_admin_url(self):
		url = reverse('admin:%s_%s_change' % (self._meta.app_label,  self._meta.model_name),  args=[self.id] )
		return u'<a href="%s">%s</a>' % (url,  self.__unicode__())
	
	"""
		todo: return a pdf of the persons cv
	"""
	def export_pdf(self):
		pass
		
	def appendices(self):
		return DocumentRelation.objects.filter(person = self)
		
	def number_of_questions(self):
		return '%d / %d' % (len(Question.objects.filter(person = self).exclude(answer = None)), len(Question.objects.filter(person = self)))
	
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
		
		return mark_safe('%s %s %s' % ((' ' + str(first) + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip(), self.last_name, date_str))

class TimelineInfo(object):
	def __init__(self, date, title):
		self.date = date
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

COLORS = ( "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2", "#557fe2", "#e25a55",
	"#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2", "#557fe2", "#e25a55",
	"#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2", "#557fe2", "#e25a55",
	"#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2", "#557fe2", "#e25a55")	

class StatisticsListInfo(object):
	def __init__(self):
		self.list = []
		
	def increment(self, name):
		hasItem = False
		for item in self.list:
			if item.name == name:
				item.value = item.value + 1
				hasItem = True
				
		if hasItem == False:
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
		
		# reapply colors
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

class PersonEventRelation(models.Model):
	event = models.CharField(max_length=512)
	date = models.DateField()
	person = models.ForeignKey(Person)
	location = models.ForeignKey(Location, blank=True, null=True) 
	
	def thumbnail(self):
		return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
	
	def __unicode__(self):			  
		return '%s - %s - %s' % (self.date, self.person, self.event)

class Ancestry(models.Model):
	name = models.CharField(max_length=50)
	image = models.ImageField(upload_to='media/ancestries', blank=True, null=True)
	map = models.ImageField(upload_to='media/maps', blank=True, null=True)
	
	def thumbnail(self):
		return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
	
	def number_of_members(self):
		return '%d persons' % len(AncestryRelation.objects.filter(ancestry = self))
	
	def export(self):
		return '<a href="/data/export/ancestry/%d/%s.pdf" target="_blank">Export PDF</a>' % (self.id, self.name)
	export.allow_tags = True
	
	def export_raw(self):
		return '<a href="/data/ancestry_export/%d/%s.html?with=style" target="_blank">Export Raw</a>' % (self.id, self.name)
	export_raw.allow_tags = True
	
	def members(self):
		result_list = AncestryRelation.objects.filter(ancestry = self)
		result_list = sorted(result_list, key=attrgetter('person.birth_date'), reverse=True)
		return result_list
		
	def noImage(self):
		tmp_list = AncestryRelation.objects.filter(ancestry = self)
		tmp_list = sorted(tmp_list, key=attrgetter('person.birth_date'), reverse=True)
		
		result_list = []
		
		for ancestryPerson in tmp_list:
			person = ancestryPerson.person
			
			if person.image.name is None or person	.image.name == '':
				result_list.append(person)
			
		return result_list
	
	def featured(self):
		result_list = AncestryRelation.objects.filter(ancestry = self).filter(featured = True)
		result_list = sorted(result_list, key=attrgetter('person.birth_date'), reverse=True)
		return result_list
		
	def featured_str(self):
		str = '<ul>'
		for item in self.featured():
			str = '%s<li>%s</li>' % (str, item.person)
		str = '%s</ul>' % str
		
		return mark_safe(str)
	
	def locations(self):
		result_list = []
		
		for ancestryPerson in AncestryRelation.objects.filter(ancestry = self):
			person = ancestryPerson.person
			
			if person.birth_location is not None:
				result_list.append(LocationInfo(person.birth_location.lon, person.birth_location.lat))
				
			if person.death_location is not None:
				result_list.append(LocationInfo(person.death_location.lon, person.death_location.lat))	
			
		return result_list
		
	def statistics(self):
		birthPerMonth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		deathPerMonth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		gender = StatisticsListInfo()
		birthLocations = StatisticsListInfo()
		children = StatisticsListInfo()
		for i in range(0, 10):
			children.add('%d' % (i), 0)
		
		specials = StatisticsListInfo()
		oldestPerson = None
		oldestAge = 0
		youngestPerson = None
		youngestAge = 100
		latestMarriageAge = 0
		latestMarriagePerson = None
		youngestMarriageAge = 100
		youngestMarriagePerson = None
		mostChildrenCount = 0
		mostChildrenPerson = None
		
		for ancestryPerson in AncestryRelation.objects.filter(ancestry = self):
			person = ancestryPerson.person
			
			if person.birth_date is not None:
				birthPerMonth[person.birth_date.month - 1] = birthPerMonth[person.birth_date.month - 1] + 1
			
			if person.death_date is not None:
				deathPerMonth[person.death_date.month - 1] = deathPerMonth[person.death_date.month - 1] + 1

			if person.birth_location is not None:
				birthLocations.increment(person.birth_location.city)

			if person.sex == 'F':
				gender.increment(_("Women"))
			else:
				gender.increment(_("Men"))
				
			if person.age() is not None and person.age() < youngestAge:
				youngestAge = person.age()
				youngestPerson = person
			
			if person.age() > oldestAge:
				oldestAge = person.age()
				oldestPerson = person
				
			if person.ageAtMarriage() > latestMarriageAge:
				latestMarriageAge = person.ageAtMarriage()
				latestMarriagePerson = person
				
			if person.ageAtMarriage() is not None and person.ageAtMarriage() < youngestMarriageAge:
				youngestMarriageAge = person.ageAtMarriage()
				youngestMarriagePerson = person
				
			if person.children_count() > mostChildrenCount:
				mostChildrenCount = person.children_count()
				mostChildrenPerson = person
				
			children.increment('%d' % person.children_count())
		
		# sort & limit birth location to 10 (+rest)
		birthLocations.limit(10)
		
		specials.add("%s:,%s" % (_("Youngest person"), youngestPerson), youngestAge)
		specials.add("%s:,%s" % (_("Oldest person"), oldestPerson), oldestAge)
		specials.add("%s:,%s" % (_("Lastest marriage"), latestMarriagePerson), latestMarriageAge)
		specials.add("%s:,%s" % (_("Youngest marriage"), youngestMarriagePerson), youngestMarriageAge)
		specials.add("%s:,%s" % (_("Most Children"), mostChildrenPerson), mostChildrenCount)
		
		#Most children: <br />
		
		return StatisticsInfo(birthPerMonth, deathPerMonth, gender, birthLocations, children, specials)
	
	def timeline(self):
		result_list = []
		partner = None
		
		for ancestryPerson in AncestryRelation.objects.filter(ancestry = self):
			person = ancestryPerson.person
			if person.birth_date is not None:
				if person.birth_location is not None:
					if person.birth_name is not None and person.birth_name <> '':
						result_list.append(TimelineInfo(person.birth_date, _('%s %s (born %s) was born in %s') % (person.first_name, person.last_name, person.birth_name, person.birth_location)))
					else:
						result_list.append(TimelineInfo(person.birth_date, _('%s %s was born in %s') % (person.first_name, person.last_name, person.birth_location)))
				else:
					result_list.append(TimelineInfo(person.birth_date, _('%s %s was born') % (person.first_name, person.last_name)))
			
			if ancestryPerson.person.death_date is not None:
				if person.death_location is not None:
					result_list.append(TimelineInfo(person.death_date, _('%s %s has died in %s') % (person.first_name, person.last_name, person.death_location)))
				else:
					result_list.append(TimelineInfo(person.death_date, _('%s %s has died') % (person.first_name, person.last_name)))
			
			for familyStatusRelation in FamilyStatusRelation.objects.filter(woman = person):
				if familyStatusRelation.date is not None:
					if familyStatusRelation.status == 'M':
						if familyStatusRelation.location is not None:
							result_list.append(TimelineInfo(familyStatusRelation.date, _('marriage of %s and %s in %s') % (familyStatusRelation.husband_name(), familyStatusRelation.wife_name(), familyStatusRelation.location)))
						else:
							result_list.append(TimelineInfo(familyStatusRelation.date, _('marriage of %s and %s') % (familyStatusRelation.husband_name(), familyStatusRelation.wife_name())))
					else:
						result_list.append(TimelineInfo(familyStatusRelation.date, _('divorce of %s and %s') % (familyStatusRelation.husband_name(), familyStatusRelation.wife_name())))
			
		result_list = sorted(result_list, key=attrgetter('date'), reverse=True)
		grouped_list = [list(g) for k, g in groupby(result_list, key=lambda x: x.date.year)]
		
		final_list = []
		for grouped_item in grouped_list:
			final_list.append(GroupedTimelineInfo(grouped_item[0].date.year, grouped_item))
		
		return final_list
		
	def appendices(self):
		appendix_list = []
		for documentRelation in DocumentRelation.objects.all():
			# check if document belongs to a person this ancestry
			if not is_empty(AncestryRelation.objects.filter(ancestry = self, person = documentRelation.person)):	
				if documentRelation.document not in appendix_list:
					appendix_list.append(documentRelation.document)
		
		appendix_list = sorted(appendix_list, key=attrgetter('date'), reverse=True)
		
		return appendix_list
	
	def distributions(self):
		return DistributionRelation.objects.filter(ancestry = self)
	
	def __unicode__(self):			  
		return self.name

class DistributionRelation(models.Model):
	distribution = models.ForeignKey(Distribution)
	ancestry = models.ForeignKey(Ancestry)
	
	def __unicode__(self):			  
		return '%s - %s' % (self.ancestry.name, self.distribution.family_name)

def person_of_document_relation(x):
	return x.person

class Document(models.Model):
	name = models.CharField(max_length=200)
	date = models.DateField(_('date of creation'))
	image = models.ImageField(upload_to='media/documents', blank=True, null=True)
	
	def person_names(self):
		str = ''
		
		for item in DocumentRelation.objects.filter(document = self):
			str = '%s, %s' % (str, item.person)
		
		str = "$%s$" % (str)
		str = str.replace("$, ", "")
		str = str.replace(", $", "")
		str = str.replace("$", "")
		
		return mark_safe(str)
	
	def persons(self):
		return map(person_of_document_relation, DocumentRelation.objects.filter(document = self))
	
	def thumbnail(self):
		return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
	
	def __unicode__(self):			  
		return self.name

class DocumentRelation(models.Model):
	person = models.ForeignKey(Person)
	document = models.ForeignKey(Document)
	
	def __unicode__(self):			  
		return mark_safe(u'%s - %s' % (self.person, self.document.name))
		

class Question(models.Model):
	person = models.ForeignKey(Person)
	question = models.CharField(max_length=100)
	answer = models.CharField(max_length=100, null=True, blank=True)
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

def ancestry_relation(from_person, to_person):
	"""
		derives the relation status from person from_person to to_person
	"""
	#return '%s -> %s' % (from_person, to_person)
	
	if from_person.father == to_person or from_person.mother == to_person:
		if from_person.female(): 
			return _('daugther')
		else: 
			return _('son')
	
	if from_person.father is not None:
		if from_person.father.mother == to_person or from_person.father.father == to_person:
			if from_person.female(): 
				return _('granddaugther')
			else: 
				return _('grandson')
				
	if from_person.mother is not None:
		if from_person.mother.mother == to_person or from_person.mother.father == to_person:
			if from_person.female(): 
				return _('granddaugther')
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
							return _('girl cousins daugther')
						if from_person.female() and fathers_sibling_child.male():
							return _('boy cousins daugther')
						if from_person.male() and fathers_sibling_child.female():
							return _('girl cousins son')
						else: 
							return _('boy cousins son')
		
		if to_person.father.father == from_person:
			return _('grandfather')
			
		if to_person.father.father is not None:
			if to_person.father.father.father is not None:
				if to_person.father.father.father == from_person:
					return _('greatgrandfather')
					
				if to_person.father.father.father.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.father.father.father.mother == from_person:
					return _('greatgreatgrandmother')
				
			if to_person.father.father.mother is not None:
				if to_person.father.father.mother == from_person:
					return _('greatgrandmother')
				
				if to_person.father.father.mother.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.father.father.mother.mother == from_person:
					return _('greatgreatgrandmother')
		
		if to_person.father.mother == from_person:
			return _('grandmother')
			
		if to_person.father.mother is not None:
			if to_person.father.mother.father is not None:
				if to_person.father.mother.father == from_person:
					return _('greatgrandfather')
				
				if to_person.father.mother.father.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.father.mother.father.mother == from_person:
					return _('greatgreatgrandmother')	
				
			if to_person.father.mother.mother is not None:
				if to_person.father.mother.mother == from_person:
					return _('greatgrandmother')
				
				if to_person.father.mother.mother.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.father.mother.mother.mother == from_person:
					return _('greatgreatgrandmother')	
		
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
							return _('girl cousins daugther')
						if from_person.female() and mothers_sibling_child.male():
							return _('boy cousins daugther')
						if from_person.male() and mothers_sibling_child.female():
							return _('girl cousins son')
						else: 
							return _('boy cousins son')
		
		if to_person.mother.father == from_person:
			return _('grandfather')
			
		if to_person.mother.father is not None:
			if to_person.mother.father.father is not None:
				if to_person.mother.father.father == from_person:
					return _('greatgrandfather')
					
				if to_person.mother.father.father.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.mother.father.father.mother == from_person:
					return _('greatgreatgrandmother')
			
			if to_person.mother.father.mother is not None:	
				if to_person.mother.father.mother == from_person:
					return _('greatgrandmother')
					
				if to_person.mother.father.mother.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.mother.father.mother.mother == from_person:
					return _('greatgreatgrandmother')
		
		if to_person.mother.mother == from_person:
			return _('grandmother')
			
		if to_person.mother.mother is not None:
			if to_person.mother.mother.father is not None:
				if to_person.mother.mother.father == from_person:
					return _('greatgrandfather')
				
				if to_person.mother.mother.father.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.mother.mother.father.mother == from_person:
					return _('greatgreatgrandmother')
				
			if to_person.mother.mother.mother is not None:
				if to_person.mother.mother.mother == from_person:
					return _('greatgrandmother')
					
				if to_person.mother.mother.mother.father == from_person:
					return _('greatgreatgrandfather')
					
				if to_person.mother.mother.mother.mother == from_person:
					return _('greatgreatgrandmother')
	
	if from_person.wife() is not None:
		if from_person.wife().father == to_person or from_person.wife().mother == to_person:
			return _('son in law')
	
	if from_person.husband() is not None:
		if from_person.husband().father == to_person or from_person.husband().mother == to_person:
			return _('daugther in law')
	
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

class AncestryRelation(models.Model):
	person = models.ForeignKey(Person)
	ancestry = models.ForeignKey(Ancestry)
	featured = models.NullBooleanField(default=False, blank=True, null=True)
	
	def relation(self):
		featured_person = self.ancestry.featured()[0]
		return ancestry_relation(self.person, featured_person.person)
	
	def __unicode__(self):
		return u'%s' % (self.ancestry.name)
		
class FamilyStatusRelation(models.Model): 
	status = models.CharField(max_length=1, choices=(('M', _('Marriage')), ('D', _('Divorce')), ('P', _('Partnership')), ('A', _('Adoption'))))
	date = models.DateField(_('date of marriage or divorce'), null=True, blank=True)
	date_only_year = models.BooleanField(default=False)
	man = models.ForeignKey(Person, related_name = _('husband'), blank=True, null=True)
	woman = models.ForeignKey(Person, related_name = _('wife'), blank=True, null=True)
	husband_extern = models.CharField(max_length=50, blank=True, null=True)
	wife_extern = models.CharField(max_length=50, blank=True, null=True)
	location = models.ForeignKey(Location, blank=True, null=True) 

	def husband_name(self):
		if self.man is not None:
			return '%s %s' % (self.man.first_name, self.man.last_name)
		else:
			return self.husband_extern
			
	def wife_name(self):
		if self.woman is not None:
			return '%s %s' % (self.woman.first_name, self.woman.last_name)
		else:
			return self.wife_extern
			
	def status_name(self):
		if self.status == 'M':			
			return _("married")
		else:
			if self.status == 'P':			
				return _("partnership")
			else:
				return _("divorced")
				
		return "---"

	def __unicode__(self):  
		if self.man is not None:
			husbandStr = '%s %s' % (self.man.first_name, self.man.last_name)
		else:
			husbandStr = self.husband_extern
			
		if self.woman is not None:
			wifeStr = '%s %s' % (self.woman.first_name, self.woman.last_name)
		else:
			wifeStr = self.wife_extern
			
		str = ''
		if self.status == 'M':			
			str = _('Marriage %s and %s') % (husbandStr, wifeStr)
		else:
			if self.status == 'P':			
				str = _('Partnership %s and %s') % (husbandStr, wifeStr)
			else:
				str = _('Divorce %s and %s') % (husbandStr, wifeStr)
				
		return mark_safe((' ' + str + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip())
			
