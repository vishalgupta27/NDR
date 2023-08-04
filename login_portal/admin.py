from django.contrib import admin

from login_portal.models import *
from accounts.models import Notification
# Register your models here.
admin.site.register(rewards)
admin.site.register(NDR_Taxes)
admin.site.register(Analytics)
admin.site.register(NDR_FAQs)
admin.site.register(NDR_Documents)
admin.site.register(NDR_PrivacyPolicy)
admin.site.register(Notification)
