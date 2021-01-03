import logging

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from .models import Ancestry, FamilyStatusRelation, Person, DocumentRelation, Question, \
    DocumentAncestryRelation, PersonEvent, AncestryRelation

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

    def get_extra(self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
		already exists or the extra configuration otherwise."""
        if obj:
            # Don't add any extra forms if the related object already exists.
            return 1

        return self.extra


class DocumentRelationInline(admin.TabularInline):
    model = DocumentRelation
    extra = 2

    def get_extra(self, request, obj=None, **kwargs):
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
    exclude = ['husband_extern']
    verbose_name = u'Wife'
    verbose_name_plural = u'Wifes'
    fields = ('status', 'date', 'date_only_year', 'woman', 'wife_link', 'wife_extern', 'location', 'ended')
    readonly_fields = ('wife_link',)

    def get_extra(self, request, obj=None, **kwargs):
        """ hide all extra if the current user is having the wrong gender """
        try:
            person_id = request.path.replace('/admin/data/person/', '').replace('/', '').replace('change', '')
            if person_id != 'add':
                person = Person.objects.get(id=person_id)
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
    exclude = ['wife_extern']
    verbose_name = u'Husband'
    verbose_name_plural = u'Husbands'
    fields = ('status', 'date', 'date_only_year', 'man', 'husband_link', 'husband_extern', 'location', 'ended')
    readonly_fields = ('husband_link',)

    def get_extra(self, request, obj=None, **kwargs):
        """ hide all extra if the current user is having the wrong gender """
        try:
            person_id = request.path.replace('/admin/data/person/', '').replace('/', '').replace('change', '')
            if person_id != 'add':
                person = Person.objects.get(id=person_id)
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


class QuestionInline(admin.TabularInline):
    model = Question
    fk_name = "person"
    extra = 1


class PersonEventInline(admin.TabularInline):
    model = PersonEvent
    fk_name = "person"
    extra = 1

    list_display = ['type', 'date']
    fields = ('type', 'date', 'person', 'location')


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'user_name', 'birth_name', 'thumbnail', 'birth', 'death', 'father_name_linked', 'mother_name_linked', 'partner_names_linked', 'ancestry_names',
        'number_of_questions',)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'birth_name', 'sex')
        }),
        ('Dates/Locations', {
            'fields': ('birth_date', 'birth_date_unclear', 'birth_date_only_year', 'birth_location', 'death_date',
                       'death_date_only_year', 'death_location', 'cause_of_death', 'already_died')
        }),
        ('Relations', {
            'fields': (
                'father', 'father_link', 'father_extern', 'mother', 'mother_link', 'mother_extern', 'children_extern',
                'children_text', 'siblings_extern', 'siblings_text', 'relation_str')
        }),
        ('Notes', {
            'fields': ('profession', 'notes', 'external_identifier', 'thumbnail', 'image', 'tree_link')
        }),
    )
    search_fields = ['first_name', 'last_name', ]
    readonly_fields = (
        'children_text', 'father_link', 'mother_link', 'thumbnail', 'tree_link', 'siblings_text', 'relation_str')
    # raw_id_fields = ('father', 'mother',)
    # list_filter = ('birth_date', 'ancestries', ) #PersonAncestryListFilter,
    list_filter = PersonAncestryListFilter,
    ordering = ('-birth_date',)
    inlines = [
        AncestryRelationInline,
        HusbandFamilyStatusRelationInline,
        WifeFamilyStatusRelationInline,
        DocumentRelationInline,
        QuestionInline,
        PersonEventInline,
    ]
    actions = None

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(PersonAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'notes':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield


def export_pdf(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect("/data/export/ancestry/%s/" % (",".join(selected)))


export_pdf.short_description = _("Create pdfs")


class AncestryRelationInline(admin.TabularInline):
    model = AncestryRelation
    fk_name = "ancestry"
    extra = 1

    list_display = ['person', 'featured']
    fields = ('person', 'featured', 'relation',)
    readonly_fields = ('relation',)


class AncestryAdmin(admin.ModelAdmin):
    list_display = ['name', 'thumbnail', 'number_of_members', 'featured_str', 'export', 'export_questions', 'export_no_documents', 'export_raw']
    fields = ('name', 'thumbnail', 'image', 'map', 'featured_str',)
    readonly_fields = ('thumbnail', 'featured_str',)

    ordering = ['name']
    inlines = [
        AncestryRelationInline,
    ]
    actions = [export_pdf]


class LocationBirthRelationInline(admin.TabularInline):
    model = Person
    fk_name = "birth_location"

    verbose_name_plural = _('List of Persons born here')

    can_delete = False
    extra = 0

    fields = ('first_name', 'last_name', 'admin_url',)
    readonly_fields = ('first_name', 'last_name', 'admin_url',)

    def admin_url(self, obj):
        return '<a href="/admin/data/person/%s/" target="_blank">Admin</a>' % (obj.id)

    admin_url.allow_tags = True

    def has_add_permission(self, request):
        return False


class LocationDeathRelationInline(admin.TabularInline):
    model = Person
    fk_name = "death_location"

    verbose_name_plural = _('List of Persons died here')

    can_delete = False
    extra = 0

    fields = ('first_name', 'last_name', 'admin_url',)
    readonly_fields = ('first_name', 'last_name', 'admin_url',)

    def admin_url(self, obj):
        return '<a href="/admin/data/person/%s/" target="_blank">Admin</a>' % (obj.id)

    admin_url.allow_tags = True

    def has_add_permission(self, request):
        return False


class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country', 'thumbnail', 'lon', 'lat')
    fields = ('thumbnail', 'city', 'state', 'country', 'image', 'lon', 'lat',)
    readonly_fields = ('thumbnail',)

    ordering = ('city',)
    inlines = [
        LocationBirthRelationInline,
        LocationDeathRelationInline,
    ]
    actions = None


class DocumentPersonRelationInline(admin.TabularInline):
    model = DocumentRelation
    fk_name = "document"


class DocumentAncestryRelationInline(admin.TabularInline):
    model = DocumentAncestryRelation
    fk_name = "document"


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'type', 'name', 'person_names', 'ancestry_names', 'admin_url',)
    readonly_fields = ('thumbnail', 'admin_url',)

    ordering = ('name',)
    inlines = [
        DocumentPersonRelationInline,
        DocumentAncestryRelationInline,
    ]

    actions = None

    def admin_url(self, obj):
        return '<a href="/admin/data/document/%s/" target="_blank">Admin</a>' % obj.id

    admin_url.allow_tags = True
