from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Account_type)
admin.site.register(Address)
admin.site.register(GPSAddress)
admin.site.register(UserDeviceToken)
admin.site.register(Notifications)
admin.site.register(UserUnavailability)
admin.site.register(UserWeekAvailability)
admin.site.register(XeroAccountingToken)
admin.site.register(CustomerSupport)
admin.site.register(PreferencesNotifications)
admin.site.register(BankAccount)
