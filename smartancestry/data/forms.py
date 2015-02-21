from django.contrib import admin
from data.models import Ancestry, AncestryRelation, FamilyStatusRelation, Person
from django.forms import CheckboxSelectMultiple
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class PersonAncestryListFilter(admin.SimpleListFilter):
	title = _('Ancestry')
	
	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'ancestry'
	
	def lookups(self, request, model_admin):
		"""
		Returns a list of tuples. The first element in each
		tuple is the coded value for the option that will
		appear in the URL query. The second element is the
		human-readable name for the option that will appear
		in the right sidebar.
		"""
		prompts = []
		for ancestry in Ancestry.objects.all():
			prompts.append((ancestry.name, _(ancestry.name)))
			
		return prompts
	
	def queryset(self, request, queryset):
		"""
		Returns the filtered queryset based on the value
		provided in the query string and retrievable via
		`self.value()`.
		"""
		if self.value():
			return queryset.filter(ancestryrelation__ancestry__name=self.value())
		else:
			return queryset

class AncestryRelationInline(admin.TabularInline):
	model = AncestryRelation
	extra = 4
	
	def get_extra (self, request, obj=None, **kwargs):
		"""Dynamically sets the number of extra forms. 0 if the related object
		already exists or the extra configuration otherwise."""
		if obj:
			# Don't add any extra forms if the related object already exists.
			return 1
			
		return self.extra

class HusbandFamilyStatusRelationInline(admin.TabularInline):
	model = FamilyStatusRelation
	fk_name = "man"
	extra = 4
	
	def get_extra (self, request, obj=None, **kwargs):
		""" hide all extra if the current user is having the wrong gender """
		try:
			person_id = request.path.replace('/admin/data/person/', '').replace('/', '')
			if person_id <> 'add':
				person = Person.objects.get(id = person_id)
				if person.sex == 'F':
					return 0
		except Person.DoesNotExist:
			pass
		
		"""Dynamically sets the number of extra forms. 0 if the related object
		already exists or the extra configuration otherwise."""
		if obj:
			# Don't add any extra forms if the related object already exists.
			return 1
		return self.extra

class WifeFamilyStatusRelationInline(admin.TabularInline):
	model = FamilyStatusRelation
	fk_name = "woman"
	extra = 4
	
	def get_extra (self, request, obj=None, **kwargs):
		""" hide all extra if the current user is having the wrong gender """
		try:
			person_id = request.path.replace('/admin/data/person/', '').replace('/', '')
			if person_id <> 'add':
				person = Person.objects.get(id = person_id)
				if person.sex == 'M':
					return 0
		except Person.DoesNotExist:
			pass
		
		"""Dynamically sets the number of extra forms. 0 if the related object
		already exists or the extra configuration otherwise."""
		if obj:
			# Don't add any extra forms if the related object already exists.
			return 1
		return self.extra

class PersonAncestryListFilter(admin.SimpleListFilter):
	title = _('Family - Father')
	
	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'ancestry'

class PersonAdmin(admin.ModelAdmin):
	list_display = ('user_name', 'thumbnail', 'birth_date', 'birth_location', 'death_date', 'death_location', 'father_name', 'mother_name', 'ancestry_names')
	list_filter = ('birth_date', ) #PersonAncestryListFilter,
	ordering = ('-birth_date',)
	inlines = [
		AncestryRelationInline,
		HusbandFamilyStatusRelationInline,
		WifeFamilyStatusRelationInline,
	]
	actions_on_top = True
	actions_on_bottom = True

def export_pdf(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect("/data/export/ancestry/%s/" % (",".join(selected)))
    
export_pdf.short_description = "create pdf"

class AncestryAdmin(admin.ModelAdmin):
    list_display = ['name', 'thumbnail', 'export']
    ordering = ['name']
    
    actions = [export_pdf]

class LocationAdmin(admin.ModelAdmin):
	list_display = ('city', 'state', 'country', 'thumbnail', 'lon', 'lat')
	ordering = ('city',)
	actions_on_top = True
	actions_on_bottom = True
    
