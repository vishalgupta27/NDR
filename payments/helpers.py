from accounts.models import *
from next_door_backend.settings import FCM_DJANGO_SETTINGS
from pyfcm import FCMNotification

def send_push_notification(user_id,fcm_token,title, message_body):
    try:
        push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
        Notifications.objects.create(user_id = user_id, title=title, body=message_body, screen_name = "Transaction")
        response = push_service.notify_single_device(
            registration_id=fcm_token,
            message_title=title, 
            message_body=message_body
            )
        print(response,"this is response")
        return response
    except Exception as e:
        print(e)
