from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Products)
admin.site.register(Product_Images)
admin.site.register(ProductStatusCode)
#Anand
admin.site.register(ProductCategory)
admin.site.register(Wishlist)
admin.site.register(ProductPickUpReturn)
admin.site.register(Reward)
admin.site.register(RequestInbox)
admin.site.register(UnavailabilityDate)
admin.site.register(LenderReviews)
admin.site.register(RenterReviews)
admin.site.register(ProductReviews)
admin.site.register(ReportIncident)
admin.site.register(OrderDetails)
