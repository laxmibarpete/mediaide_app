from django.core.mail import send_mail
from rest_framework import serializers

from mediaide.confirmation import account_activation_token
from mediaide.models import CustomUser, CountryVisa, Facilities, MedicalPackages, UserEnquiry, ContactUs, \
    UserDocuments


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'country', 'password', 'phone', 'address', 'dob', 'gender', 'confirm_password','doctor','services_need', 'treatment','hospital_name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active =True
        user.save()
        title = "MediAide account confirmation"
        content = " welcome to Mediaide. below is the account activation link ./n " \
                 "http://52.14.255.120::8000/api/confirm/"+str(account_activation_token.make_token(user))+'/'+str(user.id)

#        user.email_user(title, content, 'no-reply@mediaide.com',fail_silently=False)
        return user

    def update(self, instance, validated_data):

        return super(CustomUserSerializer, self).update( instance, validated_data)


    def validate(self, data):
        '''
        Ensure the passwords are the same
        '''
        if  data.has_key('agree') and not data['agree']:
            raise serializers.ValidationError(
                "Please accept term and condition"
            )

        if data.has_key('password'):
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError(
                    "The passwords have to be the same"
                )
            data.pop('confirm_password')

        return data


class UserDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        fields = ('user', 'description', 'document')

    def to_representation(self, value):
        response = dict(super(UserDocumentsSerializer, self).to_representation(value))
        response['document'] = "{}{}".format('api', value.document.url)
        print response['document']
        return response

    
class CountryVisaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryVisa
        fields = ('name', 'email', 'phone', 'fax', 'website', 'embassy')


class MedicalPackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalPackages
        fields = ('id', 'name_of_treatment', 'no_of_days_in_hospital', 'no_of_days_out_hospital', 'approximate_cost')


class FacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = ('name','cost')


class UserEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEnquiry
        fields = ('id', 'name', 'dob', 'phone', 'gender', 'email', 'message', 'appointment_date', 'reason')

    def create(self, validate_data):
        contact_us = super(UserEnquirySerializer, self).create(validate_data)

        subject = 'Welcome to MediAide'
        message = 'Hi ' \
                  'Welcome to MediAide and thanks for your contact with our onlinetraining program./n ' \
                  'Please find course details below. ' \
                  'Request you to send your timings and respond back to this email immediately.' \
                  ' So we can confirm training schedule and software/material as per your requirement.'

   #     send_mail(subject, message, 'no-reply@mediaide.com', [validate_data['email']])
        return contact_us


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ('id', 'name','email','message','subject','phone')

    def create(self,validate_data):
        contact_us = super(ContactUsSerializer ,self).create(validate_data)

        subject = 'Welcome to MediAide'
        message ='''
                 Hi,
                    
                    Welcome to Mediaide, this is regarding your request. Our executive will soon contact you.
                 
                 Regards
                 
                 MediAide 
                 '''


    #    send_mail(subject, message, 'no-reply@mediaide.com', [validate_data['email']])
        return contact_us


