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

# Get an instance of a logger
logger = logging.getLogger(__name__)

def calculate_age(born, death):
	return death.year - born.year - ((death.month, death.day) < (born.month, born.day))

class LocationInfo(object):
	def __init__(self, lon, lat):
		self.lon = lon
		self.lat = lat
		
	def lon_lat(self):
		return "{:10.4f}".format(self.lon) + ", " + "{:10.4f}".format(self.lat)

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

class PartnerInfo(object):
	def __init__(self, status, partner, partner_name, location, date):
		self.status = status
		self.partner = partner
		self.partner_name = partner_name
		self.location = location
		self.date = date
		
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
		self.full_name = name
		self.sex = gender
		self.birth_date = None
		self.birth_location = None
		self.death_date = None
		self.death_location = None
		
	def gender_sign(self):
		if self.sex == 'M':
			return "♂"
		else:
			return "♀"

def name_of_ancestry(x):
	return mark_safe(x.ancestry.name)

class Person(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	birth_name = models.CharField(max_length=50, blank=True, null=True)
	sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
	birth_date = models.DateField('date of birth')
	birth_location = models.ForeignKey(Location, blank=True, null=True, related_name="birth_location") 
	death_date = models.DateField('date of death', null=True, blank=True)
	death_location = models.ForeignKey(Location, blank=True, null=True, related_name="death_location") 
	already_died = models.NullBooleanField(default=False, blank=True, null=True)
	profession = models.CharField(max_length=50, blank=True, null=True)
	father = models.ForeignKey('self', blank=True, null=True, related_name="children_father")
	father_extern = models.CharField(max_length=50, blank=True, null=True)
	mother = models.ForeignKey('self', blank=True, null=True, related_name="children_mother")
	mother_extern = models.CharField(max_length=50, blank=True, null=True)
	children_extern = models.CharField(max_length=200, blank=True, null=True)
	siblings_extern = models.CharField(max_length=200, blank=True, null=True)
	notes = models.CharField(max_length=500, blank=True, null=True)  
	image = models.ImageField(upload_to='media/persons', blank=True, null=True)  
	
	def user_name(self):
		return str(self)
	
	user_name.short_description = 'Name'
	
	def full_name(self):
		return '%s %s' % ((' ' + str(self.first_name) + ' ').replace(" _", " <u>").replace("_ ", "</u> "), self.last_name)
	
	def gender_sign(self):
		if self.sex == 'M':
			return "♂"
		else:
			return "♀"
	
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
		return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
		
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
						partners.append(PartnerInfo(relation.status_name, relation.woman, "", relation.location, relation.date))
					else:
						partners.append(PartnerInfo(relation.status_name, None, relation.wife_extern, relation.location, relation.date))
				return partners
			except FamilyStatusRelation.DoesNotExist:
				pass
		
		if self.sex == 'F':
			try:
				partners = []
				for relation in FamilyStatusRelation.objects.filter(woman = self):
					if relation.man is not None:
						partners.append(PartnerInfo(relation.status_name, relation.man, "", relation.location, relation.date))
					else:
						partners.append(PartnerInfo(relation.status_name, None, relation.husband_extern, relation.location, relation.date))
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
	
		return siblings_list
		
	def siblings_extern_list(self):
		if self.siblings_extern is not None:
			return self.siblings_extern.split(',')
			
		return None
		
	def children(self):
		return Person.objects.filter(Q(father = self) | Q(mother = self))
		
	def children_extern_list(self):
		if self.children_extern is not None:
			return self.children_extern.split(',')
			
		return None
		
	def children_count(self):
		count = len(self.children())
		
		if self.children_extern_list() is not None:
			count = count + len(self.children_extern_list())
		
		return count
		
	def ancestries(self):
		return AncestryRelation.objects.filter(person = self) 

	def ancestry_names(self):
		return map(name_of_ancestry, AncestryRelation.objects.filter(person = self))
	
	def has_ancestry(self, ancestry_id):
		for ancestryRelation in AncestryRelation.objects.filter(person = self):
			if ancestryRelation.id == ancestry_id:
				return True
				
		return False
	
	def married_to(self):
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
	
	@models.permalink
	def get_absolute_url(self):
		return ('data.views.person', [str(self.id)])
	
	"""
		todo: return a pdf of the persons cv
	"""
	def export_pdf(self):
		pass
	
	def __unicode__(self):			  
		return mark_safe('%s %s' % ((' ' + str(self.first_name) + ' ').replace(" _", " <u>").replace("_ ", "</u> ").strip(), self.last_name))

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

COLORS = ( "#81D8D0", "#9ACD32", "#EDDA74", "#C85A17", "#FEECCF", "#F7464A", "#DDDDDC", "#E18B6B", "#7931DF", "#737CA1", "#1589FF", "#3BB9FF", 
	"#F76541", "#9ACD32", "#EDDA74", "#C85A17", "#FEECCF", "#F7464A", "#DDDDDC", "#E18B6B", "#7931DF", "#737CA1", "#1589FF", "#3BB9FF",
	"#F76541", "#9ACD32", "#EDDA74", "#C85A17", "#FEECCF", "#F7464A", "#DDDDDC", "#E18B6B", "#7931DF", "#737CA1", "#1589FF", "#3BB9FF",
	"#F76541", "#9ACD32", "#EDDA74", "#C85A17", "#FEECCF", "#F7464A", "#DDDDDC", "#E18B6B", "#7931DF", "#737CA1", "#1589FF", "#3BB9FF")
				
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
		
		self.list = result_list
		
	def values(self):
		result_list = []
		
		for item in self.list:
			result_list.append(item.value)
		
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

class Ancestry(models.Model):
	name = models.CharField(max_length=50)
	image = models.ImageField(upload_to='media/ancestries', blank=True, null=True)
	
	def thumbnail(self):
		return '<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>' % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
	
	def export(self):
		return '<a href="/data/export/ancestry/%d/" target="_blank">export</a>' % (self.id)
	export.allow_tags = True
	
	def members(self):
		result_list = AncestryRelation.objects.filter(ancestry = self)
		result_list = sorted(result_list, key=attrgetter('person.birth_date'), reverse=True)
		return result_list
	
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
				
			if person.age() < youngestAge:
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
	
	def __unicode__(self):			  
		return self.name

class AncestryRelation(models.Model):
	person = models.ForeignKey(Person)
	ancestry = models.ForeignKey(Ancestry)
	
	def __unicode__(self):			  
		return '%s' % (self.ancestry.name)
		
class FamilyStatusRelation(models.Model): 
	status = models.CharField(max_length=1, choices=(('M', 'Marriage'), ('D', 'Divorce'), ('P', 'Partnership')))
	date = models.DateField('date of marriage or divorce', null=True, blank=True)
	man = models.ForeignKey(Person, related_name = 'husband', blank=True, null=True)
	woman = models.ForeignKey(Person, related_name = 'wife', blank=True, null=True)
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
			return "Verheiratet"
		else:
			if self.status == 'P':			
				return "Partnerschaft"
			else:
				return "Geschieden"
				
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
			
		if self.status == 'M':			
			return 'Marriage %s and %s' % (husbandStr, wifeStr)
		else:
			if self.status == 'P':			
				return 'Partnership %s and %s' % (husbandStr, wifeStr)
			else:
				return 'Divorce %s and %s' % (husbandStr, wifeStr)
			
