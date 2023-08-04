from rest_framework import serializers
# from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from login_portal.models import NDR_Documents, NDR_PrivacyPolicy
from .models import *
from django.contrib.auth import authenticate, get_user_model
from .utils import generate_qr
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
# User Serializer to display output
# class UserSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = User
#        fields = ('account_id',
#                  'Name_First',
#                  'Name_Last',
#                  'email',
#                  )
#
#
#    def validate(self,args):
#
#        if len(args)==0:
#            raise serializers.ValidationError("please enter the below fields to update")
#
#        for each_attr in args.keys():
#            if each_attr not in ('account_id', 'Name_First','Name_Last','email'):
#                raise serializers.ValidationError("unknown key {}".format(each_attr))
#
#        return super().validate(args)
#
#
#    def update(self, instance, validated_data):
#        # https://stackoverflow.com/questions/53779723/django-rest-framework-update-with-kwargs-from-validated-data
#
#        for attr, value in validated_data.items():
#            setattr(instance, attr, value)
#        instance.save()
#        return instance


from products.models import Reward

from django.core.exceptions import ObjectDoesNotExist


class Ndr_RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50, min_length=6, required=False,
                                   allow_blank=True)  # set required False just to provide/send custom validation from backend to frontend
    # username = serializers.CharField(required=False, allow_blank = True)
    password = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    country = serializers.CharField(max_length=50, required=False, allow_blank=True)
    PhotoID = serializers.FileField(required=False)
    Name_First = serializers.CharField(required=False, allow_blank=True)
    Name_Last = serializers.CharField(required=False, allow_blank=True)
    CountryOfBirth = serializers.CharField(required=False, allow_blank=True)
    Citizenship = serializers.CharField(required=False, allow_blank=True)
    Birth_Day = serializers.CharField(required=False, allow_blank=True)
    Birth_Month = serializers.CharField(required=False, allow_blank=True)
    Birth_Year = serializers.CharField(required=False, allow_blank=True)
    PhotoID_Number = serializers.CharField(required=False, allow_blank=True)
    user_lat = serializers.FloatField(max_value=None, min_value=None, required=False)
    user_long = serializers.FloatField(max_value=None, min_value=None, required=False)
    VerificationPersonalID = serializers.CharField(required=False, allow_blank=True)
    # Address_Number = serializers.CharField(required=False, allow_blank=True)
    # Address_Street1 = serializers.CharField(required=False, allow_blank=True)
    # Address_Street2 = serializers.CharField(required=False, allow_blank=True)
    # Address_City = serializers.CharField(required=False, allow_blank=True)
    # Address_Province = serializers.CharField(required=False, allow_blank=True)
    # Address_Postal = serializers.CharField(required=False, allow_blank=True)
    # Address_Country = serializers.CharField(required=False, allow_blank=True)
    CreditCard_Type = serializers.CharField(required=False, allow_blank=True)
    UserAccountType = serializers.CharField(required=False, allow_blank=True)
    hst_number = serializers.CharField(required=False, allow_blank=True)
    refered_by = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            # 'account_id',
            'email',
            'password',
            'phone_number',
            'UserAccountType',
            'country',
            'PhotoID',
            'Name_First',
            'Name_Last',
            'CountryOfBirth',
            'Citizenship',
            'Birth_Day',
            'Birth_Month',
            'Birth_Year',
            'PhotoID_Number',
            'user_lat',
            'user_long',
            'VerificationPersonalID',
            'CreditCard_Type',
            'hst_number',
            'refered_by',
        )
        # extra_kwargs = {'password': {'write_only': True}}

    def validate(self, args):
        email = args.get('email', None)
        # username = args.get('username',None)
        phone_number = args.get('phone_number', None)
        password = args.get('password', None)
        country = args.get('country', None)
        Name_First = args.get('Name_First', None)
        Name_Last = args.get('Name_Last', None)
        CountryOfBirth = args.get('CountryOfBirth', None)
        Citizenship = args.get('Citizenship', None)
        Birth_Day = args.get('Birth_Day', None)
        Birth_Month = args.get('Birth_Month', None)
        Birth_Year = args.get('Birth_Year', None)
        PhotoID_Number = args.get('PhotoID_Number', None)
        user_lat = args.get('user_lat', None)
        user_long = args.get('user_long', None)
        VerificationPersonalID = args.get('VerificationPersonalID', None)
        CreditCard_Type = args.get("CreditCard_Type", None)
        UserAccountType = args.get("UserAccountType", None)
        print('Ndr_RegisterSerializer', args)
        refered_by = args.get("refered_by", None)
        print('refered_by--', refered_by)

        # if str(phone_number).replace(" ", "") == '' or phone_number is None:
        #
        #    raise serializers.ValidationError("Please Provide a valid Phone Number")
        # if not is_valid_number(str(phone_number)):
        #
        #    raise serializers.ValidationError("Unable to send otp to %s, please enter a valid Phone Number" %str(phone_number))

        if str(email).replace(" ", "") == '' or email is None:
            raise serializers.ValidationError("please enter a valid email")

        # if str(username).replace(" ", "") == '' or username is None:

        #    raise serializers.ValidationError("Please provide a username")

        if str(password).replace(" ", "") == '' or password is None:
            raise serializers.ValidationError("please enter password")
        # if len(username)<2  :

        #    raise serializers.ValidationError("minimum length of username is 2")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("email already exists")

        # if User.objects.filter(username=username).exists():

        #    raise serializers.ValidationError("username already exists")

        if str(country).replace(" ", "") == '' or email is None:
            raise serializers.ValidationError("please enter Country ")

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Phone Number already exists")

        if Account_type.objects.filter(AccountType__exact=UserAccountType).exists() != True:
            # print(Account_type.objects.filter(AccountType__exact= UserAccountType ).exists(),Account_type.objects.filter(AccountType__exact= UserAccountType ).id)
            raise serializers.ValidationError("UserAccountType doesnt exists")
        else:
            args['UserAccountType_id'] = Account_type.objects.get(AccountType__exact=UserAccountType).id
            args.pop('UserAccountType')

        # otp_dict = generate_otp()  # generates Otp which would be stored on DB
        # args.update(otp_dict)

        return super().validate(args)

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)

        """
        If the new user is reffered by existing user then credit 
        1000 points to the existing users wallet 
        """
        try:
            refered_by = validated_data.get('refered_by')
            print('referral_code', refered_by)
            referrer = User.objects.get(referal_code=refered_by)

            if User.objects.filter(referal_code=refered_by).exists():
                referrer = User.objects.get(referal_code=refered_by)

                if referrer:
                    try:
                        Reward.objects.update_or_create(user=User.objects.get(email=str(referrer.email)))
                        reward = Reward.objects.get(user=User.objects.get(email=str(referrer.email)))
                        print('reward', reward)
                        reward.points += 1000
                        reward.save()
                    except ObjectDoesNotExist:
                        print('No reward.')
                        pass
        except:
            pass

        return user


class Address_serializer(serializers.ModelSerializer):
    Address_Number = serializers.CharField(required=False, allow_blank=True)
    Address_Street1 = serializers.CharField(required=False, allow_blank=True)
    Address_Street2 = serializers.CharField(required=False, allow_blank=True)
    Address_City = serializers.CharField(required=False, allow_blank=True)
    Address_Province = serializers.CharField(required=False, allow_blank=True)
    Address_Postal = serializers.CharField(required=False, allow_blank=True)
    Address_Country = serializers.CharField(required=False, allow_blank=True)
    Address_Lat = serializers.CharField(required=False, allow_blank=True)
    Address_Long = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Address
        fields = (
            'Address_id',
            'Address_Number',
            'Address_Street1',
            'Address_Street2',
            'Address_City',
            'Address_Province',
            'Address_Postal',
            'Address_Country',
            'Address_Lat',
            'Address_Long',
        )

    def validate(self, args):
        Address_Number = args.get('Address_Number', None)
        Address_Street1 = args.get('Address_Street1', None)
        # Address_Street2 = args.get('Address_Street2', None)
        Address_City = args.get('Address_City', None)
        Address_Province = args.get('Address_Province', None)
        Address_Postal = args.get('Address_Postal', None)
        Address_Country = args.get("Address_Country", None)

        if Address_Number.strip() == '' or Address_Number == None:
            raise serializers.ValidationError(" please Enter Address Number ")

        if Address_Street1.strip() == '' or Address_Street1 == None:
            raise serializers.ValidationError(" please Enter Address Street 1 ")

        # if Address_Street2.strip() == '' or Address_Street2 == None:
        #     raise serializers.ValidationError(" please Enter Address Street 2 ")

        if Address_City.strip() == '' or Address_City == None:
            raise serializers.ValidationError(" please Enter Address City ")

        if Address_Province.strip() == '' or Address_Province == None:
            raise serializers.ValidationError(" please Enter Address Province ")

        if Address_Country.strip() == '' or Address_Country == None:
            raise serializers.ValidationError(" please Enter Address Country")

        if Address_Postal.strip() == '' or Address_Postal == None:
            raise serializers.ValidationError(" please Enter Address Postal")

        return super().validate(args)

    def create(self, validated_data):

        address = Address.objects.create(**validated_data)

        return address

    def update(self, instance, validated_data):
        # https://stackoverflow.com/questions/53779723/django-rest-framework-update-with-kwargs-from-validated-data

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class GPS_Address_serializer(serializers.ModelSerializer):
    Address_Number = serializers.CharField(required=False, allow_blank=True)
    Address_Street1 = serializers.CharField(required=False, allow_blank=True)
    Address_Street2 = serializers.CharField(required=False, allow_blank=True)
    Address_City = serializers.CharField(required=False, allow_blank=True)
    Address_Province = serializers.CharField(required=False, allow_blank=True)
    Address_Postal = serializers.CharField(required=False, allow_blank=True)
    Address_Country = serializers.CharField(required=False, allow_blank=True)
    Address_Lat = serializers.CharField(required=False, allow_blank=True)
    Address_Long = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = GPSAddress
        fields = (
            'Address_id',
            'Address_Number',
            'Address_Street1',
            'Address_Street2',
            'Address_City',
            'Address_Province',
            'Address_Postal',
            'Address_Country',
            'Address_Lat',
            'Address_Long',
            'isGPS',
        )


from django.contrib.auth.hashers import make_password, check_password


class TokenObtainSerializerCustom(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #    raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')
    #    return RefreshToken.for_user(user)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # print(user)
        # Add custom claims
        token['email'] = user.email
        token['account_id'] = str(user.account_id)
        return token

    def validate(self, attrs):
        # data = super().validate(attrs)
        # print(data)
        # print("this is attr", attrs)
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        print("login Credentials", authenticate_kwargs)
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        if not User.objects.filter(email=authenticate_kwargs['email']):
            return {
                "success": False,
                "status": "403",
                "message": "Login Failed, Please Enter Valid Email"
            }

        user_obj = User.objects.get(email=authenticate_kwargs['email'])
        print(user_obj.password)
        password_ = check_password(authenticate_kwargs['password'], user_obj.password)
        if password_ is False:
            return {
                "success": False,
                "status": "403",
                "message": "Login Failed. Please Enter Valid Password"
            }
        if user_obj.is_active is False:
            return {
                "success": False,
                "status": "403",
                "message": "Login Failed. Your Account is Inactive."
            }
        if user_obj.otp_status is False:
            return {
                "success": False,
                "status": "403",
                "message": "Your account is not verify. Please enter otp to verify your account"
            }
        self.user = authenticate(**authenticate_kwargs)

        print(self.user.email, "45555555555555555555555555555")

        # if not api_settings.USER_AUTHENTICATION_RULE(self.user):
        if not self.user:
            # raise serializers.ValidationError("Unknown/Unauthorized User")
            return {
                "success": False,
                "status": "200",
                "message": "Login Failed, Unauthorized User"
            }

        refresh = self.get_token(self.user)
        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data["success"] = True
        user = User.objects.get(account_id=self.user.account_id)
        print(user, "4444444444444444444444444444444444444444444")
        data["user"] = UserSerializer(user).data
        data["message"] = "Successfully Login"

        return data


class TokenRefreshSerializerCustom(TokenRefreshSerializer):
    # https: // github.com / jazzband / djangorestframework - simplejwt / blob / master / rest_framework_simplejwt / serializers.py
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        access_token = refresh.access_token
        # https://stackoverflow.com/questions/61564278/set-expiration-time-to-sample-django-jwt-token
        access_token.set_exp(lifetime=timedelta(days=10))  # first 5 updated 24 hrs expiry

        # data = {"access": str(refresh.access_token)}
        data = {"access": str(access_token)}
        data['success'] = True
        print("Login Credentials", data)
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    print('refresh.blacklist()', refresh.blacklist())
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    # pass
                    data = {"success": False}
                    return data

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data


class UpdatePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    new_password = serializers.CharField(required=False,
                                         allow_blank=True)  # set required False just to provide/send custom validation to front end
    confirm_password = serializers.CharField(required=False,
                                             allow_blank=True)  # set required False just to provide/send custom validation to front end

    def validate(self, args):
        new_pword = args.get('new_password', None)
        confirm_pword = args.get('confirm_password', None)

        if new_pword == None or str(new_pword).replace(" ", "") == '':
            # raise serializers.ValidationError({'Password':("Password Mismatch on NEW and confirm Fields")})
            raise serializers.ValidationError("please provide new password")

        if confirm_pword == None or str(confirm_pword).replace(" ", "") == '':
            # raise serializers.ValidationError({'Password':("Password Mismatch on NEW and confirm Fields")})
            raise serializers.ValidationError("please confirm new password")

        if str(new_pword) != str(confirm_pword):
            # raise serializers.ValidationError({'Password':("Password Mismatch on NEW and confirm Fields")})
            raise serializers.ValidationError("Password Mismatch on new and confirm password")

        return super().validate(args)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    UserAccountType = serializers.CharField(source='UserAccountType.AccountType')

    class Meta:
        model = User
        fields = ('account_id',
                  'Name_First',
                  'Name_Last',
                  'email',
                  'QrCode_Account',
                  'profile_image',
                  'phone_number',
                  'full_name',
                  'Address_id',
                  'user_lat',
                  'user_long',
                  'uuid',
                  'my_address',
                  'is_verified',
                  'reward_points',
                  'UserAccountType',
                  'hst_number',
                  'CreationDate',
                  'is_bank_account',
                  )

    Address_id = serializers.SerializerMethodField('get_address_id')
    my_address = serializers.SerializerMethodField('get_my_address')

    def get_address_id(self, obj):

        # https://stackoverflow.com/questions/49414976/django-rest-framework-serializer-with-reverse-relation

        print(obj, type(obj))
        return Address.objects.get(QrCode_Account=obj.account_id).Address_id

    def get_my_address(self, obj):

        # https://stackoverflow.com/questions/49414976/django-rest-framework-serializer-with-reverse-relation

        print(obj, type(obj))

        my_address = Address.objects.get(QrCode_Account=obj.account_id)

        # return Address.objects.get(QrCode_Account=obj.account_id).Address_id

        return my_address.Address_Number + ', ' + my_address.Address_Street1 + ', ' + my_address.Address_Street2 + ', ' + my_address.Address_City + ', ' + my_address.Address_Province + ', ' + my_address.Address_Postal + ', ' + my_address.Address_Country

    def validate(self, args):

        if len(args) == 0:
            raise serializers.ValidationError("please enter the below fields to update")

        full_name = args.get('full_name', None)
        phone_number = args.get('phone_number', None)

        if full_name is not None:
            name_list = [each_name for each_name in full_name.split(' ') if each_name != '']

            print("name validation", name_list)

            if len(name_list) > 1:
                args['Name_First'] = name_list[0]
                args['Name_Last'] = name_list[1]
            elif len(name_list) == 1:
                args['Name_First'] = name_list[0]
            else:
                pass

            args.pop('full_name')

        if phone_number is not None:
            if User.objects.filter(phone_number=phone_number).exists():
                raise serializers.ValidationError("Phone Number already exists")

        # for each_attr in args.keys():
        #    if each_attr not in ('account_id', 'Name_First','Name_Last','email','profile_image','phone_number'):
        #        args.pop(each_attr)

        user_editable_params_filters = ('Name_First', 'Name_Last', 'email', 'profile_image', 'phone_number')

        filterByKey = lambda keys, data: {x: data[x] for x in keys if x in data.keys()}
        args = filterByKey(user_editable_params_filters, args)
        print(args)

        return super().validate(args)

    def update(self, instance, validated_data):
        # https://stackoverflow.com/questions/53779723/django-rest-framework-update-with-kwargs-from-validated-data

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'fullname', 'Address_id', 'QrCode_Account', 'Address_Number', 'Address_Lat', 'Address_Long',
            'Address_Street1', 'Address_Street2', 'Address_City',
            'Address_Province', 'Address_Postal', 'Address_Country', "my_address")

    fullname = serializers.SerializerMethodField('get_user_name')
    my_address = serializers.SerializerMethodField('get_address')

    def get_user_name(self, obj):
        return obj.QrCode_Account.Name_First + ' ' + obj.QrCode_Account.Name_Last

    def get_address(self, obj):
        return obj.Address_Number + ', ' + obj.Address_Street1 + ', ' + obj.Address_Street2 + ', ' + obj.Address_City + ', ' + obj.Address_Province + ', ' + obj.Address_Postal + ', ' + obj.Address_Country


class UserDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceToken
        fields = '__all__'


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


class UserUnavailabilitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserUnavailability
        fields = ['id', 'unavailableDate', 'user']


class UserWeekAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWeekAvailability
        fields = '__all__'


from rest_framework import serializers


class TCsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NDR_Documents
        fields = '__all__'


class PPcSerializer(serializers.ModelSerializer):
    class Meta:
        model = NDR_PrivacyPolicy
        fields = '__all__'


from accounts.models import Notification


class NotificationAddShow(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ['created']


class AbusiveContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAbusiveContent
        fields = '__all__'
