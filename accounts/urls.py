# from .views import RegisterAPI , MyTokenObtainPairView, HelloView, ForgetPasswordView, ChangePasswordView, BlacklistRefreshView
from login_portal import views
from .views import *
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/register-otp-verification/', VerifyOTPView.as_view(), name='VerifyOTPView'),
    path('api/resend-otp/', ResendOTPView.as_view(), name='ResendOTPView'),
    # path('api/login/', LoginView.as_view(), name='login'),
    path('api/login/', MyTokenObtainPairView.as_view(), name='login'),
    # path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/mock/', HelloView.as_view(), name='mock'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/refresh/', MyRefreshTokenView.as_view(), name='token_refresh'),
    path('api/forgot_password/', ForgetPasswordView.as_view(), name='forgot_password'),
    path('api/verify-otp/', ForgotPasswordOTPVerification.as_view(), name='ForgotPasswordOTPVerification'),
    path('api/update_password/', ChangePasswordView.as_view(), name='update_password'),
    path('api/list_drop_down/', list_drop_down.as_view(), name='list_dropdown'),
    path('api/logout/', BlacklistRefreshView.as_view(), name="logout"),
    path('api/Myaccount/', ProfileView.as_view(), name="View_My_Account"),
    path('api/MyAddress/', AddressView.as_view(), name="View_My_Address"),
    path('api/GPSAddress/', AddGPSAddressView.as_view(), name="AddGPSAddressView"),
    path('api/upload_profile_image/', ProfileImageUpdate.as_view(), name="UploadProfileImage"),
    path('api/user_device_token/', UserDeviceTokenView.as_view(), name="UserDeviceTokenView"),
    path('api/stripe_secret_key/', StripeSecretKey.as_view(), name="StripeSecretKey"),
    path('api/notifications/', NotificationsView.as_view(), name="NotificationsView"),
    path('api/firebase_test/', FirebaseTest.as_view(), name="FirebaseTest"),
    path('api/refer-and-earn/', Reffered.as_view(), name="Reffered"),
    path('api/user-unavailability/', UserUnavailabilityView.as_view(), name="UserUnavailabilityView"),
    path('api/user-week-availability/', UserWeekAvailabilityView.as_view(), name="UserWeekAvailabilityView"),
    path('api/app-feedback/', AppFeedbackView.as_view(), name="AppFeedbackView"),
    path('api/customer-support/', CustomerSupportView.as_view(), name="CustomerSupportView"),
    path('api/preferences-notifications/', PreferencesNotificationsView.as_view(), name="PreferencesNotificationsView"),
    path('tcs_list/', tcs_list, name='tcs_list'),
    path('pps_list/', pps_list, name='pps_list'),
    path('api/NotificationsEdit/', NotificationsEdit.as_view(), name='NotificationsEdit'),
    path('api/AbusiveContentView/', AbusiveContentView.as_view(), name='AbusiveContentView'),

]
