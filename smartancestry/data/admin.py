from django.contrib import admin

# Register your models here.
from data.models import Person, Ancestry, AncestryRelation, FamilyStatusRelation, Location
from data.forms import PersonAdmin

admin.site.register(Person, PersonAdmin)

admin.site.register(Ancestry)
admin.site.register(AncestryRelation)
admin.site.register(FamilyStatusRelation)
admin.site.register(Location)