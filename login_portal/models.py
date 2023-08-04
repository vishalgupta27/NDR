import imp

from django.core.exceptions import ValidationError
from django.db import models
import uuid
from accounts.models import User


# Create your models here.


class subscription(models.Model):
    profile_id = models.CharField(max_length=500)
    PLANS_TYPE = (
        ('Silver', 'Silver'),
        ('Gold ', 'Gold'),
        ('Platinum ', 'Platinum'),
    )
    plans_type = models.CharField(max_length=100, choices=PLANS_TYPE, null=True)
    subscription_title = models.CharField(max_length=200, null=True)
    subscription_description = models.CharField(max_length=1000, null=True)
    subscription_duration = models.IntegerField(null=True)
    subscription_amount = models.CharField(max_length=100, null=True)
    start_date = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.CharField(max_length=100, null=True, blank=True)


# https://medium.com/analytics-vidhya/django-and-stripe-subscriptions-part-2-8ddd406458a9
class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripeid = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    membership = models.BooleanField(default=False)


class rewards(models.Model):
    title = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=100, null=True)
    amount = models.CharField(max_length=100, null=True)
    valid_from = models.CharField(max_length=100, null=True)
    valid_to = models.CharField(max_length=100, null=True)
    # max_value = models.IntegerField(validators=[MaxValueValidator(100)], verbose_name='Coupon Quantity', null=True) # No. of coupon
    # used = models.IntegerField(default=0)
    # REWARD_STATUS = (
    #     ('Active', 'Active'),
    #     ('Expire', 'Expire')
    # )
    reward_status = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title


class NDR_Taxes(models.Model):
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, default=0)
    ndr_charge = models.DecimalField(max_digits=4, decimal_places=2, null=True, default=0)
    points_earned_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, default=0)
    ndr_credit_card_charge = models.DecimalField(max_digits=4, decimal_places=2, null=True, default=0)
    renter_credit_card_charge = models.DecimalField(max_digits=4, decimal_places=2, null=True, default=0)


class Analytics(models.Model):
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    sales = models.IntegerField(null=True, blank=True)
    profit = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.month} - {self.year} - {self.sales} - {self.profit}'


class NDR_FAQs(models.Model):
    questions = models.CharField(max_length=100, null=True)
    answers = models.TextField(null=True)

    def __str__(self):
        return self.questions


def validate_file_extension(file):
    if file.name.endswith('.pdf') or file.name.endswith('.docx'):
        return
    raise ValidationError('Only PDF and Word files are allowed.')


class NDR_Documents(models.Model):
    files = models.FileField(upload_to='user/documents', validators=[validate_file_extension])


class NDR_PrivacyPolicy(models.Model):
    files = models.FileField(upload_to='user/PP_documents', validators=[validate_file_extension])


