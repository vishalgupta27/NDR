import json
import os

from django.contrib import messages
# import http
# from django.core.mail import send_mail
# from .utils  import generate_qr
# # Create your views here.
# from rest_framework import generics, permissions
# from rest_framework.response import Response
# from .serializers import UserSerializer, Admin_UserSerializer, TokenObtainSerializerCustom_admin_user, admin_user_watch_user_list, RegisterSerializer, TokenObtainSerializerCustom, UpdatePasswordSerializer, Ndr_RegisterSerializer,TokenRefreshSerializerCustom
from django.contrib.auth.models import User, auth
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from pyfcm import FCMNotification
from rest_framework.decorators import api_view

from accounts.models import Account_type, Address, Notifications, ChatAbusiveContent
from next_door_backend.settings import FCM_DJANGO_SETTINGS
from products.models import *
from .models import *


def coming_soon(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            print(current_user_.PhotoID)
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_count": report_count,
                "report_incident": report_incident,
            }
            return render(request, 'coming-soon.html', data)

        return render(request, "login.html")


def admin_dashboard(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)

    today = datetime.datetime.now()
    year = today.strftime("%Y")

    Total_Sales = OrderDetails.objects.values()
    sales_revenue = 0
    total_profit = 0
    total_sales = 0
    for dic in Total_Sales.values():
        print(dic['amount'])
        sales_revenue = sales_revenue + float(dic['amount'])
    print('sales_revenue', sales_revenue)
    total_profit = int(total_profit + (12 / 100) * sales_revenue)
    total_sales = total_sales + (sales_revenue - total_profit)
    print('Total_Sales', type(Total_Sales))

    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
    for mth in month_list:
        if not Analytics.objects.filter(month=mth, year=year).exists():
            Analytics.objects.create(month=mth, year=year, sales=0, profit=0)

        if OrderDetails.objects.filter(sales_month=mth, sales_year=year).exists():
            x = OrderDetails.objects.filter(sales_month=mth)
            print(type(x))
            amount = 0
            profit = 0
            sales = 0
            for obj in x.values():
                amount = amount + float(obj['amount'])

            if amount == 0:
                profit = 0
            else:
                profit = profit + (12 / 100) * amount
            sales = amount - profit
            x = Analytics.objects.filter(month=mth).update(month=mth, year=year, sales=sales, profit=profit)
        else:
            pass

    dt = Analytics.objects.all()
    # print('Analytics', dt)
    review_data = LenderReviews.objects.values()
    lst = []
    for dic in review_data:
        print('review_data', dic)
        lst.append(dic)
    # print('review_data', review_data)
    print(lst)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            user_name = current_user_.email
            split_name = user_name.split("@")
            print(split_name)
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "analytics": dt,
                "sales_revenue": sales_revenue,
                "total_profit": total_profit,
                "total_sales": total_sales,
                "review_data": lst,
                "report_count": report_count,
            }
            return render(request, "index.html", data)


def admin_logout(request):
    try:
        auth.logout(request)
    except:
        return render(request, 'login.html')

    return render(request, 'login.html')


def login_admin_user(request):
    print(request.user)
    current_user_ = request.user
    print(current_user_, "normal click")
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        if request.method == "POST":
            got_username = request.POST['username'].strip()
            got_password = request.POST['password'].strip()
            print(got_username, got_password)
            if got_username and got_password:
                user_detail = auth.authenticate(email=got_username, password=got_password)
                if user_detail:
                    if user_detail.is_admin and user_detail.is_staff:
                        auth.login(request, user_detail)
                        return redirect("admin_dashboard")
                    return render(request, "login.html")
                messages.error(request, "Unauthorized user. Please enter valid email password ")
                return render(request, "login.html")
            return render(request, "login.html")
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            user_name = current_user_.email
            split_name = user_name.split("@")
            print(split_name[0])
            data = {"admin_email": current_user_.email,
                    "admin_username": ((current_user_.email).split("@"))[0],
                    "profile_image": "../" + str(current_user_.PhotoID),
                    "report_incident": report_incident,
                    "report_count": report_count,

                    }
            return render(request, "index.html", data)

    # return render(request, "index.html")


def admin_user_page(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            print("user_list_to_how")
            all_user_detail = User.objects.all()
            print(all_user_detail)
            user_detail_to_show = []
            for i in range(0, len(all_user_detail)):
                if not all_user_detail[i].is_admin:
                    account_type = Account_type.objects.get(id=all_user_detail[i].UserAccountType_id)

                    print(account_type)
                    user_name = all_user_detail[i].Name_First + " " + all_user_detail[i].Name_Last
                    account_type = account_type
                    photo_id = all_user_detail[i].PhotoID_Number
                    email_id = all_user_detail[i].email
                    contact = all_user_detail[i].phone_number
                    is_verified = all_user_detail[i].is_verified
                    country = all_user_detail[i].country
                    dob = str(all_user_detail[i].Birth_Day) + "/" + str(all_user_detail[i].Birth_Month) + "/" + str(
                        all_user_detail[i].Birth_Year)
                    status = all_user_detail[i].Email_Verified
                    active_user = all_user_detail[i].is_active
                    image_path = "../" + str(all_user_detail[i].PhotoID)
                    print("=========", image_path, "=========")
                    a = {"name": user_name, "account_type": account_type, "photo_id": photo_id,
                         "is_verified": is_verified, "email_id": email_id,
                         "user_profile_img": image_path,
                         "contact": contact, "country": country, "DOB": dob, "status": status,
                         "active_user": active_user,
                         "user_id": all_user_detail[i].account_id}
                    user_detail_to_show.append(a)

            # user_data__ = User.objects.filter(account_id="f7e5fd14-d203-47ce-ad40-a7fd54ba8929").first()

            print(user_detail_to_show)
            # print(user_data__)
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {"use_list": user_detail_to_show,
                    "admin_email": current_user_.email,
                    "admin_username": ((current_user_.email).split("@"))[0],
                    "profile_image": "../" + str(current_user_.PhotoID),
                    "report_incident": report_incident,
                    "report_count": report_count,

                    }
            return render(request, "user-management.html", data)

        return render(request, "login.html")


def edit_user_to_active(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            data = kwargs.values()
            a = list(kwargs.values())
            print(a[0])
            if a:
                user_data__ = User.objects.filter(account_id=str(a[0])).first()
                device_token_obj = UserDeviceToken.objects.get(user_id=str(a[0]))
                device_id = device_token_obj.device_id
                user_data__.is_active = 1
                user_data__.save()
                # Send Push Notification and Mail
                title = "Your Account has been Activated !"
                message_body = "Congratulation ! Your Account has been activated. Feel free to contact us for any query. Thank you"
                push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                Notifications.objects.create(user_id=a[0], title=title, body=message_body, screen_name="noReply")
                res = push_service.notify_single_device(
                    registration_id=device_id,
                    message_title=title,
                    message_body=message_body
                )
                subject = "Your Account has been Activated !"
                message = "Congratulation ! Your Account has been activated. Feel free to contact us for any query. Thank you"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user_data__.email, ]
                send_mail(subject, message, email_from, recipient_list)
                return res
            return redirect("admin_user_page")

        return render(request, "login.html")


def edit_user_to_inactive(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            data = kwargs.values()
            a = list(kwargs.values())
            if a:
                user_data__ = User.objects.filter(account_id=str(a[0])).first()
                device_token_obj = UserDeviceToken.objects.get(user_id=str(a[0]))
                device_id = device_token_obj.device_id
                user_data__.is_active = 0
                user_data__.save()
                # Send Push Notification and Mail
                title = "Your Account has been Inactivated !"
                message_body = "Please be aware that we have suspended your account due to voilations of our guidelines. Please contact us for more information on how we can reactivate your account.  Thank you."
                push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                Notifications.objects.create(user_id=a[0], title=title, body=message_body, screen_name="noReply")
                res = push_service.notify_single_device(
                    registration_id=device_id,
                    message_title=title,
                    message_body=message_body
                )
                subject = "Your Account has been Inactivated !"
                message = "Please be aware that we have suspended your account due to voilations of our guidelines. Please contact us for more information on how we can reactivate your account.  Thank you."
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user_data__.email, ]
                send_mail(subject, message, email_from, recipient_list)
                return res
            return redirect("admin_user_page")
        return render(request, "login.html")


def edit_user_to_verified(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            # data = kwargs.values()
            a = list(kwargs.values())
            print(a[0])
            # send_mail(
            #     'Next Door Rental',  # subject,
            #     "Congratulations ! you are now verified user on the NDR app, You can now avail the features and services of the application",  # message
            #     "drake.augurs@gmail.com",  # from email
            #     ["shaurabh.kumar@augurstech.com"]  # to email,
            #     # fail_silently=False
            # )
            if a:
                user_data__ = User.objects.filter(account_id=str(a[0])).first()
                send_mail(
                    'Next Door Rental',  # subject,
                    "Congratulations ! you are now verified user on the NDR app, You can now avail the features and services of the application",
                    # message
                    "drake.augurs@gmail.com",  # from email
                    [user_data__.email]  # to email,
                    # fail_silently=False
                )
                # print(user_data__.email)
                user_data__.Email_Verified = 1
                user_data__.save()
            return redirect("admin_user_page")

        return render(request, "login.html")


def show_user_profile(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            # data = kwargs.values()
            a = list(kwargs.values())
            print(a[0])
            if a:
                user_data__ = User.objects.filter(account_id=str(a[0])).first()
                # a = {"user_name": user_data__.Name_First + " " + user_data__.Name_Last}
                if user_data__:
                    user_full_data = []
                    account_type = Account_type.objects.get(id=user_data__.UserAccountType_id)
                    dob = str(user_data__.Birth_Day) + "/" + str(user_data__.Birth_Month) + "/" + str(
                        user_data__.Birth_Year)
                    image_path = "../" + str(user_data__.PhotoID)
                    print("=========", image_path, "=========")
                    data = {"user_name": user_data__.Name_First + " " + user_data__.Name_Last,

                            "user_profile_img": "../" + str(user_data__.PhotoID),
                            "account_type": account_type, "admin_username": ((current_user_.email).split("@"))[0],
                            "photo_id": user_data__.PhotoID_Number, "email_id": user_data__.email,
                            "contact_no": user_data__.phone_number,
                            "country": user_data__.country, "DOB": dob, "status": user_data__.Email_Verified,
                            "user_id": user_data__.account_id, "admin_email": current_user_.email,
                            "profile_image": "../" + str(current_user_.PhotoID)}
                    # user_full_data.append(a)
                    # data ={"all_data": user_full_data}
                    return render(request, "view-user.html", data)
                return render(request, "login.html")
        return render(request, "login.html")


def admin_profile_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            print(current_user_.PhotoID)
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_count": report_count,
                "report_incident": report_incident,
            }
            return render(request, "profile.html", data)

        return render(request, "login.html")


def admin_product_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            user_data = Products.objects.all()
            data_ = serializers.serialize("json", user_data.all())
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            product_listing = json.loads(data_)
            product_full_detail = []
            serial_no = 1

            if user_data:
                for i in range(len(product_listing)):
                    product_id = product_listing[i]["pk"]
                    product_name = product_listing[i]["fields"]["ProductName"]
                    is_verified = product_listing[i]["fields"]["is_verified"]
                    created_at = product_listing[i]["fields"]["created_at"]
                    product_categories = product_listing[i]["fields"]["Category"]
                    product_owner_is = product_listing[i]["fields"]["QrCode_Account"]
                    print(product_owner_is, "product_owner_is")
                    if product_categories is not None:
                        prod_cat = ProductCategory.objects.filter(category_id=str(product_categories)).first()
                    if product_owner_is is not None:
                        user_data__ = User.objects.filter(account_id=str(product_owner_is)).first()
                        if user_data__ is not None:
                            if user_data__.UserAccountType_id:
                                account_type = Account_type.objects.get(id=user_data__.UserAccountType_id)
                            else:
                                account_type = "not_defined"
                            data_get = {"serial_no": serial_no,
                                        "user_name": user_data__.Name_First + " " + user_data__.Name_Last,
                                        "account_type": account_type, "product_name": product_name,
                                        "is_verified": is_verified,
                                        "product_categories": prod_cat.category, "created_at": created_at,
                                        "products_id": product_id,
                                        "country": user_data__.country}
                            product_full_detail.append(data_get)
                            serial_no = serial_no + 1
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "product_full_detail": product_full_detail,
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

            }
            return render(request, "product-management.html", data)

        return render(request, "login.html")


def admin_content_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

            }
            return render(request, "content-management.html", data)

        return render(request, "login.html")


def admin_subscription_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            subscription_detail_show = []
            subscription_detail = subscription.objects.filter(profile_id=str(current_user_.account_id))
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            print(subscription_detail, "============")
            if subscription_detail:
                for i in subscription_detail:
                    a = {
                        "account_id": i.id,
                        "subscription_title": i.subscription_title,
                        "plans_type": i.plans_type,
                        "subscription_description": i.subscription_description,
                        "subscription_duration": i.subscription_duration,
                        "subscription_amount": i.subscription_amount,
                        "start_date": i.start_date,
                        "end_date": i.end_date,
                    }
                    subscription_detail_show.append(a)
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

                "show_subscription_data": subscription_detail_show}
            return render(request, "subscription.html", data)

        return render(request, "login.html")


def admin_rewards_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            rewards_detail_show = []
            rewards_detail = rewards.objects.filter(user_id=str(current_user_.account_id))
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            for i in rewards_detail:
                a = {"id": i.id, "user_id": i.id, "title": i.title,
                     "code": i.code, "valid_from": i.valid_from,
                     "valid_to": i.valid_to, "amount": i.amount,
                     "reward_status": i.reward_status}
                rewards_detail_show.append(a)
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

                "show_rewards": rewards_detail_show}
            return render(request, "rewards.html", data)

        return render(request, "login.html")


def admin_add_subscription_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

            }
            return render(request, "add-subscription.html", data)

        return render(request, "login.html")


def admin_add_subscription_page_data(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            print(request.POST['title'].strip(), "=====")
            subscription_data = subscription(profile_id=str(current_user_.account_id),
                                             subscription_title=request.POST['title'].strip(),
                                             plans_type=request.POST['plans_type'].strip(),
                                             subscription_description=request.POST['description'].strip(),
                                             subscription_duration=request.POST['duration'].strip(),
                                             subscription_amount=request.POST['amount'].strip(),
                                             )
            subscription_data.save()
            # data = {"admin_email": current_user_.email, "admin_username": ((current_user_.email).split("@"))[0], "profile_image": "../"+str(current_user_.PhotoID)}
            messages.success(request, "Subscription Added Successfully!!")
            return redirect('admin_subscription_page')

        return render(request, "login.html")


def admin_delete_subscription_data(request, **kwargs):
    print(request.user, "=============================================")
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        try:
            if current_user_.is_admin and current_user_.is_staff:
                # print(list(kwargs.values()), "valeujdhfjhbscjzsc============")
                id_value = list(kwargs.values())[0]
                # id_value = 45
                print(id_value, "valeujdhfjhbscjzsc============")

                subscription_data = subscription.objects.get(id=int(id_value))
                subscription_data.delete()
                # data = {"admin_email": current_user_.email, "admin_username": ((current_user_.email).split("@"))[0], "profile_image": "../"+str(current_user_.PhotoID)}
                messages.success(request, "Subscription deleted Successfully!")
                return redirect('admin_subscription_page')
        except Exception as e:
            print("got some error")
            return redirect('admin_subscription_page')

        return render(request, "login.html")


def admin_edit_subscription_page(request, pk, **kwargs):
    print("+++++++++++++++++++", pk)
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            rewards_detail = rewards.objects.filter(user_id=str(current_user_.account_id))
            subs_data = subscription.objects.get(pk=pk)
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "subs_data": subs_data,
                "report_incident": report_incident,
                "report_count": report_count,
            }
            return render(request, 'edit-subscription.html', data)
        return render(request, "login.html")
    return render(request, 'edit-subscription.html')


def admin_update_subscription_page(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        amount = request.POST.get('amount')
        print("-------------", id, title, description, duration, amount)
        subs_obj = subscription(
            id=id,
            profile_id=request.user.account_id,
            subscription_title=title,
            subscription_description=description,
            subscription_duration=duration,
            subscription_amount=amount
        )
        subs_obj.save()
        messages.success(request, "Subscription Updated Successfully!!")
        return redirect('/admin_subscription_page')


def admin_add_rewards_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            rewards_detail = rewards.objects.filter(user_id=str(current_user_.account_id))
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            print(rewards_detail, "============")
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

            }
            return render(request, "add-rewards.html", data)

        return render(request, "login.html")


def admin_add_rewards_page_data(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            rewards_data = rewards(user_id=str(current_user_.account_id),
                                   title=request.POST['title'].strip(),
                                   code=request.POST['code'].strip(),
                                   amount=request.POST['amount'].strip(),
                                   valid_from=request.POST['valid_from'].strip(),
                                   valid_to=request.POST['valid_to'].strip(),
                                   reward_status=request.POST['reward_status'].strip()
                                   )
            if rewards_data.valid_from == rewards_data.valid_to:
                messages.error(request, "The date of Valid from and Valid to are not same!")
                return redirect(admin_add_rewards_page)
            rewards_data.save()
            # data = {"admin_email": current_user_.email, "admin_username": ((current_user_.email).split("@"))[0], "profile_image": "../"+str(current_user_.PhotoID)}
            return redirect('admin_rewards_page')
            # return redirect("admin_user_page")
        return render(request, "login.html")


def admin_delete_rewards_data(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        try:
            if current_user_.is_admin and current_user_.is_staff:
                id_value = list(kwargs.values())[0]
                print(id_value, "Ananddddddddddddddddddddddddddddddddddd")
                rewards_data = rewards.objects.get(id=int(id_value))
                rewards_data.delete()
                # data = {"admin_email": current_user_.email, "admin_username": ((current_user_.email).split("@"))[0], "profile_image": "../"+str(current_user_.PhotoID)}
                messages.success(request, "Reward Deleted Successfully!")
                return redirect('admin_rewards_page')
                # return redirect("admin_user_page")
        except Exception as e:
            print("got some error")
            return redirect('admin_rewards_page')

        return render(request, "login.html")


def upload_admin_profile(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            try:
                if request.method == "POST" and request.FILES['upload']:
                    print(
                        "hello *************************************************************************************************")
                    image_file_detail = request.FILES['upload']
                    path = os.getcwd()
                    print(image_file_detail.name)
                    name__ = image_file_detail.name
                    print(name__, type(name__))
                    name__ = name__.split(".")
                    val_len = len(name__)
                    extension = name__[val_len - 1]

                    print(extension)
                    # profile_img_name = image_file_detail.name
                    profile_img_name = "admin_profile_pic" + "." + extension
                    # print(profile_img_name)

                    path = os.path.join(path, 'static', 'images', 'admin_profile_image', profile_img_name)
                    destination = open(path, 'wb+')

                    for images in image_file_detail.chunks():
                        destination.write(images)
                    print("Done")
                    user_data__ = User.objects.filter(email=current_user_check).first()
                    if user_data__.is_admin and user_data__.is_staff:
                        user_data__.PhotoID = "static/images/admin_profile_image/" + profile_img_name
                        user_data__.save()

                    # data = {"admin_email": current_user_.email}
                    return redirect("admin_profile_page")

            except Exception as e:
                print(e)

                return redirect("admin_profile_page")

        return render(request, "login.html")


# By Anand
def AddCategoryView(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                category = request.POST.get('category')
                if ProductCategory.objects.filter(category__icontains=category).first():
                    messages.error(request, 'Category Name Already Exist')
                    return redirect('/add_category')
                prod_cat = ProductCategory(category=category)
                prod_cat.save()
                messages.success(request, "Category Created Successfully!")
                return redirect('/categories')

            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            print("total_brands")
            data = {"admin_email": current_user_.email,
                    "admin_username": ((current_user_.email).split("@"))[0],
                    "profile_image": "../" + str(current_user_.PhotoID),

                    "report_incident": report_incident,
                    "report_count": report_count,
                    }
            return render(request, "add-category.html", data)
        return render(request, "login.html")


# By Anand
def CategoryListView(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            category_data = []
            categories = ProductCategory.objects.all().order_by('category')
            for x in categories:
                prod_count = Products.objects.filter(Category_id=x.category_id).count()
                a = {
                    "category_id": x.category_id,
                    "name": x.category,
                    "created": x.created_at,
                    "count": prod_count
                }
                category_data.append(a)
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                'report_incident': report_incident,
                'report_count': report_count,
                'product_category': category_data
            }
            return render(request, "category-list.html", data)
        return render(request, "login.html")


# By Anand
def deleteCategoryView(request, **kwargs):
    print("This is Delete Functions")
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            id_value = list(kwargs.values())[0]
            print("jsdsjfgsdfgdsfgdsf", id_value)
            category_obj = ProductCategory.objects.get(category_id=str(id_value))
            category_obj.delete()
            messages.success(request, "Category Deleted Successfully!")
            return redirect('/categories')
        return render(request, "login.html")


# By Anand
def editCategoryView(request, category_id):
    if request.method == 'POST':
        category = request.POST.get('category')
        cate_obj = ProductCategory.objects.get(category_id=category_id)
        cate_obj.category = category
        cate_obj.save()
        messages.info(request, "Category Updated Successfully!")
        return redirect('/categories')
    category_obj = ProductCategory.objects.get(category_id=category_id)
    return render(request, 'update-category.html', {'category': category_obj})


# import firebase_admin
# from firebase_admin import credentials
# import firebase_admin
# from firebase_admin import credentials, messaging
# from next_door_backend.settings import FCM_DJANGO_SETTINGS

# cred = credentials.Certificate("C:/Users/Augurs-Android/Desktop/Next_Door_Rental/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

# def send_token_push(title, body, tokens):
#     message = messaging.MulticastMessage(
#     notification=messaging.Notification(
#     title=title,
#     body=body
#     ),
#   tokens=tokens
#  )
#     response =messaging.send_multicast(message)
#     print("Message Send Successfully", response)

# def send_notification(request):
#     tokens = ["AAAAX3RjOd4:APA91bFuLJtX1IGnhVpBfBK3X6O77jU5C1LGei46UkwmBiHnbWED5HAjuOwO_mnrsREHuq-8cLqz2imi-oolV6D1iRukjP-UcCZjJUpXhLx-oD_NxL5L6ruPmCCCCbLBRH3OjJeZXF-y"]
#     send_token_push("hi","this is push Message", tokens)


def admin_notification(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=True).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
            }
            return render(request, "notification.html", data)

        return render(request, "login.html")


def NotificationDetails(request):
    report_details = ReportIncident.objects.get(id=1)
    data = {
        "report_details": report_details
    }
    return JsonResponse(data)


# By Anand
# def send_notification(device_token,message_title, message_body):
#     try:
#         push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
#         result=push_service.notify_single_device(
#             registration_id=device_token, 
#             message_title=message_title,
#             message_body=message_body
#             )
#         print(result)
#         return result
#     except:
#       pass  

# By Anand
def send_notification(device_token, title, message_body):
    print("this is title", title)
    try:
        push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
        fcm_token = []
        for obj in device_token:
            Notifications.objects.create(user_id=obj.user_id, title=title, body=message_body)
            fcm_token.append(obj.device_id)
            fcm_token.append(obj.device_id)
        response = push_service.notify_multiple_devices(
            registration_ids=fcm_token,
            message_title=title,
            message_body=message_body
        )
        print(response, "this is response")
        return response
    except:
        pass


# By Anand
from accounts.models import UserDeviceToken


def send_noti(request):
    device_token = UserDeviceToken.objects.all()
    # device_token = "d7-w1wgfRe6AahRwc3JvLK:APA91bHj5rOLTOcoqJ9R-Hqy4_VkIhdJeJbeVpuWqfhZUMv6WISAuRc28jU0gLYIPoCKKDIxvfrz30S_ZFXwYaYNF798ExtaiNhEXxKF8Ceb_FS43NctPDjLRH2f2IntSEuRAaiH4SmP"
    try:
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            response = send_notification(device_token, title, description)
            print(response)
    except Exception as e:
        print(e)
    return redirect("success")


# By Anand
def success(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=True).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            rewards_detail = rewards.objects.filter(user_id=str(current_user_.account_id))
            print(rewards_detail, "============")
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
            }
            return render(request, "success.html", data)


# By Anand
from django.utils import formats


def ReportIncidentDetails(request, pk):
    data = {}
    try:
        if request.method == 'GET':
            get_data = ReportIncident.objects.get(id=pk)
            if get_data:
                data['id'] = get_data.id

                data['about'] = get_data.about
                data['description'] = get_data.description
                data['transaction_id'] = get_data.transaction_id
                data['created'] = formats.date_format(get_data.created, "SHORT_DATETIME_FORMAT")

                # try:
                #     data['imgpath'] = get.photo.url
                # except Exception as e:
                #     print(e)
                return JsonResponse(data)
        else:
            return JsonResponse({'status': 403})
    except Exception as e:

        return JsonResponse({
            "data": data,
            "success": True,
            "status": 200,
            "message": str(e)
        })


# By Anand
def ListofReportIncident(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            all_data = ReportIncident.objects.all().order_by('-created')
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "all_data": all_data,
                "report_count": report_count,

            }
            return render(request, "report-incident-list.html", data)


# By Anand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage


def ReplyReportIncident(request):
    try:
        if request.method == 'POST':
            about = request.POST.get('about')
            user = request.POST.get('user')
            transaction_id = request.POST.get('transaction_id')
            report_id = request.POST.get('report_id')
            description = request.POST.get('description')
            reply = request.POST.get('reply')
            objects = ReportIncident.objects.get(id=report_id)
            email = objects.reported_by.email
            photo = objects.photo
            file = objects.document
            print(email, "465465465465465465465465465465465465465465465465465465465")
            report_obj = ReportIncident(
                id=report_id,
                about=about,
                reply=reply,
                photo=photo,
                document=file,
                reported_by=objects.reported_by,
                description=description,
                transaction_id=transaction_id,
                created=timezone.now(),
                status=True
            )
            report_obj.save()
            subject = about
            body = f"{reply}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            messageEmail = EmailMessage(subject, body, email_from, recipient_list)
            messageEmail.send()
            return JsonResponse({'status': 200})
            if file and photo: attachment = [file, photo]
            for x in attachment:
                messageEmail.attach('file.pdf', x.read(), 'application/pdf')
            messageEmail.send()
            return JsonResponse({'status': 200})
    except Exception as e:
        return JsonResponse({
            "status": 403,
            "success": False,
            "message": str(e)
        })


# By Anand
def UserActiveInactive(request, user_id):
    data = {}
    try:
        if request.method == 'POST':
            user_is_active = request.POST.get('is_active')
            print(user_is_active, "++++++++++++++++++++++++++++++++++++++++++++++++")
            if user_is_active == '0':
                user_obj = User.objects.get(account_id=user_id)
                user_obj.is_active = True
                user_obj.save()
            if user_is_active == '1':
                user_obj = User.objects.get(account_id=user_id)
                user_obj.is_active = False
                user_obj.save()
    except Exception as e:
        return JsonResponse({str(e)})
    return JsonResponse(data)


# By Anand
def admin_edit_rewards(request, pk):
    if request.method == 'POST':
        title = request.POST.get('title')
        code = request.POST.get('code')
        amount = request.POST.get('amount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        reward_status = request.POST.get('reward_status')
        rewards_obj = rewards.objects.get(id=pk)
        rewards_obj.title = title
        rewards_obj.code = code
        rewards_obj.amount = amount
        rewards_obj.valid_from = valid_from
        rewards_obj.valid_to = valid_to
        rewards_obj.reward_status = reward_status
        rewards_obj.save()
        messages.info(request, "Reward Updated Successfully!")
        return redirect('/admin_rewards_page')
    reward = rewards.objects.get(id=pk)
    return render(request, 'edit-reward.html', {'reward': reward})


# By Anand
def ViewUser(request, user_id):
    current_user_ = request.user
    if request.method == 'POST':
        Name_First = request.POST.get('Name_First')
        Name_Last = request.POST.get('Name_Last')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        CountryOfBirth = request.POST.get('CountryOfBirth')
        country = request.POST.get('country')
        Citizenship = request.POST.get('Citizenship')
        PhotoID_Number = request.POST.get('PhotoID_Number')
        VerificationDate = request.POST.get('VerificationDate')
        VerificationPersonalID = request.POST.get('VerificationPersonalID')
        CreditCard_Type = request.POST.get('CreditCard_Type')
        is_verified = request.POST.get('is_verified')
        print("kdjskfjgsdjfhsdfvdkfdskfgsdf", is_verified)
        user_obj = User.objects.get(account_id=user_id)
        if user_obj is not None:
            user_obj.Name_First = Name_First
            user_obj.Name_Last = Name_Last
            user_obj.email = email
            user_obj.phone_number = phone_number
            user_obj.CountryOfBirth = CountryOfBirth
            user_obj.country = country
            user_obj.Citizenship = Citizenship
            user_obj.PhotoID_Number = PhotoID_Number
            user_obj.Citizenship = Citizenship
            user_obj.VerificationDate = VerificationDate
            user_obj.VerificationPersonalID = VerificationPersonalID
            user_obj.CreditCard_Type = CreditCard_Type
            user_obj.save()
            messages.success(request, "User Data Updated Successfully!")
            return redirect('/admin_user_page')
    user_data = User.objects.get(account_id=user_id)
    location = Address.objects.get(QrCode_Account=user_id)
    report_count = ReportIncident.objects.filter(status=False).count()
    report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
    return render(request, 'edit-user.html', {'user': user_data, 'location': location, 'report_count': report_count,
                                              'report_incident': report_incident,
                                              "admin_username": ((current_user_.email).split("@"))[0], })


# By Anand
def userVerfication(request):
    print("function Called")
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        is_verified = request.POST.get('is_verified')
        if user_id is not None:
            user_obj = User.objects.get(account_id=user_id)
            noti_obj = UserDeviceToken.objects.get(user_id=user_id)
            fcm_token = noti_obj.device_id
            email = user_obj.email
            print("User Device Token", fcm_token)
            if is_verified == 'false':
                user_obj.is_verified = True
                # Send Push Notification and Mail
                title = "Your Account has been Verified!"
                message_body = "You are all set! Now you have full access to the application and any assets are listed now!"
                push_service = FCMNotification(api_key=settings.FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                print(push_service, "===========================")
                Notifications.objects.create(user_id=user_id, title=title, body=message_body, screen_name="noReply")
                res = push_service.notify_single_device(
                    registration_id=fcm_token,
                    message_title=title,
                    message_body=message_body
                )
                # print(res,"=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
                # Send Mail
                subject = "Your Account has been Verified!"
                message = "You are all set! Now you have full access to the application and any assets are listed now!"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail(subject, message, email_from, recipient_list)
                user_obj.save()
                # print(res)
                return JsonResponse({
                    "status": 200,
                    "res": res,
                })
            else:
                user_obj.is_verified = False
                user_obj.save()
                return JsonResponse({
                    "status": 403
                })


def NDR_Taxes_View(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                tax_rate = request.POST.get('tax_rate')
                ndr_charge = request.POST.get('ndr_charge')
                points_earned_rate = request.POST.get('points_earned_rate')
                ndr_credit_card_charge = request.POST.get('ndr_credit_card_charge')
                renter_credit_card_charge = request.POST.get('renter_credit_card_charge')
                NDR_Taxes.objects.create(
                    tax_rate=tax_rate,
                    ndr_charge=ndr_charge,
                    points_earned_rate=points_earned_rate,
                    ndr_credit_card_charge=ndr_credit_card_charge,
                    renter_credit_card_charge=renter_credit_card_charge,
                )
                messages.success(request, "Our Taxes Added Successfully!")
                return redirect('/ndr_taxes_list')
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

            }
            return render(request, 'ndr-taxes.html', data)


def TaxList(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            all_tax = NDR_Taxes.objects.all()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

                "all_tax": all_tax,
            }
            return render(request, 'ndr-taxes-list.html', data)


def UpdateNDRTaxes(request, id):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                tax_rate = request.POST.get('tax_rate')
                ndr_charge = request.POST.get('ndr_charge')
                ndr_credit_card_charge = request.POST.get('ndr_credit_card_charge')
                renter_credit_card_charge = request.POST.get('renter_credit_card_charge')
                points_earned_rate = request.POST.get('points_earned_rate')
                taxes_obj = NDR_Taxes.objects.get(id=id)
                if taxes_obj is not None:
                    taxes_obj.tax_rate = tax_rate
                    taxes_obj.ndr_charge = ndr_charge
                    taxes_obj.ndr_credit_card_charge = ndr_credit_card_charge
                    taxes_obj.renter_credit_card_charge = renter_credit_card_charge
                    taxes_obj.points_earned_rate = points_earned_rate
                    taxes_obj.save()
                    messages.success(request, 'Our Taxes Updated Successfully!')
                    return redirect('/ndr_taxes_list')
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            taxes = NDR_Taxes.objects.get(id=id)
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,

                "taxes": taxes,
            }
            return render(request, 'update-ndr-taxes.html', data)


def DeleteNDRTax(request, pk):
    try:
        get_tax = NDR_Taxes.objects.get(id=pk)
        get_tax.delete()
        messages.success(request, "Tax Removed Successfully")
        return redirect("/ndr_taxes_list")
    except Exception as e:
        print(e)


def TransactionDetails(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            transactions = OrderDetails.objects.all().order_by('date_of_payment')
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
                "transactions": transactions,
            }
    return render(request, 'transactions.html', data)


def admin_pickup_return_page(request, **kwargs):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            pickup_return = ProductPickUpReturn.objects.all()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
                "pickup_return": pickup_return,
            }
            return render(request, "pickup-and-return.html", data)

        return render(request, "login.html")


from openpyxl.chart import LineChart, Reference
from django.http import HttpResponse
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook


def exelgraph(request):
    profit = Analytics.objects.values_list('profit', flat=True)
    sales = Analytics.objects.values_list('sales', flat=True)
    month = Analytics.objects.values('month')
    lst_profit = list(profit)
    lst_sales = list(sales)
    lst_month = list(month)
    print('profit', lst_profit)
    print('sales', lst_sales)
    # print('months', lst_month)
    lst = []
    for ele in lst_month:
        for v in ele.values():
            lst.append(v)

    print('lst_month', lst)

    l4 = [['sales', 'profit', 'month'], ]

    for i in range(len(lst)):
        x = [lst_sales[i], lst_profit[i], lst[i], ]
        l4.append(x)

    rows = l4

    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)

    values = Reference(ws, min_col=1, min_row=1, max_col=2, max_row=13)
    chart = LineChart()
    chart.add_data(values, titles_from_data=True)

    chart.title = "NDR Analysis"
    chart.style = 13
    chart.x_axis.title = "Months"
    # chart.x_axis.number_format = 'd-mmm'
    # chart.x_axis.majorTimeUnit = "months"
    chart.y_axis.title = "Sales and Profit"
    ws.add_chart(chart, "E4")

    wb.save("LineChart.xlsx")

    response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses.xlsx'
    return response


def admin_add_faq(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                questions = request.POST.get("questions")
                answers = request.POST.get("answers")
                obj = NDR_FAQs(questions=questions, answers=answers)
                obj.save()
                messages.success(request, "Data Inserted Successfully!")
                return redirect('/FAQs')
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            pickup_return = ProductPickUpReturn.objects.all()

            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
                "pickup_return": pickup_return,
            }
            return render(request, "add-faq.html", data)

        return render(request, "login.html")


def faq_list(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            faqs = NDR_FAQs.objects.all()
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            pickup_return = ProductPickUpReturn.objects.all()
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
                "pickup_return": pickup_return,
                "faqs": faqs,
            }
            return render(request, "faqs.html", data)

        return render(request, "login.html")


def Admin_Delete_FAQs(request, id):
    obj = NDR_FAQs.objects.get(id=id)
    obj.delete()
    messages.success(request, 'Question Deleted Successfully')
    return redirect('/FAQs')


def Admin_Update_FAQs(request, id):
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                questions = request.POST.get('questions')
                answers = request.POST.get('answers')
                faq = NDR_FAQs.objects.get(id=id)
                faq.questions = questions
                faq.answers = answers
                faq.save()
                messages.success(request, "Question Updated Successfully!")
                return redirect('/FAQs')
            report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
            report_count = ReportIncident.objects.filter(status=False).count()
            pickup_return = ProductPickUpReturn.objects.all()
            faq = NDR_FAQs.objects.get(id=id)
            data = {
                "admin_email": current_user_.email,
                "admin_username": ((current_user_.email).split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "report_incident": report_incident,
                "report_count": report_count,
                "pickup_return": pickup_return,
                "faq": faq,
            }
            return render(request, "update-faqs.html", data)
        return render(request, "login.html")


def ProductDetails(request, product_id):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    report_incident = ReportIncident.objects.filter(status=False).order_by('-created')[0:5]
    report_count = ReportIncident.objects.filter(status=False).count()
    pickup_return = ProductPickUpReturn.objects.all()
    product = Products.objects.get(Products_id=product_id)
    data = {
        "admin_email": current_user_.email,
        "admin_username": ((current_user_.email).split("@"))[0],
        "profile_image": "../" + str(current_user_.PhotoID),
        "report_incident": report_incident,
        "report_count": report_count,
        "pickup_return": pickup_return,
        "product": product,
    }
    return render(request, 'view_product.html', data)


def VerifyProduct(request):
    if request.method == 'POST':
        is_verified = request.POST.get('is_verified')
        product_id = request.POST.get('product_id')
        if is_verified == 'false':
            product_obj = Products.objects.get(Products_id=product_id)
            product_obj.is_verified = True
            product_obj.save()
            return JsonResponse({'status': 200})
        if is_verified == 'true':
            product_obj = Products.objects.get(Products_id=product_id)
            product_obj.is_verified = False
            product_obj.save()
            return JsonResponse({'status': 200})


def admin_add_terms_conditions(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "templates/login.html")
    else:
        if request.user.is_admin and request.user.is_staff:
            if request.method == 'POST':
                files = request.FILES.get("files")

                # Check if file is a PDF or Word document
                allowed_extensions = ['.pdf', '.doc', '.docx']
                file_extension = os.path.splitext(files.name)[1].lower()

                if file_extension not in allowed_extensions:
                    messages.warning(request, 'Invalid file format. Only PDF and Word documents are allowed.')
                    return render(request, 'templates/add-terms-conditions.html')

                # Check if the file already exists in the desired folder
                storage = FileSystemStorage(location=settings.MEDIA_ROOT)
                target_path = f'user/PPs_documents/{files.name}'
                if storage.exists(target_path):
                    messages.error(request, 'File already exists')
                    return render(request, 'templates/add-terms-conditions.html')

                obj = NDR_Documents(files=files)
                obj.save()
                messages.success(request, "Data Inserted Successfully!")
                return redirect('terms_conditions_list')
            data = {

                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }

            return render(request, 'templates/add-terms-conditions.html', data)

        return render(request, 'templates/login.html')


def terms_conditions_list(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "templates/login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            tc_list = NDR_Documents.objects.all()
            data = {
                "tc_list": tc_list,
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }

            return render(request, 'templates/terms-conditions-list.html', data)

        return render(request, 'templates/login.html')


def delete_tcs(request, id):
    obj = get_object_or_404(NDR_Documents, id=id)
    obj.delete()
    messages.success(request, 'T&C Deleted Successfully')
    return redirect('terms_conditions_list')


def download_file(request, id):
    try:
        # Retrieve the file object based on the id
        file = NDR_Documents.objects.get(id=id)

        # Construct the file path on the server
        file_path = file.files.path

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')

            # Set the content-disposition header to trigger the file download
            response['Content-Disposition'] = 'attachment; filename={}'.format(file.files.name)

            return response
    except ObjectDoesNotExist:
        return HttpResponse('File not found.', status=404)


def add_privacy_policy(request):
    current_user_ = request.user
    current_user_check = str(current_user_)
    if request.user.is_anonymous:
        return render(request, "templates/login.html")
    else:
        if request.user.is_admin and request.user.is_staff:
            if request.method == 'POST':
                files = request.FILES.get("files")

                # Check if file is a PDF or Word document
                allowed_extensions = ['.pdf', '.doc', '.docx']
                file_extension = os.path.splitext(files.name)[1].lower()

                if file_extension not in allowed_extensions:
                    messages.warning(request, 'Invalid file format. Only PDF and Word documents are allowed.')
                    return render(request, 'templates/add-privacy-policy.html')

                # Check if the file already exists in the desired folder
                storage = FileSystemStorage(location=settings.MEDIA_ROOT)
                target_path = f'user/PPs_documents/{files.name}'
                if storage.exists(target_path):
                    messages.error(request, 'File already exists')
                    return render(request, 'templates/add-privacy-policy.html')

                obj = NDR_PrivacyPolicy(files=files)
                obj.save()
                messages.success(request, "Data Inserted Successfully!")
                return redirect('privacy_policy_list')
            data = {
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }
            return render(request, 'templates/add-privacy-policy.html', data)

        return render(request, 'templates/login.html')


def privacy_policy_list(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            pp_list = NDR_PrivacyPolicy.objects.all()
            data = {
                "pp_list": pp_list,
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }

            return render(request, 'templates/privacy-policy-list.html', data)

        return render(request, 'templates/login.html')


def delete_Privacy_Policy(request, id):
    obj = get_object_or_404(NDR_PrivacyPolicy, id=id)
    obj.delete()
    messages.success(request, 'File Deleted Successfully')
    return redirect('privacy_policy_list')


def download_file_pp(request, id):
    try:
        # Retrieve the file object based on the id
        file = NDR_PrivacyPolicy.objects.get(id=id)

        # Construct the file path on the server
        file_path = file.files.path
        print(file_path, "filespath")

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')

            # Set the content-disposition header to trigger the file download
            response['Content-Disposition'] = 'attachment; filename={}'.format(file.files.name)

            return response
    except ObjectDoesNotExist:
        return HttpResponse('File not found.', status=404)


from accounts.models import Notification


def admin_add_notification(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                title = request.POST.get("title")
                content = request.POST.get("content")
                print(title, content, "datacheck")
                obj = Notification(title=title, content=content)
                obj.save()

                messages.success(request, "Data Inserted Successfully!")
                return redirect('/notifications_lists')
            data = {
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }
            return render(request, 'templates/add-notifications.html', data)

        return render(request, "login.html")


def notifications_lists(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            notif_list = Notification.objects.all()
            data = {
                "notif_list": notif_list,
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }

            return render(request, 'templates/notifications-list.html', data)

        return render(request, 'templates/login.html')


def delete_Notification(request, id):
    obj = get_object_or_404(Notification, id=id)
    obj.delete()
    messages.success(request, 'Notification Deleted Successfully')
    return redirect('notifications_lists')


def edit_notifications(request, id):
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            if request.method == 'POST':
                title = request.POST.get('title')
                content = request.POST.get('content')
                obj = Notification.objects.get(id=id)

                if obj is not None:
                    obj.title = title
                    obj.content = content
                    obj.save()
                    messages.success(request, "Notification Updated Successfully!")
                return redirect('notifications_lists')
            objs = Notification.objects.get(id=id)
            data = {
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "obj": objs,
            }
            return render(request, 'templates/update-notification.html', data)

        return render(request, "login.html")


import requests
from django.shortcuts import render


def get_chat_lists(request, uuid):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            # Replace 'your-firebase-database-url' with your Firebase Realtime Database URL
            firebase_database_url = 'https://next-door-renal-default-rtdb.firebaseio.com/'

            # List of chat list paths in Firebase (you can customize this based on your data structure)
            chat_list_paths = [f'one_to_one/{uuid}']

            chat_lists = {}

            for path in chat_list_paths:
                # Endpoint URL for each chat list
                endpoint = f'{firebase_database_url}/{path}.json'

                # Make a GET request to Firebase to fetch the chat list
                response = requests.get(endpoint)

                if response.status_code == 200:
                    chat_lists[path] = response.json()
                    chat_list = []

                    for outer_key, inner_dict in chat_lists[path].items():
                        for inner_key, inner_value in inner_dict.items():
                            chat_sender = inner_value['chat_sender']
                            chat_receiver = inner_value['chat_receiver']
                            chat_message = inner_value['chat_message']
                            chat_time = inner_value['chat_time']
                            print(chat_sender, chat_receiver, chat_message, "mssssgg")
                            chat_list.append(
                                (outer_key, inner_key, chat_sender, chat_receiver, chat_message, chat_time))

                else:
                    # Handle error appropriately (return an error message or an empty list)
                    chat_lists[path] = {'error': 'Failed to fetch chat list'}
            data = {
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../../" + str(current_user_.PhotoID),
                'chat_list': chat_list

            }
            return render(request, 'templates/chat_history.html', data)


def chat_page(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            user = User.objects.all()
            print(user, 'bj')
            data = {
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
                "user": user,
            }
            return render(request, 'templates/chatList.html', data)


def view_page(request, email):
    user = User.objects.get(email=email)
    uuid = user.uuid  # Assuming the User model has a 'uuid' field
    print(uuid, "uuuuuuid")
    return redirect('get_chat_list', uuid=uuid)


def abusive_content_list(request):
    print(request.user)
    current_user_ = request.user
    current_user_check = str(current_user_)
    if current_user_check == "AnonymousUser":
        return render(request, "templates/login.html")
    else:
        if current_user_.is_admin and current_user_.is_staff:
            abusive_list = ChatAbusiveContent.objects.all()
            data = {
                "abusive_list": abusive_list,
                "admin_email": current_user_.email,
                "admin_username": (current_user_.email.split("@"))[0],
                "profile_image": "../" + str(current_user_.PhotoID),
            }

            return render(request, 'abusive-content-list.html', data)

        return render(request, 'templates/login.html')


def download_file_chat(request, id):
    try:
        # Retrieve the file object based on the id
        file = ChatAbusiveContent.objects.get(id=id)

        # Construct the file path on the server
        file_path = file.files.path  # Use 'path' instead of 'name'

        # Debugging: Print the file path to verify it
        print("File Path:", file_path)

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')

            # Set the content-disposition header to trigger the file download
            response['Content-Disposition'] = 'attachment; filename={}'.format(file.files.name)

            return response
    except ObjectDoesNotExist:
        return HttpResponse('File not found.', status=404)
