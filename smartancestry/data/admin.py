from django.contrib import admin

from .forms import PersonAdmin, LocationAdmin, AncestryAdmin, DocumentAdmin

from .models import Person, Ancestry, FamilyStatusRelation, Location, Distribution, DistributionRelation, Document, \
    DocumentRelation, Question, DocumentAncestryRelation, PersonEvent

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
admin.site.register(PersonEvent)