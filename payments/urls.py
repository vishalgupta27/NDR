
from .views import *
from django.urls import path

urlpatterns = [
    path('api/create_stripe_account/', CreateStripeAccount.as_view(), name="CreateStripeAccount"),
    path('api/link-account/', LinkAccountView.as_view(), name="LinkAccountView"),
    # path('api/edit-bank-account/', EditBankAccountsView.as_view(), name="EditBankAccountsView"),
    path('users/oauth/callback/', BankAccountReturnURL, name='authorize_callback'),
    path('api/payment/', PaymentGatewayView.as_view(), name="PaymentGatewayView"),
    path('api/payment-success', PaymentSuccessView, name="PaymentSuccessView"),
    path('api/payment-cancelled/', PaymentCancelView, name="PaymentCancelView"),
    path('api/refund-payment/', RefundPaymentView.as_view(), name="RefundPaymentView"),
    path('api/xero-auth/', XeroAuthView.as_view(), name="XeroAuthView"),
    path('xero/callback/', XeroAuthCallBackURL, name="XeroAuthCallBackURL"),
    path('api/xero/refresh-access-token/', XeroRefreshAccessTokenView.as_view(), name="XeroRefreshAccessTokenView"),
    path('api/booked-products/', BookedProductsView.as_view(), name="BookedProductsView"),
    path('api/add-bank-account/', AddStripeBankAccountView.as_view(), name="AddStripeBankAccountView"),
    path('api/transaction-extend-request/', RequestTransactionExtendView.as_view(), name="RequestTransactionExtendView"),
    path('api/transaction-extend-payment/', TransactionExtendView.as_view(), name="TransactionExtendView"),
    path('api/transaction-extend-success/', TransactonExtendSuccess, name="TransactonExtendSuccess"),
    path('api/transaction-extend-cancel/', TransactonExtendCancel, name="TransactonExtendCancel"),
]
