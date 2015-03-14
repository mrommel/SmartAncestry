from django.contrib import admin

# Register your models here.
from data.models import Person, Ancestry, AncestryRelation, FamilyStatusRelation, Location, Distribution, DistributionRelation
from data.forms import PersonAdmin, LocationAdmin, AncestryAdmin

admin.site.register(Person, PersonAdmin)
admin.site.register(Ancestry, AncestryAdmin)
admin.site.register(AncestryRelation)
admin.site.register(FamilyStatusRelation)
admin.site.register(Location, LocationAdmin)
admin.site.register(Distribution)
admin.site.register(DistributionRelation)