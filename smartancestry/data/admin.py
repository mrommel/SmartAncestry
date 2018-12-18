from django.contrib import admin

# Register your models here.
from data.models import Person, Ancestry, AncestryRelation, FamilyStatusRelation, Location, Distribution, DistributionRelation, Document, DocumentRelation, Question, DocumentAncestryRelation
from data.forms import PersonAdmin, LocationAdmin, AncestryAdmin, DocumentAdmin

admin.site.register(Person, PersonAdmin)
admin.site.register(Question)
admin.site.register(Ancestry, AncestryAdmin)
admin.site.register(FamilyStatusRelation)
admin.site.register(Location, LocationAdmin)
admin.site.register(Distribution)
admin.site.register(DistributionRelation)

admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentRelation)
admin.site.register(DocumentAncestryRelation)