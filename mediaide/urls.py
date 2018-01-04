from django.conf.urls import  url,include

from mediaide import views
from mediaide.views import Logout, ResendMes, UserEnquiryView, CustomUserView, MedicalPackagesView, \
    CountryVisaView, FacilitiesView, ContactUsView, user_login, get_estimate_data, forget_password, UserDocumentView
from .views import RegisterUser, upload_data

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'get-user', CustomUserView)
router.register(r'upload-document', UserDocumentView)
router.register(r'medical-package', MedicalPackagesView)
router.register(r'country-visa', CountryVisaView)
router.register(r'facilities', FacilitiesView)
router.register(r'user-enquiry', UserEnquiryView)
router.register(r'contact-us', ContactUsView)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^register/$', RegisterUser.as_view()),
    url(r'^logout/$', Logout.as_view()),
    url(r'^login/$', user_login),
    url(r'^upload-data/$', upload_data),

    url(r'^forgot-password/$', forget_password),
    url(r'^get-estimate/$', get_estimate_data),
    url(r'^resend-confirmation-mail/$', ResendMes.as_view()),
    url(r'^confirm/(?P<confirmation_code>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<id>[\w]+)/$',
        views.confirm,name='confirm'),
]

