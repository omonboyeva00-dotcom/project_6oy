from django.template.context_processors import request
from rest_framework import serializers,status

from .models import CODE_VERIFY,CustomUser,VIA_EMAIL,VIA_PHONE
from rest_framework.exceptions import ValidationError
from shared.utility import check_email_or_phone
from django.db.models import Q


class SignUpSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    auth_status=serializers.CharField(read_only=True)
    verify_type=serializers.CharField(read_only=True)

    def __init__(self,instance=None,data=...,**kwargs):
        super().__init__(instance,data,**kwargs)
        self.fields['email_or_phone']=serializers.CharField(write_only=True,required=True)

    class Meta:
        model=CustomUser
        fields=['id','auth_status','auth_type']
    def create(self, validated_data):
        user=super().create(validated_data)
        if user.auth_type==VIA_EMAIL:
            code=user.generate_code(VIA_EMAIL)
            # shu yerda send_email(user.emil,code)yozilishi kerak

        elif user.auth_type==VIA_PHONE:
            code=user.generate_code(VIA_PHONE)
        else:
            raise ValidationError('email yoki telefon raqam xato')
        return user


    def validate(self,attrs):
        super().validate(attrs)
        data=self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(user_input):
        user_input= user_input.data.get('email_or_phone')
        user_input_type= check_email_or_phone(user_input)
        if user_input_type=='phone':
            data={
                'auth_type':VIA_PHONE,
                'phone_number':user_input
            }

        elif user_input_type=='email':
            data={
                'auth_type':VIA_EMAIL,
                'email':user_input
            }

        else:
            response={
                'status':status.HTTP_400_BAD_REQUEST,
                'message': "email yoki telefon raqamingiz xato kiritilgan"
            }
            raise ValidationError(response)

        return data

    def validate_email_or_phone(self,email_or_phone):
        user=CustomUser.objects.filter(Q(phone_number=email_or_phone)| Q(email=email_or_phone))
        if not user:
            raise ValidationError(detail="bu email yoki telefon bilan oldin royxatdan otilgan")
        return email_or_phone


    def to_representation(self, instance):
        data=super().to_representation(instance)
        data['massage']='kodingiz yuborildi'
        data['refresh']=instance.token()['refresh']
        data['access']=instance.token()['access']
        return data








