# from .views import RegisterAPI , MyTokenObtainPairView, HelloView, ForgetPasswordView, ChangePasswordView, BlacklistRefreshView
from django.conf.urls.static import static

from .views import *
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views

# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [
    # =================== Admin functionality ===================================
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('coming-soon', views.coming_soon, name='coming_soon'),
    path('login_admin_user', views.login_admin_user, name='login_admin_user'),
    path('admin_logout', views.admin_logout, name='admin_logout'),
    path('admin_user_page', views.admin_user_page, name='admin_user_page'),
    path('edit_user_to_active/<str:id>', views.edit_user_to_active, name='edit_user_to_active'),
    path('edit_user_to_inactive/<str:id>', views.edit_user_to_inactive, name='edit_user_to_inactive'),
    path('show_user_profile/<str:id>', views.show_user_profile, name='show_user_profile'),
    path('edit_user_to_verified/<str:id>', views.edit_user_to_verified, name='edit_user_to_verified'),
    path('admin_profile_page', views.admin_profile_page, name='admin_profile_page'),
    path('admin_product_page', views.admin_product_page, name='admin_product_page'),
    path('upload_admin_profile', views.upload_admin_profile, name='upload_admin_profile'),
    path('admin_pickup_return_page', views.admin_pickup_return_page, name='admin_pickup_return_page'),
    path('admin_content_page', views.admin_content_page, name='admin_content_page'),
    path('admin_subscription_page', views.admin_subscription_page, name='admin_subscription_page'),
    path('admin_rewards_page', views.admin_rewards_page, name='admin_rewards_page'),
    path('admin_notification', views.admin_notification, name='admin_notification'),
    path('admin_add_subscription_page', views.admin_add_subscription_page, name='admin_add_subscription_page'),
    path('admin_add_rewards_page', views.admin_add_rewards_page, name='admin_add_rewards_page'),
    path('edit_reward/<int:pk>', views.admin_edit_rewards, name="EditReward"),
    path('admin_add_subscription_page_data', views.admin_add_subscription_page_data,
         name='admin_add_subscription_page_data'),
    path('admin_add_rewards_page_data', views.admin_add_rewards_page_data, name='admin_add_rewards_page_data'),
    path('admin_delete_subscription_data/<str:id>', views.admin_delete_subscription_data,
         name='admin_delete_subscription_data'),
    path('edit_subscription/<str:pk>', views.admin_edit_subscription_page, name='admin_edit_subscription_page'),
    path('update_subscription', views.admin_update_subscription_page, name='admin_update_subscription_page'),
    path('admin_delete_rewards_data/<str:id>', views.admin_delete_rewards_data, name='admin_delete_rewards_data'),
    path('add_category', views.AddCategoryView, name="admin_add_category"),
    path('edit_category/<str:category_id>', views.editCategoryView, name="admin_edit_category"),
    path('categories', views.CategoryListView, name="CategoryListView"),
    path('delete_category/<str:category_id>', views.deleteCategoryView, name="deleteCategoryView"),
    path('success', views.success, name="success"),
    path('send_notification', views.send_noti, name="send_notification"),
    path('report-incident-list', views.ListofReportIncident, name="ListofReportIncident"),
    path('report_incident_details/<int:pk>', views.ReportIncidentDetails, name="ReportIncidentDetails"),
    path('send_reply', views.ReplyReportIncident, name="ReplyReportIncident"),
    path('user_active_inactive/<str:user_id>', views.UserActiveInactive, name="UserActiveInactive"),
    path('view_user/<str:user_id>', views.ViewUser, name="ViewUser"),
    path('verify_user', views.userVerfication, name="userVerfication"),
    path('ndr_taxes_view', views.NDR_Taxes_View, name="NDR_Taxes_View"),
    path('ndr_taxes_list', views.TaxList, name="TaxList"),
    path('update_ndr_tax/<int:id>', views.UpdateNDRTaxes, name="UpdateNDRTaxes"),
    path('delete_ndr_tax/<int:pk>', views.DeleteNDRTax, name="DeleteNDRTax"),
    path('transactions_details', views.TransactionDetails, name="TransactionDetails"),
    path('add_faq', views.admin_add_faq, name="admin_add_faq"),
    path('FAQs', views.faq_list, name="faq_list"),
    path('delete_faqs/<int:id>', views.Admin_Delete_FAQs, name="Admin_Delete_FAQs"),
    path('update_faqs/<int:id>', views.Admin_Update_FAQs, name="Admin_Update_FAQs"),
    path('product_details/<str:product_id>', views.ProductDetails, name="ProductDetails"),
    path('product_verify', views.VerifyProduct, name="VerifyProduct"),
    path('admin_add_terms_conditions', views.admin_add_terms_conditions, name="admin_add_terms_conditions"),
    path('terms_conditions_list', views.terms_conditions_list, name="terms_conditions_list"),
    path('delete_tcs/<int:id>', views.delete_tcs, name="delete_tcs"),
    path('download_file/<int:id>/', views.download_file, name='download_file'),
    path('add_privacy_policy', views.add_privacy_policy, name='add_privacy_policy'),
    path('privacy_policy_list', views.privacy_policy_list, name='privacy_policy_list'),
    path('delete_Privacy_Policy/<int:id>', views.delete_Privacy_Policy, name="delete_Privacy_Policy"),
    path('download_file_pp/<int:id>/', views.download_file_pp, name='download_file_pp'),
    path('admin_add_notification', views.admin_add_notification, name='admin_add_notification'),
    path('notifications_lists', views.notifications_lists, name='notifications_lists'),
    path('delete_Notification/<int:id>', views.delete_Notification, name='delete_Notification'),
    path('edit_notifications/<int:id>', views.edit_notifications, name='edit_notifications'),
    path('get_chat_list/<str:uuid>/', views.get_chat_lists, name='get_chat_list'),
    path('chat_page', views.chat_page, name='chat_page'),
    path('view_page/<str:email>/', views.view_page, name='view_page'),
    path('abusive_content_list/', views.abusive_content_list, name='abusive_content_list'),
    path('download_file_chat/<int:id>/', views.download_file_chat, name='download_file_chat'),

]

