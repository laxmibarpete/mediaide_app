from django.contrib import admin

from mediaide.models import MedicalPackages, CustomUser, UserTreatmentPackages, TermsAndConditions, \
    UserEnquiry, Facilities, ContactUs, UserDocuments, CountryVisa, Country

# Register your models here.

admin.site.register(CountryVisa)
admin.site.register(MedicalPackages)
admin.site.register(CustomUser)
admin.site.register(UserTreatmentPackages)
admin.site.register(TermsAndConditions)
admin.site.register(UserEnquiry)
admin.site.register(Facilities)
admin.site.register(ContactUs)
admin.site.register(UserDocuments)
admin.site.register(Country)

