
from rest_framework.permissions import IsAuthenticated, AllowAny
from next_door_backend.settings import FCM_DJANGO_SETTINGS
from django.views.decorators.csrf import csrf_exempt
from payments.calculation import reward_calculation
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializer import BankAccountSerializer
from .xero_helper import refresh_xero_tokens
from requests_oauthlib import OAuth2Session
from rest_framework.views import APIView
from next_door_backend import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from pyfcm import FCMNotification
from accounts.models import *
from products.models import *
from .serializer import *
from .helpers import *
from products.helpers import send_email
from xero import Xero
import datetime
import stripe
import json
stripe.api_key = settings.STRIPE_SECRET_KEY

# domain_url = "http://54.89.50.153:7070"
domain_url = "http://127.0.0.1:8000"

class CreateStripeAccount(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            user_id  = request.user.account_id
            accounts_details = stripe.Account.create(
                type="express",
                email = request.user.email,
                capabilities={
                    "transfers": {"requested": True},
                },
                metadata = {
                    "user_id" : request.user.account_id
                },
                )
            lender_obj = BankAccount.objects.filter(user = user_id).first()
            if lender_obj is None :
                BankAccount.objects.create(user_id = user_id, stripe_account_id = accounts_details.id)
                return Response({
                    "account": accounts_details,
                    "status": 200,
                    "success": True,
                    "message": "Your Details"
                })
            
            lenderObj = BankAccount.objects.get(user_id = user_id)
            lenderObj.stripe_account_id = accounts_details.id
            lenderObj.save()
            return Response({
                "account": accounts_details,
                "status": 200,
                "success": True,
                "message": "Your Details"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

class LinkAccountView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            get_id = request.query_params.get("stripe_account_id")
            accounts_link = stripe.AccountLink.create(
                account=get_id,
                refresh_url=domain_url +'/users/oauth/callback/',
                return_url= domain_url +'/users/oauth/callback/?id={get_id}',
                type="account_onboarding",
            )
            return Response({
                "account": accounts_link,
                "status": 200,
                "success": True,
                "message": "Your Details"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

def send_notification(user_id,fcm_token,title, message_body):
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



class PaymentGatewayView(APIView):
    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        request_inbox_id = request.query_params.get('request_inbox_id')
        ndr_charges = request.query_params.get('ndr_charges')
        product_id = request.query_params.get('product_id')
        lender_id = request.query_params.get('lender_id')
        amount = request.query_params.get('amount')
        delivery_fee = request.query_params.get('delivery_fee')
        reward_points = request.query_params.get('reward_points', None)
        final_amount = 0
        if reward_points is None:
            final_amount += int(amount)
        else:
            minus_reward_point = int(amount) - int(reward_points)
            final_amount += minus_reward_point
        renter_id = request.user.account_id
        product_obj = Products.objects.filter(Products_id = product_id).first()
        if product_obj is None:
            return Response({
                "status": 400,
                "success" : False,
                "message": "Product does not exist"
            })
        stripeAccountID = BankAccount.objects.filter(user_id = lender_id).first()
        if stripeAccountID is None:
            return Response({
                "status": 400,
                "success" : False,
                "message": "Currently lender can not accept the payments"
            })
        payment_session = stripe.checkout.Session.create(
            mode="payment",
            customer_email = request.user.email,
            invoice_creation={"enabled": True},
            metadata = {
                "reward_points" : reward_points,
                "product_id" : product_id,
                "ndr_charges" : ndr_charges,
                "lender_id" : lender_id,
                "renter_id" : renter_id,
                "request_inbox_id" : request_inbox_id,
                "delivery_fee" : delivery_fee,
            },
            line_items=[{
                'price_data': {
                'currency': 'CAD',
                'unit_amount': final_amount,
                'product_data': {
                    'name': product_obj.ProductName,
                    'description': product_obj.ProductDescription,  
                },
                }, 
                'quantity': 1,
            }],
           
            payment_intent_data={
                "application_fee_amount": ndr_charges,
                "transfer_data": {"destination": stripeAccountID.stripe_account_id},
            },
            
            success_url=domain_url + '/api/payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/api/payment-cancelled/',
        )
        return Response({
            "status": 200,
            "message" : "Payment link generated. Please find url",
            'sessionId': payment_session['id'],
            "payment_intent" : payment_session,
        })

def PaymentSuccessView(request):
    try:
        session_id = request.GET.get('session_id')
        stripe_res = stripe.checkout.Session.retrieve(session_id)
        user_id = stripe_res['metadata']['renter_id']
        delivery_fee = stripe_res['metadata']['delivery_fee']
        amountInPoints = int(stripe_res['amount_total'])
        amountInDollar = int(amountInPoints)/100
        rewardPoints = stripe_res['metadata']['reward_points']
        OrderDetails.objects.create(
            request_inbox_id = stripe_res['metadata']['request_inbox_id'],
            product_id = stripe_res['metadata']['product_id'],
            lender_id = stripe_res['metadata']['lender_id'],
            renter_id = user_id,
            amount = float(round(amountInDollar, 2)),
            delivery_fee = float(delivery_fee),
            reward_points = rewardPoints,
            payment_status = stripe_res['payment_status'],
            payment_id = stripe_res['payment_intent'],
        )
        request_obj = RequestInbox.objects.get(id = stripe_res['metadata']['request_inbox_id'])
        request_obj.payment_status = stripe_res['payment_status']
        request_obj.reward_points = rewardPoints
        request_obj.save()
        reward_calculation(amountInPoints, user_id)
        # Send Push Notification and Mail
        device_token_obj = UserDeviceToken.objects.get(user_id =  user_id)
        fcm_token = device_token_obj.device_id
        renter_name = device_token_obj.user.Name_First
        title = f"Payment successful"
        message_body = f"Dear {renter_name}, your payment C${amountInDollar} amount  is successfully debited."
        send_notification(user_id, fcm_token, title, message_body)
    except Exception as e:
        print(e)
    return render(request, 'payment-success.html')
    
def PaymentCancelView(request):
    return render(request, 'payment-failed.html')


# Xero OAuth2.0
class XeroAuthView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # Set up Xero OAuth 2.0 parameters
            client_id = settings.XERO_CLIENT_ID
            redirect_uri = "http://localhost:8000/xero/callback"
            scope = "openid profile email offline_access"
            xero = OAuth2Session(client_id, redirect_uri=redirect_uri,scope=scope)
            authorization_url, state = xero.authorization_url('https://login.xero.com/identity/connect/authorize')
            request.session['xero_auth_state'] = state
            return Response({
                "status" : 200,
                "success" : True,
                "authorization_url":authorization_url
            })
        except Exception as e:
            return Response({
                "status" : 400,
                "success" : False,
                "message":str(e)
            })
      

def XeroAuthCallBackURL(request):
    stored_state = request.GET.get('state', None)
    if stored_state is None or stored_state != request.GET.get('state'):
        return Response({
            "status" : 400,
            "success" : False,
            "message":"Invalid state parameter"
        })
    client_id = '9F801E1DE2FE42A88330D5DBE80F0692'
    client_secret = 'XsrSRBuNuqUJKqb1-56hZIW6hc29NIO7GxafbsLzF6diAQtF'
    redirect_uri = 'http://localhost:8000/xero/callback'
    xero = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token_url = 'https://identity.xero.com/connect/token'
    token = xero.fetch_token(
        token_url,
        authorization_response=request.build_absolute_uri(),
        client_secret=client_secret
    )
    access_token = token['access_token']
    refresh_token = token['refresh_token']
    existingToken = XeroAccountingToken.objects.all()
    if existingToken:
        XeroAccountingToken.objects.update(
            access_token = token['access_token'], 
            refresh_token = token['refresh_token'], 
            expires_in = token['expires_in'],
            token_type = token['token_type']
        )
        return JsonResponse({
            "status":200,
            "message": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
        })
    XeroAccountingToken.objects.create(
        access_token = token['access_token'], 
        refresh_token = token['refresh_token'], 
        expires_in = token['expires_in'],
        token_type = token['token_type']
    )
    return JsonResponse({
        "status":200,
        "message": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
    })

class XeroRefreshAccessTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            new_token = refresh_xero_tokens(refresh_token)
            print(new_token)
            print(new_token['access_token'])
            XeroAccountingToken.objects.update(
                refresh_token = new_token['refresh_token'], 
                access_token = new_token['access_token'], 
                expires_in = new_token['expires_in'],
                token_type = new_token['token_type']
            )
            return Response({
                "status": 200,
                "success" : True,
                "refresh_token": new_token['refresh_token'], 
                "access_token" : new_token['access_token']
            })
        except Exception as e:
            return Response({
                "status": 400,
                "success" : False,
                "message":str(e)
            })

    def get(self, request):
        refreshToken = XeroAccountingToken.objects.all()
        list = []
        for i in refreshToken:
            data = {
                "refreshToken" : i.refresh_token
            }
            list.append(data)

        return Response({
                "status": 200,
                "success" : True,
                "token": list
            })



class BookedProductsView(APIView):
    def get(self, request):
        productId = request.query_params.get('product_id')
        lender_id = request.query_params.get('lender_id')
        requestProducts = RequestInbox.objects.filter(product_id =productId, request_status = 'Accepted')
        list = []
        userUnavailabilityList = []
        if requestProducts:
            for i in requestProducts:
                userUnavailability = UserUnavailability.objects.filter(user_id = lender_id)
                for x in userUnavailability:
                    payload = {
                        "unavailableDate": x.unavailableDate,
                    }
                    userUnavailabilityList.append(payload)
                data = {
                    "fromDate" : i.from_date,
                    "toDate" : i.to_date,
                    "renter_id" : i.renter.account_id,
                    "lender_id" : i.lender.account_id,
                    "product_id" : i.product.Products_id,
                }
                list.append(data)
                return Response({
                    "status" : 200,
                    "success" : False,
                    "bookedProductDate": list,
                    "userUnavailabilityList": userUnavailabilityList,
                    "lender_available_schedule" : [x.weekAvailability for x in UserWeekAvailability.objects.filter(user_id = lender_id)],
                })
        userUnavailability = UserUnavailability.objects.filter(user_id = lender_id)
        for x in userUnavailability:
            payload = {
                "unavailableDate": x.unavailableDate,
            }
            userUnavailabilityList.append(payload)
        return Response({
            "status" : 400,
            "success" : False,
            "bookedProductDate": list,
            "userUnavailabilityList": userUnavailabilityList,
            "lender_available_schedule" : [x.availabilityDate for x in UserWeekAvailability.objects.filter(user_id = lender_id)],
        })

class RefundPaymentView(APIView):
    def post(self, request):
        try:
            orderID = request.data.get('orderID')
            order = get_object_or_404(OrderDetails, id=orderID)
            
            payment_intent_id = order.payment_id
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if payment_intent['status'] != 'succeeded':
                return Response({
                    "status": 400,
                    "success": False,
                    'message': 'Payment is not eligible for a refund.',
                })
            refund = stripe.Refund.create(payment_intent=payment_intent_id)
            order.payment_status = "Refund"
            order.save()

            return Response({
                'status': 200,
                'success': True,
                'message': 'Payment refunded successfully.'
            })
        except stripe.error.StripeError as e:
            return Response({
                'message': str(e),
                'status': 400,
                'success': False,
            })
    
class AddStripeBankAccountView(APIView):
    def post(self, request):
        serializer = BankAccountSerializer(data=request.data)
        if serializer.is_valid():
            bank_account = serializer.save()
            try:
                # Create the bank account token
                bank_token = stripe.Token.create(
                    bank_account={
                        'country': 'US',
                        # 'country':'US' if bank_account.currency == 'USD' else 'CA',
                        'currency': 'USD',
                        "account_holder_type": "individual",
                        'account_holder_name': bank_account.account_holder_name,
                        'account_number': bank_account.account_number,
                        'routing_number': bank_account.routing_number,
                    }, 
                )
                # Link the bank account to the Stripe account
                stripe_account = stripe.Account.create(
                    type="custom",
                    email = request.user.email,
                    country="CA",
                    business_type = "individual",
                    # country= 'US' if bank_account.currency == 'USD' else 'CA',
                    capabilities={
                        'card_payments': {'requested': True},
                        'transfers': {'requested': True},
                    },
                    metadata = {
                        "user_id" : request.user.account_id
                    },
                )
                stripe_account.external_accounts.create(external_account=bank_token.id)
                bank_account.stripe_account_id = stripe_account.id
                bank_account.user_id = request.user.account_id
                bank_account.save()
                accounts_link = stripe.AccountLink.create(
                    account=stripe_account.id,
                    refresh_url= f"{domain_url}/users/oauth/callback/",
                    return_url= f"{domain_url}/users/oauth/callback/?id={stripe_account.id}",
                    type="account_onboarding",
                )
                return Response({
                    "status":200,
                    "success": True,
                    "url":accounts_link['url']
                })
            except stripe.error.StripeError as e:
                return Response({'error': str(e)}, status=400)
        else:
            return Response(serializer.errors, status=400)

    def get(self, request):
        stripeAccountId = BankAccount.objects.filter(user = request.user).first()
        if stripeAccountId is None:
            return Response({
                "status": 400,
                "success": False,
                "customerDetails": "You have not bank account"
            })
        customerDetails = stripe.Account.retrieve(stripeAccountId.stripe_account_id)
        return Response({
            "status":200,
            "success":True,
            "customerDetails": customerDetails
        })
    
    def put(self, request):
        serializer = BankAccountSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data from the serializer
            validated_data = serializer.validated_data
            bankDetails = BankAccount.objects.filter(user = request.user).first()
            if bankDetails is None:
                return Response({
                    "status": 400,
                    "success": False,
                    "customerDetails": "You have not bank account"
                })
            try:
                stripe.Customer.modify(
                    'cus_ODI6Yv1M4ECZPh',
                    source={
                        'object': 'bank_account',
                        'account_number': validated_data['account_number'],
                        'routing_number': validated_data['routing_number'],
                        'account_holder_name': validated_data['account_holder_name'],
                        'account_holder_type': "individual",
                    }
                )
            except stripe.error.StripeError as e:
                return Response({
                    "status": 400,
                    "success":False,
                    "message": str(e)
                })

            return Response({
                "status":200,
                "success":True,
                "message": "Bank details updated successfully."
            })
        
        return Response({
            "status":400,
            "success":False,
            "message": serializer.errors
        })

def BankAccountReturnURL(request):  
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        acc_id = request.GET.get('id')
        stripeUserDetails = stripe.Account.retrieve(acc_id)
        user_id = stripeUserDetails['metadata']['user_id']
        device_token_obj = UserDeviceToken.objects.filter(user_id =  user_id).first()
        if device_token_obj is None:
            print("User Device id does not exist!")
        fcm_token = device_token_obj.device_id

        userObj = User.objects.get(account_id = user_id)
        userObj.is_bank_account = True
        userObj.save()

        title = f"Stripe Account Creation"
        message_body = f"Your stripe  account has been created Now. enjoy !."
        send_notification(user_id, fcm_token, title, message_body)

        return render(request, "account-connected-success.html")
    except Exception as e:
        print(e)
    return render(request, "account-connected-success.html")


class RequestTransactionExtendView(APIView):
    def post(self, request):
        serializer = ExtendTransactionSerializer(data=request.data)
        if serializer.is_valid():
            requestTransaction = serializer.save()
            requestTransaction.extendStatus = "Requested"
            requestTransaction.save()
            try:
                user_id = request.user.account_id
                userEmail = request.user.email
                deviceToken = UserDeviceToken.objects.filter(user_id=user_id).first()
                fcm_token = deviceToken.device_id

                title = "Transaction Extend"
                message_body = "Someone want to extend transaction"
                send_push_notification(user_id, fcm_token, title, message_body)

                subject = "Transaction Extend"
                html_content = "Someone want to extend transaction"
                send_email(subject, html_content, userEmail)
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Extend request has been sent. Please wait for confirmation!"
                })
            except Exception as e:
                return Response({
                    "status":400,
                    "success": False,
                    "message": str(e)
                })
    def get(self, request):
        userType = request.query_params.get('userType')
        if userType == 'Lender':
            lenderDetails = ExtendTransaction.objects.filter(order__lender = request.user)
            serialize = ViewLenderExtendSerializer(lenderDetails, many=True).data
            return Response({
                'status': 200,
                "success": True,
                "lenderDetails": serialize
            })
        if userType =='Renter':
            renterDetails = ExtendTransaction.objects.filter(order__renter = request.user)
            serialize = ViewRenterExtendSerializer(renterDetails, many=True).data
            return Response({
                'status': 200,
                "success": True,
                "renterDetails": serialize
            })
    def put(self, request):
        try:
            transactionExtendId = request.query_params.get('transactionExtendId')
            requestStatus = request.query_params.get('status')
            details = ExtendTransaction.objects.filter(id = transactionExtendId).first()
            if details is None:
                return Response({
                "status":400,
                "success": False,
                "message": "invalid id"
            })
            transactionObject = ExtendTransaction.objects.get(id = transactionExtendId)
            transactionObject.extendStatus = requestStatus
            transactionObject.save()
            return Response({
                "status":200,
                "success": True,
                "message": "Thanks!"
            })
        except Exception as e:
            return Response({
                "status":400,
                "success": False,
                "message": str(e)
            })

class TransactionExtendView(APIView):
    def post(self, request):
        try:
            extendAmount = request.query_params.get('extendAmount')
            extendRequestID = request.query_params.get('extendRequestID')
            lenderID = request.query_params.get('lenderID')
            productName = request.query_params.get('productName')
            unitAmount = int(extendAmount) * 100
            # (Payment Amount * Percentage Fee) + Fixed Fee
            stripeProcessingFees = (float(extendAmount) * 0.03) + 0.30
            finalFees = round(stripeProcessingFees, 2) * 100
            print(finalFees)
            lenderAccountDetails = BankAccount.objects.filter(user = lenderID).first()
            if lenderAccountDetails is None:
                return Response({
                    "status":400,
                    "success": False,
                    "message": "Lender account details does not exist!"
                })
            stripe_account_id = lenderAccountDetails.stripe_account_id
            session = stripe.checkout.Session.create(
                mode="payment",
                customer_email = request.user.email,
                invoice_creation={"enabled": True},
                metadata = {
                    "extendRequestID" : extendRequestID,
                    "lenderID" : lenderID,
                    "stripe_account_id" : stripe_account_id,
                    "processingFees" : finalFees,
                },
                line_items=[{
                    'price_data': {
                    'currency': 'CAD',
                    'unit_amount': unitAmount,
                    'product_data': {
                        'name': productName,  
                    },
                    }, 
                    'quantity': 1,
                }],
                payment_intent_data={
                    "application_fee_amount": int(finalFees * 100),
                    "transfer_data": {"destination": stripe_account_id},
                },
                success_url= domain_url + '/api/transaction-extend-success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + '/api/transaction-extend-cancel/',
            )
            return Response({
                "status":200,
                "success": True,
                "paymentDetails": session['url']
            })
        except Exception as e:
            return Response({
                "status":400,
                "success": False,
                "message": str(e)
            })
        
def TransactonExtendSuccess(request):
    session_id = request.GET.get('session_id')
    retrieveSession = stripe.checkout.Session.retrieve(session_id)
    amount = retrieveSession['amount_total'] / 100
    customer_id = retrieveSession.customer
    extendRequestID = retrieveSession['metadata']['extendRequestID']
    transactionObject = ExtendTransaction.objects.get(id = extendRequestID)
    transactionObject.extentPaymentStatus = True
    transactionObject.extendPaymentId = retrieveSession['payment_intent']
    transactionObject.save()
    # return JsonResponse(retrieveSession)
    return render(request, 'extend-payment-success.html', {'amount': amount})

def TransactonExtendCancel(request):
    return render(request, 'payment-failed.html')


