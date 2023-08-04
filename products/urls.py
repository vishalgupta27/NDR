from .views import *
from django.urls import path

urlpatterns = [

    path('api/add_products/',AddProductView.as_view() , name="Add_Product"),
    path('api/view_products/',ViewAllProductView.as_view() , name="View_Product"),
    path('api/view_my_products/',ViewAllMyProductView.as_view() , name="View_My_Product"),
    path('api/test/',TestRelationsView.as_view() , name="Test"),
    path('api/ProductImagerView/',ProductImage.as_view(),name="ProductImagerView"),
    path('api/ProductExplore/',Product_Explore.as_view(),name="ProductExplore"),
    
    # By Anand
    path('api/add_to_wishlist/', UserWishlist.as_view() , name="AddToWishlist"),
    path('api/my_wishlist/', ViewMyWishlist.as_view(), name="ViewMyWishlist"),
    path('api/product_category/', ProductCategoryView.as_view(), name="ProductCategory"),
    path('api/ProductFilter/',ProductFilterView.as_view(),name='ProductFilter'),
    path('api/send_request/', SendRequestInboxView.as_view(), name="SendRequestInbox"),
    path('api/request_inbox/', ViewAllRequestInboxView.as_view(), name="RequestInbox"),
    path('api/sort_filter/', FilterSort.as_view(), name="SortFilter"),
    # path('api/sort_item/', SortItemView.as_view(), name="SortItem"),
    
    path('api/product_unavailability_date/', ProductUnavailabiltyDate.as_view(), name="ProductUnavailabiltyDate"),
    path('api/report_incident/', ReportIncidentViews.as_view(), name="ReportIncidentViews"),
    path('api/view_lender_products/', ViewLenderProducts.as_view(), name="ViewLenderProducts"),
    path('api/view_renter_products/', RenterRequestedProducts.as_view(), name="RenterRequestedProducts"),
    path('api/view_ndr_tax/', NDRTaxViewAPI.as_view(), name="NDRTaxViewAPI"),
   
    path('api/create_order/', CreateOrder.as_view(), name="CreateOrder"),
    # path('api/send_referral/', ReferralView.as_view(), name="SendReferralView"),
    path('api/my_orders/', RenterOrderView.as_view(), name="RenterOrderView"),
    path('api/transactions/', TransactionView.as_view(), name="TransactionView"),

    path('api/renter_orders_pickup/', RenterPickupConfirmation.as_view(), name="RenterPickupConfirmation"),
    path('api/lender_orders_pickup/', LenderPickupConfirmation.as_view(), name="LenderPickupConfirmation"),
    path('api/renter_product_return/', RenterProductReturnView.as_view(), name="RenterProductReturnView"),
    path('api/lender_product_return/', LenderProductReturnView.as_view(), name="LenderProductReturnView"),
    path('api/product_review/', ProductRatingView.as_view(), name="ProductRatingView"),
    path('api/lender_review/', LenderRatingView.as_view(), name="LenderRatingView"),
    
    path('api/gps_lat_long/', GPSOnOffLatLong.as_view(), name="GPSOnOffLatLong"),
    path('api/my_filters/', ProductsFilters.as_view(), name="ProductsFilters"),
    path('api/faqs/', FAQsView.as_view(), name="FAQsView"),
    path('api/subscriptions/', SubscriptionsView.as_view(), name="SubscriptionsView"),
    path('api/products-filter/', ProductsFilterView.as_view(), name="ProductsFilterView"),
    # path('api/view-products/', ViewProducts.as_view(), name="ViewProducts"),
    path('api/my-reviews/', MyProfileReviewView.as_view(), name="MyProfileReviewView"),
    path('api/transaction-filter/', TransactionFilterView.as_view(), name="TransactionFilterView"), 
]

# https://github.com/seyyedaliayati/django-fcm-sample-project