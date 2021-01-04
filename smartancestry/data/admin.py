from django.contrib import admin

from .forms import PersonAdmin, LocationAdmin, AncestryAdmin, DocumentAdmin, QuestionAdmin, PersonEventAdmin, FamilyStatusRelationAdmin

from .models import Person, Ancestry, FamilyStatusRelation, Location, Distribution, DistributionRelation, Document, \
    DocumentRelation, Question, DocumentAncestryRelation, PersonEvent

admin.site.register(Person, PersonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Ancestry, AncestryAdmin)
admin.site.register(FamilyStatusRelation, FamilyStatusRelationAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Distribution)
admin.site.register(DistributionRelation)

admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentRelation)
admin.site.register(DocumentAncestryRelation)
admin.site.register(PersonEvent, PersonEventAdmin)
