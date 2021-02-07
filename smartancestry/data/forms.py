import logging

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from .models import Ancestry, FamilyStatusRelation, Person, DocumentRelation, Question, \
    DocumentAncestryRelation, PersonEvent, AncestryRelation, AncestryTreeRelation, Document

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


class AncestryTreeRelationInline(admin.TabularInline):
    model = AncestryTreeRelation
    extra = 1

    def get_extra(self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
		already exists or the extra configuration otherwise."""
        if obj:
            # Don't add any extra forms if the related object already exists.
            return 1

        return self.extra


class AncestryRelationInline(admin.TabularInline):
    model = AncestryRelation
    extra = 1

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


class HusbandFamilyStatusRelationInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(HusbandFamilyStatusRelationInlineFormSet, self).clean()

        for form in self.forms:
            if not form.is_valid():
                return  # other errors exist, so don't bother

            if self.can_delete and self._should_delete_form(form):
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            if form.cleaned_data:
                woman = form.cleaned_data['woman']
                wife_extern = form.cleaned_data['wife_extern']

                if woman is not None and wife_extern is not None:
                    raise ValidationError(_('You cant have both woman and wife_extern filled.'))


class HusbandFamilyStatusRelationInline(admin.TabularInline):
    model = FamilyStatusRelation
    fk_name = "man"
    extra = 1
    exclude = ['husband_extern']
    verbose_name = u'Wife'
    verbose_name_plural = u'Wives'
    fields = ('status', 'date', 'date_only_year', 'woman', 'wife_link', 'wife_extern', 'location', 'ended')
    readonly_fields = ('wife_link',)

    formset = HusbandFamilyStatusRelationInlineFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "man":
            kwargs["queryset"] = Person.objects.filter(sex='F').order_by('-birth_date')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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


class WifeFamilyStatusRelationInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(WifeFamilyStatusRelationInlineFormSet, self).clean()

        for form in self.forms:
            if not form.is_valid():
                return  # other errors exist, so don't bother

            if self.can_delete and self._should_delete_form(form):
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            if form.cleaned_data:
                man = form.cleaned_data['man']
                husband_extern = form.cleaned_data['husband_extern']

                if man is not None and husband_extern is not None:
                    raise ValidationError(_('You cant have both man and husband_extern filled.'))


class WifeFamilyStatusRelationInline(admin.TabularInline):
    model = FamilyStatusRelation
    fk_name = "woman"
    extra = 1
    exclude = ['wife_extern']
    verbose_name = u'Husband'
    verbose_name_plural = u'Husbands'
    fields = ('status', 'date', 'date_only_year', 'man', 'husband_link', 'husband_extern', 'location', 'ended')
    readonly_fields = ('husband_link',)

    formset = WifeFamilyStatusRelationInlineFormSet

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "man":
            kwargs["queryset"] = Person.objects.filter(sex='M').order_by('-birth_date')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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

    list_display = ['event_type', 'date', 'location']
    fields = ('type', 'date', 'person', 'location', 'description')


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'user_name', 'birth_name', 'thumbnail', 'birth', 'death', 'father_name_linked', 'mother_name_linked',
        'partner_names_linked', 'ancestry_names',
        'number_of_questions',)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'birth_name', 'sex')
        }),
        ('Dates/Locations', {
            'fields': ('birth_date', 'birth_date_only_year', 'birth_date_unclear', 'birth_location', 'death_date',
                       'death_date_only_year', 'already_died', 'death_location', 'cause_of_death')
        }),
        ('Relations', {
            'fields': (
                'father',
                # 'father_link',
                'father_extern', 'mother',
                #'mother_link',
                'mother_extern', 'children_extern',
                'children_text', 'siblings_extern', 'siblings_text', 'relation_str')
        }),
        ('Notes', {
            'fields': (
                'profession', 'external_identifier', 'notes', 'image', 'thumbnail', 'automatic_questions_list', 'tree_link', 'export_link')
        }),
    )
    search_fields = ['first_name', 'last_name', ]
    readonly_fields = (
        'children_text', 'father_link', 'mother_link', 'thumbnail', 'tree_link', 'siblings_text', 'relation_str',
        'automatic_questions_list', 'export_link')
    raw_id_fields = ('father', 'mother',)
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
    actions = []

    class Media:
        js = ('admin/admin.js',)
        css = {
            'all': ('admin/person.css',)
        }

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(PersonAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'notes':
            formfield.widget = forms.Textarea(attrs={"rows": 5, "cols": 80})
        return formfield


def export_pdf(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    return HttpResponseRedirect("/data/export/ancestry/%s/" % (",".join(selected)))


export_pdf.short_description = _("Create pdfs")


class DocumentAncestryAncestryRelationInline(admin.TabularInline):
    model = DocumentAncestryRelation
    fk_name = "ancestry"

    extra = 1


class AncestryAdmin(admin.ModelAdmin):
    list_display = ['name', 'thumbnail', 'number_of_members', 'featured_str', 'exports']
    fields = ('name', 'thumbnail', 'image', 'map', 'featured', 'statistic_links',)
    readonly_fields = ('thumbnail', 'featured_str', 'statistic_links',)

    ordering = ['name']
    inlines = [
        AncestryTreeRelationInline,
        AncestryRelationInline,
        DocumentAncestryAncestryRelationInline,
    ]
    actions = [export_pdf]

    class Media:
        js = ('admin/admin.js',)
        pass


class FamilyStatusRelationAdmin(admin.ModelAdmin):
    list_display = ['status_name', 'husband_link', 'wife_link', 'date', 'location']

    class Media:
        pass


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


class LocationFamilyStatusRelationInline(admin.TabularInline):
    model = FamilyStatusRelation
    fk_name = "location"

    verbose_name_plural = _('List of family status locations')

    can_delete = False
    extra = 0

    fields = ('status_name', 'husband_link', 'wife_link', 'admin_url',)
    readonly_fields = ('status_name', 'husband_link', 'wife_link', 'admin_url',)

    def admin_url(self, obj):
        return '<a href="/admin/data/familystatusrelation/%s/" target="_blank">Admin</a>' % (obj.id)

    admin_url.allow_tags = True

    def has_add_permission(self, request):
        return False


class LocationEventRelationInline(admin.TabularInline):
    model = PersonEvent
    fk_name = "location"

    verbose_name_plural = _('List of personal events')

    can_delete = False
    extra = 0

    fields = ('event_type', 'first_name', 'last_name', 'admin_url',)
    readonly_fields = ('event_type', 'first_name', 'last_name', 'admin_url',)

    def admin_url(self, obj):
        return '<a href="/admin/data/personevent/%s/" target="_blank">Admin</a>' % (obj.id)

    admin_url.allow_tags = True

    def has_add_permission(self, request):
        return False


class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country', 'thumbnail', 'lon', 'lat')
    fields = ('thumbnail', 'city', 'state', 'country', 'image', 'lon', 'lat', 'map',)
    readonly_fields = ('thumbnail', 'map',)

    ordering = ('city',)
    inlines = [
        LocationBirthRelationInline,
        LocationDeathRelationInline,
        LocationFamilyStatusRelationInline,
        LocationEventRelationInline,
    ]
    actions = None

    class Media:
        pass


class DocumentPersonRelationInline(admin.TabularInline):
    model = DocumentRelation
    fk_name = "document"

    raw_id_fields = ('person',)
    extra = 1


class DocumentAncestryRelationInline(admin.TabularInline):
    model = DocumentAncestryRelation
    fk_name = "document"

    extra = 1


class DocumentAncestryFilter(admin.SimpleListFilter):
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
            prompts.append((ancestry.id, _(ancestry.name)))

        return prompts

    def queryset(self, request, queryset):
        """
		Returns the filtered queryset based on the value
		provided in the query string and retrievable via
		`self.value()`.
		"""
        if self.value():
            documents = []
            for document in Document.objects.all():
                should_add = False
                for ancestry in document.ancestries():
                    if str(ancestry.id) == str(self.value()):
                        should_add = True

                if should_add:
                    documents.append(document.id)

            return queryset.filter(id__in=documents)
        else:
            return queryset


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'date', 'name', 'type', 'person_names', 'ancestry_names', 'admin_url',)
    readonly_fields = ('thumbnail_large', 'ancestry_names', 'admin_url',)

    list_filter = DocumentAncestryFilter,

    ordering = ('date',)
    inlines = [
        DocumentPersonRelationInline,
        DocumentAncestryRelationInline,
    ]

    actions = None

    def admin_url(self, obj):
        return '<a href="/admin/data/document/%s/" target="_blank">Admin</a>' % obj.id

    admin_url.allow_tags = True

    class Media:
        pass


class QuestionAncestryListFilter(admin.SimpleListFilter):
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
            prompts.append((ancestry.id, _(ancestry.name)))

        return prompts

    def queryset(self, request, queryset):
        """
		Returns the filtered queryset based on the value
		provided in the query string and retrievable via
		`self.value()`.
		"""
        # print("abc=%s" % self.value())
        # print(queryset)
        if self.value():
            ancestry_relations = AncestryRelation.objects.filter(ancestry=self.value())
            persons = ancestry_relations.values_list('person', flat=True)
            return queryset.filter(person__pk__in=persons)
        else:
            return queryset


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'person', 'answer', 'admin_url')

    list_filter = QuestionAncestryListFilter,

    def admin_url(self, obj):
        return '<a href="/admin/data/question/%s/">Admin</a>' % obj.id

    admin_url.allow_tags = True

    class Media:
        pass


class DocumentAncestryRelationAdmin(admin.ModelAdmin):
    class Media:
        pass


class PersonEventAdmin(admin.ModelAdmin):
    list_display = ('person', 'type', 'date', 'location', 'admin_url')

    def admin_url(self, obj):
        return '<a href="/admin/data/personevent/%s/">Admin</a>' % obj.id

    admin_url.allow_tags = True

    class Media:
        pass


class HistoryEventAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'date', 'admin_url')
    readonly_fields = ('thumbnail', 'admin_url',)

    def admin_url(self, obj):
        return '<a href="/admin/data/historyevent/%s/">Admin</a>' % obj.id

    admin_url.allow_tags = True

    class Media:
        pass