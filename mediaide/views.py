import datetime
import jwt
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes


from django.http.response import HttpResponse
from rest_framework import viewsets

from Mediaide import settings
from mediaide.confirmation import account_activation_token
from mediaide.models import CustomUser, CountryVisa, MedicalPackages, Facilities, UserEnquiry, ContactUs, Country, \
    UserDocuments
from mediaide.serializer import CustomUserSerializer, CountryVisaSerializer, MedicalPackagesSerializer, \
    FacilitiesSerializer, UserEnquirySerializer, ContactUsSerializer, UserDocumentsSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response

class RegisterUser(APIView):
    """
    Register a new user.
    """
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('Register successfully please check your email', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    queryset = CustomUser.objects.all()

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


#TODO UserName Must Be Unique
@permission_classes([AllowAny])

def confirm(request,confirmation_code, id):

    user = CustomUser.objects.get(id=int(id))
    if user and account_activation_token.check_token(user,confirmation_code) and user.date_joined > (
            timezone.now() - datetime.timedelta(days=1)):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class ResendMes(APIView):
    permission_classes = (AllowAny,)
    def post(self,request,format=None):
        email = request.data.get('email')
        user = CustomUser.objects.get(email=email)

        if user:
            title = "MediAide account confirmation"
            content = " welcome to Mediaide. below is the account activation link  " \
                      "http://52.14.255.120::8000/api/confirm/" + str(
                account_activation_token.make_token(user)) + '/' + str(user.id)+'/'

            user.email_user(title,content, 'no-reply@mediaide.com')
            return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny,])

def forget_password(request):
    email = request.data.get('email',None)
    user_object = CustomUser.objects.filter(email=email)

    if user_object.exists():
        user_object = user_object[0]

        title = " MediAide Password Reset Link "
        content = "below is the password reset link " \
                  "http://52.14.255.120::8000/api/confirm/" + str(
            account_activation_token.make_token(user_object))+'/'+str(user_object.id)

        user_object.email_user(title, content, 'no-reply@mediaide.com')
        return Response('check your email for reset link ')
    else:
        raise serializers.ValidationError('email not found')

@permission_classes([AllowAny,])
def reset_password(request):
    token = request.data.get('token',None)
    id = request.data.get('id',None)
    password = request.data.get('password', None)
    confirm_password = request.data.get('confirm_password', None)
    user = CustomUser.objects.get(id=id)

    if confirm_password!=password:
        raise serializers.ValidationError(
            "The passwords have to be the same"
        )

    if user and account_activation_token.check_token(user,token):
        user.set_password(password)
        user.save()
        return HttpResponse('password change')


class CustomUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserEnquiryView(viewsets.ModelViewSet):
    queryset = UserEnquiry.objects.all()
    serializer_class = UserEnquirySerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        super(UserEnquiryView,self).create(request, args, kwargs)
        return Response('Thank you for concern, soon our excutive will get in contact with you',status=status.HTTP_201_CREATED)
  


class ContactUsView(viewsets.ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = (AllowAny,)


    def create(self, request, *args, **kwargs):
        super(ContactUsView,self).create(request, args, kwargs)
        return Response('Thank you for your concern, soon our excutive will get contact with you',status=status.HTTP_201_CREATED)


class CountryVisaView(viewsets.ModelViewSet):
    queryset = CountryVisa.objects.all()
    serializer_class = CountryVisaSerializer



class MedicalPackagesView(viewsets.ModelViewSet):
    queryset = MedicalPackages.objects.all()
    serializer_class = MedicalPackagesSerializer
    permission_classes = (AllowAny,)


class FacilitiesView(viewsets.ModelViewSet):
    queryset = Facilities.objects.all()
    serializer_class = FacilitiesSerializer
    permission_classes = (AllowAny,)

@api_view(['POST'])
@permission_classes([AllowAny,])

def user_login( request):

    email = request.data.get('email',)
    password = request.data.get('password',)

    user = authenticate(email=email, password=password)

    if user and not user.is_active:
        raise serializers.ValidationError(' please verify email ')

    if user and user.is_active:
        encoded_token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm =settings.JWT_ALGORITHM)
        response_data = CustomUserSerializer().to_representation(user)
        response_data.update({'token':encoded_token})
        return Response(dict(response_data),status=status.HTTP_200_OK)
    else:
        raise serializers.ValidationError('incorrect email or password')


@api_view(['GET','POST'])
@permission_classes([AllowAny,])

def get_estimate_data(request):

    def validated_treatment(treatment):
        medical_package_instance = MedicalPackages.objects.filter(id=treatment)
        if medical_package_instance.exists():
            return medical_package_instance[0]
        else:
            raise serializers.ValidationError('No Such Medical Package Exits..')

    def validated_country(country):
        country_instance = Country.objects.filter(name=country)
        if country_instance.exists():
            return country_instance[0]
        else:
            raise serializers.ValidationError('No Such Country Exits..')

    def validate_patient(patients):
        if patients<=0:
            raise serializers.ValidationError(' number of patient should be 0')
        return patients

    if request.method == 'GET':

        response_dict = {}
        response_dict['country'] = Country.objects.all().values_list('name',flat=1)
        response_dict['treatment'] = MedicalPackages.objects.all().values('id','name_of_treatment')
        response_dict['facilities'] = Facilities.objects.all().values_list('name', flat=1)

        return Response(response_dict)

    if request.method=='POST':

        data = request.data

        treatment = validated_treatment(data.get('treatment',0))
        country = validated_country(data.get('country',))
        facilities = data.get('facilities',[])
        number_of_patient = data.get('patients')
        totel_treatment_cost = (treatment.approximate_cost*100000/60)*number_of_patient
        totel_treatment_cost =round(totel_treatment_cost,2)

        facilities = Facilities.objects.filter(name__in=facilities).values_list('cost',flat=1)
        facilities_cost=sum(facilitie/100000 for facilitie in facilities)*number_of_patient
        teratment_dict = model_to_dict(treatment)
        teratment_dict.update({'estimate_cost':totel_treatment_cost})
        return Response(teratment_dict)


class UserDocumentView(viewsets.ModelViewSet):
    queryset = UserDocuments.objects.all()
    serializer_class = UserDocumentsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


import xlrd
def upload_data(request):
#    ExcelFileName = 'treatments_info.xlsx'
    ExcelFileName = 'countries.xls'
    workbook = xlrd.open_workbook(ExcelFileName)
    worksheet = workbook.sheet_by_name("Sheet1")
    num_rows = worksheet.nrows
    num_cols = worksheet.ncols
    for curr_row in range(0, num_rows, 1):
        row_data = []

        for curr_col in range(0, num_cols, 1):
            data = worksheet.cell_value(curr_row, curr_col)  # Read the data in the current cell
            row_data.append(data)
  #      MedicalPackages.objects.create(name_of_treatment=row_data[1],no_of_days_in_hospital=row_data[2],no_of_days_out_hospital=row_data[3],approximate_cost=row_data[4])

        Country.objects.create(name=row_data[0].strip())

