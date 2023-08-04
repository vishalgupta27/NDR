import re

from django.contrib import messages
from rest_framework.parsers import FileUploadParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.exceptions import AuthenticationFailed
from next_door_backend.settings import FCM_DJANGO_SETTINGS
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponsePermanentRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import generics, permissions
from django.urls import reverse_lazy, reverse
from rest_framework.response import Response
from products.models import LenderReviews
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from django.db.models import Count, Avg
from rest_framework import serializers
from next_door_backend import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import Context
from django.shortcuts import render
from rest_framework import status
from pyfcm import FCMNotification
from .utils import generate_qr
from urllib import request
from .serializers import *
from .models import User
import jwt, datetime
import pandas as pd
import pyrebase
import requests
import stripe
import http
import json

stripe.api_key = settings.STRIPE_SECRET_KEY
config = {
    "apiKey": "AIzaSyBmP6yuD1-bvUC0QeuJN3KwGIs-nl5CNgM",
    "authDomain": "Use Your authDomain Here",
    "databaseURL": "https://next-door-renal-default-rtdb.firebaseio.com/",
    "projectId": "next-door-renal",
    "storageBucket": "gs://next-door-renal.appspot.com",
    "appId": "1:409974553054:android:30e717b0d25518e7a2454f",
    "messagingSenderId": "409974553054",
}
# config={
#     "apiKey": "AIzaSyADRWQykgc3lizvK538Hxti7h3PGrBQsH8",
#     "authDomain": "Use Your authDomain Here",
#     "databaseURL": "https://next-door-renal-default-rtdb.firebaseio.com/",
#     "projectId": "next-door-renal",
#     "storageBucket": "next-door-renal.appspot.com",
#     "appId": "1:409974553054:android:dec7036c4ca72394a2454f"
# }
# Initialising database,auth and firebase for further use
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


class FirebaseTest(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password, "This is email password")
        name = database.get().val()
        print(name)
        try:
            # creating a user with the given email and password
            user = authe.create_user_with_email_and_password(email, password)
            print("this is user")
            uid = user['localId']
            return Response({
                "status": 200,
                "uuid": uid
            })
        except Exception as e:
            return Response({
                "status": 403,
                "message": str(e)
            })


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [settings.APP_SCHEME, 'http', 'https']


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = Ndr_RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        email = request.data['email']
        user_device_id = request.data.get('user_device_id')
        request_dict = request.data.dict()
        user_details = {key: request_dict[key] for key in request_dict.keys() & Ndr_RegisterSerializer.Meta.fields}
        user_serializer = self.get_serializer(data=user_details)
        if (user_serializer.is_valid()):

            self.serializer_class = Address_serializer
            address_details = {key: request_dict[key] for key in request_dict.keys()
                               & Address_serializer.Meta.fields}

            address_serializer = self.get_serializer(data=address_details)
            if (address_serializer.is_valid()):
                print(Ndr_RegisterSerializer.Meta.fields, type(Ndr_RegisterSerializer.Meta.fields))
                response = Response()
                user = user_serializer.save()
                otp = random.randint(100000, 999999)
                firebase_user = authe.create_user_with_email_and_password(request.data['email'],
                                                                          request.data['password'])
                print("this is user", firebase_user)
                uid = firebase_user['localId']

                user.uuid = uid
                user.otp = otp
                user.save()
                user_address = address_serializer.save()
                user_address.QrCode_Account_id = user.account_id
                user_address.save()

                # Send Push Notification and Mail
                title = "Regarding Limited Access"
                message_body = f"Thanks for Signing up and choosing Next Door Rental! For the safety of our community, your account has limited access until our team can verify who you are. You can still browse, and sign up all your products, they just won’t be listed until verified. For more information, please see our How it Works Section. Enter otp {otp} to verify your account"
                push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                Notifications.objects.create(user_id=user.account_id, title=title, body=message_body,
                                             screen_name="howItWorks")
                res = push_service.notify_single_device(
                    registration_id=user_device_id,
                    message_title=title,
                    message_body=message_body
                )
                # Send Mail
                subject = "Regarding Limited Access"
                message = f"Thanks for Signing up and choosing Next Door Rental! For the safety of our community, your account has limited access until our team can verify who you are. You can still browse, and sign up all your products, they just won’t be listed until verified. For more information, please see our How it Works Section. Enter otp {otp} to verify your account"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail(subject, message, email_from, recipient_list)
                return Response({
                    "success": True,
                    "status": "200",
                    "message": "Successfully Registered, We have sent an OTP to your registered mail id, please enter OTP to verify your account",
                    "response": res
                })

            else:
                error_field = [i for i in address_serializer.errors.keys()][0]
                message = address_serializer.errors[error_field][0].title()

                return Response({
                    "status": 200,
                    "success": False,
                    "message": message})

        error_field = [i for i in user_serializer.errors.keys()][0]

        message = user_serializer.errors[error_field][0].title()

        return Response({
            "status": 200,
            "success": False,
            "message": message})


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        user = User.objects.filter(email=email, otp=otp).first()
        if user is None:
            return Response({
                "status": 400,
                "success": False,
                "message": "Please enter valid otp"
            })
        userObj = User.objects.get(email=email)
        userObj.otp_status = True
        userObj.save()
        return Response({
            "status": 200,
            "success": True,
            "message": "OTP Verified successfully. Now you can logged in"
        })


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        otp = random.randint(100000, 999999)
        if user is None:
            return Response({
                "status": 400,
                "success": False,
                "message": "Account does not exist. Please enter valid email"
            })
        userObj = User.objects.get(email=email)
        userObj.otp = otp
        userObj.save()
        subject = "Resend OTP"
        message = f"Please enter OTP {otp} to verify your account"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)
        return Response({
            "status": 200,
            "success": True,
            "message": "OTP has been sent. Please check your email"
        })


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainSerializerCustom


class MyRefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializerCustom


class HelloView(APIView):

    # permission_classes = [IsAuthenticated,]
    # print(permission_classes)

    def get(self, request):
        try:
            permission_classes = [IsAuthenticated, ]
            print(permission_classes)
            # token = request.COOKIES.get('jwt')

            user = request.user.username

            print(user, request.user)

            return Response({'message': 'Hello ' + user})

        except Exception as e:
            return Response({'message': 'Hello ' + e})


class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]

    # authentication_classes = ()

    def post(self, request, *args, **kwargs):
        print(self.kwargs)
        # print(request.query_params.get('user'))
        # user = User.objects.get(email=self.kwargs['email'])

        email = request.data.get('email', None)

        if str(email).replace(" ", "") == '' or email is None:
            message = 'please enter a valid Phone Number'
            return Response({
                "status": 200,
                "success": False,
                "message": message})

        user = User.objects.filter(email=email).exists()
        if not user:
            return Response({'success': False,
                             'message': "Please enter valid email to reset password",
                             'status': status.HTTP_200_OK})
        user = User.objects.filter(email=email).first()

        otp = random.randint(10000, 99999)
        user.otp = otp
        user.save()
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain

        # relativeLink = reverse('email-verify')

        absurl = 'http://' + current_site + '/api/update_password/' + "?token=" + str(token)
        # Send Mail
        mydict = {
            'otp': otp,
        }
        html_template = 'reset-password-mail.html'
        html_message = render_to_string(html_template, context=mydict)
        subject = 'forgot password otp'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        message = EmailMessage(subject, html_message, email_from, recipient_list)
        message.content_subtype = 'html'
        try:
            message.send()
        except:
            return Response({
                "status": 403,
                "success": False,
                "message": "Unable to send mail."
            })

        response = Response()

        response.data = {
            'success': True,
            'reset_url': absurl,
            'message': "otp send successfully",
            'status': status.HTTP_200_OK}
        return response


class ForgotPasswordOTPVerification(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data['otp']
        user = User.objects.filter(otp=otp).first()
        if user is None:
            return Response({
                "status": 400,
                "success": False,
                "message": "OTP did not match!"
            })
        return Response({
            "status": 200,
            "success": True,
            "message": "OTP Verified successfully"
        })


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UpdatePasswordSerializer

    def post(self, request, *args, **kwargs):

        # token = self.kwargs.get('jwt', None)

        token = self.request.query_params.get('token', None)

        if not token:
            return Response({
                "status": 200,
                "success": False,
                "message": 'User not found'})

        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
        except:
            return Response({
                "status": 200,
                "success": False,
                "message": 'User not found'})

        serializer = self.get_serializer(data=request.data)

        # queryset = User.objects.filter(id=decoded['id'])
        user = User.objects.filter(account_id=decoded['user_id']).first()

        # if queryset is None:
        if user is None:
            return Response({
                "status": 200,
                "success": False,
                "message": 'user Does not Exist'})

        # if (serializer.is_valid(raise_exception=True)):
        if (serializer.is_valid()):
            password = request.data.get('confirm_password')

            if user.check_password(password):
                response = Response()
                response.set_cookie(key='jwt', value=None, httponly=True)
                response.data = {
                    "status": 200,
                    "success": False,
                    "message": "New Password cannot be the same as old password"
                }
                return response

            update_pwd = User.objects.get(account_id=decoded['user_id'])
            update_pwd.set_password(serializer.data.get("confirm_password"))
            update_pwd.save()

            return Response(
                {'success': True,
                 'message': 'Password updated'
                 },
                status=status.HTTP_200_OK)

        else:

            # print('--------------------------')
            # print(serializer.errors.keys())
            error_field = [i for i in serializer.errors.keys()][0]
            # print('--------------------------')
            # print(error_field)
            # print(serializer.errors)
            # message = serializer.errors['non_field_errors'][0].title()

            message = serializer.errors[error_field][0].title()

            return Response({
                "status": 200,
                "success": False,
                "message": message})


class BlacklistRefreshView(APIView):
    def post(self, request):

        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            # print('auth-token',request.user)
            response = Response()
            response.data = {
                "status": 200,
                "success": True,
                "message": "Successfully Logged out"
            }
            return response

        except Exception as e:
            response = Response()
            response.data = {
                "status": 200,
                "success": False,
                "message": str(e)
            }
            return response


class list_drop_down(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        try:

            country = self.request.query_params.get('country', None)
            city = self.request.query_params.get('city', None)
            postal_code = self.request.query_params.get('postal_code', None)

            if country is None:
                # raise Exception ('please select country')
                # json_file_path = '/home/augursdemo/NDR/next_door_backend_updated/arranged/next_door_backend/accounts/full_dataset_csv.csv'
                json_file_path = '/home/ubuntu/Next_Door_Rental/accounts/full_dataset_csv.csv'
                df = pd.read_csv(json_file_path)
                print(df[['country', 'state', 'city', 'zipCode']])

                countries = [i for i in df[['country', 'state', 'city', 'zipCode']]['country'].unique()]
                response = Response()
                response.data = {
                    "status": 200,
                    "success": True,
                    "country": countries
                }
                return response

            else:

                # json_file_path = '/home/augursdemo/NDR/next_door_backend_updated/arranged/next_door_backend/accounts/full_dataset_csv.csv'
                json_file_path = '/home/ubuntu/Next_Door_Rental/accounts/full_dataset_csv.csv'
                df = pd.read_csv(json_file_path)
                print(df[['country', 'state', 'city', 'zipCode']])

                countries = [i for i in df[['country', 'state', 'city', 'zipCode']]['country'].unique()]

                # states = df[df['country'] == 'Canada']['state'].unique()

                # cities = df[(df['country'] == 'Canada') & (df['state'] == 'British Columbia')]['city'].unique()

                # zip = df[(df['country'] == 'Canada') & (df['state'] == 'British Columbia') & (df['city'] == 'Boswell')]['zipCode'].unique()

                cities = df[(df['country'] == country)]['city'].unique()
                # cities = df[(df['country'].str.contains(country, case = False))]['city'].unique()

                if city:
                    # zip = df[(df['country'] == 'Canada') & (df['state'] == 'British Columbia') & (df['city'] == 'Boswell')]['zipCode'].unique()
                    zip = df[(df['country'] == country) & (df['city'] == city)]['zipCode'].unique()
                    # zip = df[(df['country'].str.contains(country ,case = False) == country) & (df['city'].str.contains(city, case = False) )]['zipCode'].unique()

                    response = Response()
                    response.data = {
                        "status": 200,
                        "success": True,
                        "country": countries,
                        "cities": cities,
                        "zip": zip
                    }
                    return response

                response = Response()
                response.data = {
                    "status": 200,
                    "success": True,
                    "country": countries,
                    "cities": cities
                }
                return response




        except Exception as e:
            response = Response()
            response.data = {
                "status": 200,
                "success": False,
                "message": str(e)
            }
            return response


# class ProfileView(APIView):
#
#    permission_classes = [IsAuthenticated, ]
#    print(permission_classes)
#    serializer_class = UserSerializer
#
#    def get(self, request, *args, **kwargs):
#        print(self.kwargs)
#
#        user = User.objects.get(account_id=request.user.account_id)
#
#        print(UserSerializer(user).data)
#
#        return Response(
#            {'user':UserSerializer(user).data,
#             'status':200,
#             'success':True})
#
#    def put(self, request, *args, **kwargs):
#        serializer = self.serializer_class(request.user, data=request.data, partial=True)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated, ]
    print(permission_classes)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            print(self.kwargs)
            user = User.objects.get(account_id=request.user.account_id)
            count = Notifications.objects.filter(status=False, user_id=request.user.account_id).count()
            lender_rating = LenderReviews.objects.filter(lender_id=request.user.account_id)
            lender_rate_avg = lender_rating.aggregate(lender_ratings=Avg('rating'))
            lender_review_count = lender_rating.aggregate(count=Count('user'))
            print(UserSerializer(user).data)

            return Response({
                'user': UserSerializer(user).data,
                "notification_count": count,
                "lender_ratings": lender_rate_avg,
                "lender_review_count": lender_review_count,
                'status': 200,
                'success': True
            })
        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "messege": str(e)})

    def put(self, request, *args, **kwargs):
        try:

            phone_number = request.data.get('phone_number', None)
            if phone_number is not None:
                if str(phone_number) == str(request.user.phone_number):
                    request.data.pop('phone_number')

            serializer = self.serializer_class(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "messege": str(e)})


class AddressView(APIView):
    permission_classes = [IsAuthenticated, ]
    print(permission_classes)
    serializer_class = Address_serializer

    def get(self, request, *args, **kwargs):
        print(self.kwargs)

        # address_obj = Address.objects.get(QrCode_Account_id = request.user.account_id)

        address_obj = Address.objects.filter(QrCode_Account_id=request.user.account_id)

        print(address_obj)

        address_list = [Address_serializer(each_set).data for each_set in address_obj]

        return Response(
            # {'address':Address_serializer(address_obj).data,
            {'address': address_list,
             'status': 200,
             'success': True})

    def put(self, request, *args, **kwargs):
        try:
            # address_obj = Address.objects.get(QrCode_Account_id = request.user.account_id)
            print(request.data['user_long'])
            Address_id = request.query_params.get('Address_id', None)
            if Address_id == None:
                raise Exception("please select address to Edit")

            address_obj = Address.objects.get(Address_id=Address_id)
            serializer = self.serializer_class(address_obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"address": serializer.data, "status": status.HTTP_200_OK, "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "messege": str(e)})

    def delete(self, request):
        try:
            Address_id = request.query_params.get('Address_id', None)
            if Address_id == None:
                raise Exception("please select address to delete")
            Address.objects.get(Address_id=Address_id).delete()
            return Response({
                "message": "Address Deleted",
                "status": 200,
                "success": True})
        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "messege": str(e)})

    def post(self, request):
        try:
            address_serializer = Address_serializer(data=request.data)

            if address_serializer.is_valid():
                user_address = address_serializer.save()

                user_address.QrCode_Account_id = request.user.account_id

                user_address.save()

                return Response({'status': 200,
                                 'messgae': 'New Address updated',
                                 'success': True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "messege": str(e)
            })


class AddGPSAddressView(APIView):
    def post(self, request):
        Address_Number = request.data.get('Address_Number')
        Address_Street1 = request.data.get('Address_Street1')
        Address_Street2 = request.data.get('Address_Street2')
        Address_Lat = request.data.get('Address_Lat')
        Address_Long = request.data.get('Address_Long')
        Address_City = request.data.get('Address_City')
        Address_Province = request.data.get('Address_Province')
        Address_Postal = request.data.get('Address_Postal')
        Address_Country = request.data.get('Address_Country')
        gpsAddress = GPSAddress.objects.filter(QrCode_Account=request.user).first()
        if gpsAddress is None:
            GPSAddress.objects.create(
                QrCode_Account_id=request.user.account_id,
                Address_Number=Address_Number,
                Address_Street1=Address_Street1,
                Address_Street2=Address_Street2,
                Address_Lat=Address_Lat,
                Address_Long=Address_Long,
                Address_City=Address_City,
                Address_Province=Address_Province,
                Address_Postal=Address_Postal,
                Address_Country=Address_Country,
            )
            return Response({
                "status": 200,
                "success": True,
                "message": "GPS Address Saved Successfully"
            })
        gpsAddressObject = GPSAddress.objects.get(QrCode_Account=request.user)
        gpsAddressObject.Address_Number = Address_Number
        gpsAddressObject.Address_Street1 = Address_Street1
        gpsAddressObject.Address_Street2 = Address_Street2
        gpsAddressObject.Address_Lat = Address_Lat
        gpsAddressObject.Address_Long = Address_Long
        gpsAddressObject.Address_City = Address_City
        gpsAddressObject.Address_Province = Address_Province
        gpsAddressObject.Address_Postal = Address_Postal
        gpsAddressObject.Address_Country = Address_Country
        gpsAddressObject.save()
        return Response({
            "status": 200,
            "success": True,
            "message": "GPS Address Saved Successfully"
        })

    def get(self, request):
        myAddress = GPSAddress.objects.filter(QrCode_Account=request.user)
        serialize = GPS_Address_serializer(myAddress, many=True)
        return Response({
            "status": 200,
            "success": True,
            "myGPSAddress": serialize.data
        })


class ProfileImageUpdate(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            account_id = request.user.account_id
            if account_id == None:
                raise Exception("please select address to Edit")

            user_obj = User.objects.get(account_id=account_id)
            serializer = self.serializer_class(user_obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "user": serializer.data,
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Profile Image Updated Successfully!!"
            })

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "messege": str(e)})


class UserDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = UserDeviceTokenSerializer(data=request.data)
            user_obj = UserDeviceToken.objects.filter(user_id=request.user.account_id).first()
            if user_obj is None:
                if serializer.is_valid():
                    user_device_obj = serializer.save()
                    user_device_obj.user_id = request.user.account_id
                    user_device_obj.save()
                    return Response({
                        "status": 200,
                        "success": True,
                        "message": "Your Device ID Sent Successfully!"
                    })

                return Response({
                    "status": 403,
                    "success": False,
                    "message": "Data is not Valid"
                })
            else:
                device_obj = UserDeviceToken.objects.get(user_id=request.user.account_id)
                device_obj.device_id = request.data['device_id']
                device_obj.save()
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Device ID Updated!"
                })

        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


class StripeSecretKey(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            STRIPE_SECRET_KEY = {
                'publishable_key': settings.TRIPE_PUBLISHABLE_KEY,
                'secret_key': settings.STRIPE_SECRET_KEY
            }
            return Response({
                'stripe_key': STRIPE_SECRET_KEY,
                'success': True,
                'status': 200,
                'message': "Stripe Key"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


class NotificationsView(APIView):
    def get(self, request):
        try:
            notifications = Notifications.objects.filter(user=request.user).order_by('-date_time')
            NotiS = NotificationsSerializer(notifications, many=True)
            return Response({
                "notifications": NotiS.data,
                "status": 200,
                "success": True
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def put(self, request):
        try:
            noti_id = request.query_params.get('notification_id')
            noti_obj = Notifications.objects.get(id=noti_id)
            noti_obj.status = True
            noti_obj.save()
            return Response({
                "status": 200,
                "success": True,
                "message": "Successfully Read!"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def delete(self, request):
        try:
            noti_id = request.query_params.get('notification_id')
            noti_obj = Notifications.objects.get(id=noti_id)
            noti_obj.delete()
            return Response({
                "status": 200,
                "success": True,
                "message": "Notifications Deleted Successfully"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


class Reffered(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            referal_code = request.user.referal_code
            current_user = request.user.Name_First
            # Send Mail
            # subject = f"Hi {first_name}"
            # message = f"Hi {first_name} Your friend Ravish has referred us. Try our all exclusive mobile platform to list your belongings for renting and earning.Click the button below to download the app and start your journey Now! https://nextdoorrental.ca/{referal_code}"
            # email_from = settings.EMAIL_HOST_USER
            # recipient_list = [email, ]
            # send_mail(subject, message, email_from, recipient_list )

            mydict = {
                'email': email,
                'first_name': first_name,
                'referal_code': referal_code,
                'current_user': current_user,
            }
            html_template = 'refer-and-earn.html'
            html_message = render_to_string(html_template, context=mydict)
            subject = 'Experience Renting and Earning Through NDR'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            try:
                message.send()
            except:
                return Response({
                    "status": 403,
                    "success": False,
                    "message": "Unable to send mail."
                })
            return Response({
                "status": 200,
                "success": True,
                "message": "Send Successfully"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


class UserUnavailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        unavailableDate = dict((request.data))['unavailableDate']
        user_id = request.user.account_id
        for date in unavailableDate:
            UserUnavailability.objects.create(user_id=user_id, unavailableDate=date)
        return Response({
            "status": 200,
            "success": True,
            "message": "User unavailability saved successfully"
        })

    def get(self, request):
        user_obj = UserUnavailability.objects.filter(user=request.user)
        serialize = UserUnavailabilitySerializer(user_obj, many=True).data
        return Response({
            "status": 200,
            "success": True,
            "user_unavailability_date": serialize
        })

    def delete(self, request):
        date = dict((request.data))['date']
        for x in date:
            checkData = UserUnavailability.objects.filter(unavailableDate=x, user=request.user).first()
            if checkData is None:
                return Response({
                    "status": 400,
                    "success": False,
                    "message": "matching query does not exist"
                })
            date = UserUnavailability.objects.get(unavailableDate=x, user=request.user)
            date.delete()
        return Response({
            "status": 200,
            "success": True,
            "message": "Removed successfully"
        })


class UserWeekAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # weekAvailability = dict(request.data.get('weekAvailability'))
            weekAvailability = dict((request.data))['weekAvailability']
            user = UserWeekAvailability.objects.filter(user=request.user).first()
            if user is None:
                UserWeekAvailability.objects.create(user_id=request.user.account_id, weekAvailability=weekAvailability)
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Your availability saved successfully"
                })
            userObj = UserWeekAvailability.objects.get(user=request.user)
            userObj.weekAvailability = weekAvailability
            userObj.save()
            return Response({
                "status": 200,
                "success": True,
                "message": "Your availability saved successfully"
            })
        except Exception as e:
            return Response({
                "status": 400,
                "success": False,
                "message": str(e)
            })

    def get(self, request):
        try:
            data = UserWeekAvailability.objects.filter(user=request.user)
            serialize = UserWeekAvailabilitySerializer(data, many=True).data
            print(serialize)
            return Response({
                "status": 200,
                "success": True,
                "user_availability": serialize
            })
        except Exception as e:
            return Response({
                "status": 400,
                "success": False,
                "message": str(e)
            })


class AppFeedbackView(APIView):
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        subject = f"{title}"
        html_content = f"{description}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['support@nextdoorrental.ca', ]
        message = EmailMultiAlternatives(subject, html_content, email_from, recipient_list, cc=[request.user.email])
        # send_mail( subject, message, email_from, recipient_list ,"text/html")
        message.attach_alternative(html_content, "text/html")
        try:
            message.send()
        except:
            return Response({
                "status": 403,
                "success": False,
                "message": "Unable to send mail."
            })
        return Response({
            "status": 200,
            "success": True,
        })


import random


class CustomerSupportView(APIView):
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        ticketNumber = random.randint(10000000, 99999999)
        user = request.user
        CustomerSupport.objects.create(userID=user, title=title, issueText=description, ticketNumber=ticketNumber)
        subject = f"{title}"
        html_content = f"{description}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['support@nextdoorrental.ca', ]
        message = EmailMultiAlternatives(subject, html_content, email_from, recipient_list)
        # send_mail( subject, message, email_from, recipient_list ,"text/html")
        message.attach_alternative(html_content, "text/html")
        try:
            message.send()
        except:
            return Response({
                "status": 403,
                "success": False,
                "message": "Unable to send mail."
            })
        return Response({
            "status": 200,
            "success": True,
            "ticketNumber": ticketNumber,
        })


class PreferencesNotificationsView(APIView):
    def post(self, request):
        user = request.user
        isEmail = request.data.get('isEmail')
        isNotification = request.data.get('isNotification')
        success = Response({
            "status": 200,
            "success": True,
            "message": "Notification Update Successfully!"
        })
        users = PreferencesNotifications.objects.filter(user=user).first()
        if users is None:
            print("User is None")
            if isEmail == 'isOnlyEmailTrue':
                PreferencesNotifications.objects.create(user=user, isEmail=True)
                return success
            if isNotification == 'isOnlyNotificationTrue':
                PreferencesNotifications.objects.create(user=user, isNotifications=True)
                return success
        if isEmail == 'isOnlyEmailFalse':
            obj = PreferencesNotifications.objects.get(user=user)
            obj.isEmail = False
            obj.save()
            return success
        if isEmail == 'isOnlyEmailTrue':
            obj = PreferencesNotifications.objects.get(user=user)
            obj.isEmail = True
            obj.save()
            return success
        if isNotification == 'isOnlyNotificationFalse':
            obj = PreferencesNotifications.objects.get(user=user)
            obj.isNotifications = False
            obj.save()
            return success
        if isNotification == 'isOnlyNotificationTrue':
            obj = PreferencesNotifications.objects.get(user=user)
            obj.isNotifications = True
            obj.save()
            return success

    def get(self, request):
        notificationStatus = PreferencesNotifications.objects.filter(user=request.user)
        list = []
        for x in notificationStatus:
            data = {
                "userName": x.user.Name_First,
                "isEmail": x.isEmail,
                "isNotifications": x.isNotifications
            }
            list.append(data)
        return Response({
            "status": 200,
            "success": True,
            "output": list
        })


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import TCsSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tcs_list(request):
    try:
        tcs_ojs = NDR_Documents.objects.all()
        serializer = TCsSerializer(tcs_ojs, many=True)
        return Response({'status': True, 'message': 'success data', 'data': serializer.data})
    except Exception as e:
        return Response({'status': False, 'message': 'Failed data', 'error': str(e)})


from .serializers import PPcSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pps_list(request):
    try:
        pps_ojs = NDR_PrivacyPolicy.objects.all()
        serializer = PPcSerializer(pps_ojs, many=True)
        return Response({'status': True,
                         'message': 'success data',
                         'data': serializer.data})
    except Exception as e:
        return Response({'status': False,
                         'message': 'Failed data',
                         'error': str(e)})


class NotificationsEdit(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            notif = Notification.objects.all()
            serialize = NotificationAddShow(notif, many=True)
            return Response({
                "status": 200,
                "success": True,
                "data": serialize.data
            })
        except Exception as e:
            return Response({'status': False,
                             'message': 'Failed data',
                             'error': str(e)})


class AbusiveContentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Request data:", request.data)
        if request.user.is_authenticated and request.user.is_admin and request.user.is_staff:
            try:
                # Get the data from the request and create a new ChatAbusiveContent object
                serializer = AbusiveContentSerializer(data=request.data)
                if serializer.is_valid():
                    abusive_content = serializer.save()
                    abusive_content.user = request.user
                    abusive_content.save()
                    return Response({'status': True,
                                     'message': 'Data added successfully',
                                     'data': serializer.data})
                else:
                    return Response({'status': False,
                                     'message': 'Failed to add data',
                                     'errors': serializer.errors})

            except Exception as e:
                return Response({'status': False,
                                 'message': 'Failed to add data',
                                 'error': str(e)})
        else:
            return Response({"status": False, "message": "Unauthorized. Admin access required."}, status=403)
