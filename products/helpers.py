from next_door_backend.settings import FCM_DJANGO_SETTINGS  
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from django.db.models import Count, Avg
from pyfcm import FCMNotification
from django.conf import settings
from accounts.models import *
from products.models import *
import datetime

def send_email(subject, html_content, userEmail):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [userEmail, ]
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
    })

def send_push_notification(title, message_body,fcm_token):
    push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
    res = push_service.notify_single_device(
        registration_id=fcm_token,
        message_title=title, 
        message_body=message_body
        )
    return res

def lender_and_product_avg(Products_id, QrCode_Account_id):
    product_rating = ProductReviews.objects.filter(product_id=Products_id)
    lender_rating = LenderReviews.objects.filter(lender_id=QrCode_Account_id)
    prodAvgRatings = {
        "rating_avg": product_rating.aggregate(product_ratings=Avg('rating')),
        "renter_count":product_rating.aggregate(users_rated_to_the_product=Count('renter_id')),
        "lender_rate_avg": lender_rating.aggregate(lender_ratings=Avg('rating')),
        "rated_renter_count": lender_rating.aggregate(users_rated_to_the_lender=Count('user_id'))
    }
    return prodAvgRatings


from math import radians, sin, cos, sqrt, atan2

def calculate_distance(user_lat, user_lon, product_lat, product_lon):
    
    # Convert coordinates from degrees to radians
    user_lat = radians(user_lat)
    user_lon = radians(user_lon)
    product_lat = radians(product_lat)
    product_lon = radians(product_lon)

    # Radius of the Earth in kilometers
    radius = 6371

    # Calculate the differences between the latitudes and longitudes
    dlat = product_lat - user_lat
    dlon = product_lon - user_lon

    # Apply the Haversine formula
    a = sin(dlat / 2) ** 2 + cos(user_lat) * cos(product_lat) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = radius * c

    return distance
