from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, UserManager, BaseUserManager
import uuid
from .utils import generate_qr
# Create your models here.
import os
import glob
from django.core.files.base import ContentFile
import random, string


class Account_type(models.Model):
    AccountType = models.CharField(max_length=100, null=False)

    # UserAccountType = models.ForeignKey(User,on_delete = models.DO_NOTHING)

    class Meta:
        db_table = "tbl_AccountType"

    def __str__(self):
        return self.AccountType


class MyUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)

        # Show Data Whene Uer Scan QR 
        qr_payload = {
            'user ID': user.account_id,
            # 'username' : user.username,
            'phone number': user.phone_number
        }

        # generated_qr_image = generate_qr(user.account_id,'user/tmp/{}.png'.format(user.account_id))
        generated_qr_image = generate_qr(qr_payload, 'user/tmp/{}.png'.format(user.account_id))

        files = glob.glob('user/tmp//*')
        for f in files:
            os.remove(f)

        user.save(using=self._db)
        user.QrCode_Account.save('{}.jpg'.format(user.account_id), ContentFile(generated_qr_image))
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# class User(AbstractUser):
class User(AbstractBaseUser):
    objects = MyUserManager()

    def generate_code(length):
        random_code = ''.join((random.choice(string.ascii_letters) for x in range(length)))
        return str(random_code)

    # generate_code_obj = generate_code
    USER_ACCOUNT_CHOICES = (
        ("Business", "Business"),
        ("Personal", "Personal"),
    )
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True)
    otp = models.CharField(max_length=20, null=True)
    otp_status = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, null=True)
    uuid = models.CharField(max_length=1000, null=True, blank=True)
    UserAccountType = models.ForeignKey(Account_type, null=True, on_delete=models.DO_NOTHING)
    CountryOfBirth = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    QrCode_Account = models.FileField(upload_to='user/qr_codes', null=True, blank=True)
    CreationDate = models.DateTimeField(auto_now_add=True)
    Name_First = models.CharField(max_length=100, unique=False)
    Name_Last = models.CharField(max_length=100, unique=False)
    PhotoID = models.FileField(
        upload_to='user/PhotoID', null=True, blank=True
    )
    Citizenship = models.CharField(max_length=100, null=False, unique=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    user_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    Email_Verified = models.BooleanField(default=False)
    PhoneNumber_Verfied = models.BooleanField(default=False)
    Email_VerificationMethod = models.CharField(max_length=50, null=True)
    PhoneNumber_VerificationMethod = models.CharField(max_length=50, null=True)
    Birth_Day = models.PositiveSmallIntegerField(max_length=4, null=True)
    Birth_Month = models.PositiveSmallIntegerField(max_length=4, null=True)
    Birth_Year = models.PositiveSmallIntegerField(max_length=6, null=True)
    PhotoID_Number = models.CharField(max_length=100, null=True, unique=False)
    VerificationPersonalID = models.CharField(max_length=100, null=True, unique=False)
    CreditCard_Type = models.CharField(max_length=50, null=True, unique=False)
    profile_image = models.ImageField(upload_to='user/profile_image', null=True, blank=True)
    reward_points = models.CharField(max_length=1000, null=True, blank=True)
    hst_number = models.CharField(max_length=1000, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    referal_code = models.CharField(max_length=6, editable=False, null=True, blank=True)
    is_bank_account = models.BooleanField(default=False)

    ## Define Username_field

    USERNAME_FIELD = 'email'
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email','username']
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    # Override Save Method
    def save(self, *args, **kwargs):
        self.referal_code = random.randint(10000, 99999)
        super(User, self).save(*args, **kwargs)

    # @property
    # def is_staff(self):
    #    "Is the user a member of staff?"
    #    return self.staff

    # @property
    # def is_admin(self):
    #    "Is the user a admin member?"
    #    return self.admin

    # def __str__(self):
    #    return self.UserAccountType

    class Meta:
        db_table = "tbl_AccountRegistration"


class Address(models.Model):
    Address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    QrCode_Account = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="my_address")
    Address_Number = models.CharField(max_length=50, null=True, unique=False)
    Address_Street1 = models.CharField(max_length=255, null=True, unique=False)
    Address_Street2 = models.CharField(max_length=255, null=True, unique=False)
    Address_Lat = models.CharField(max_length=255, null=True, unique=False)
    Address_Long = models.CharField(max_length=255, null=True, unique=False)
    Address_City = models.CharField(max_length=50, null=True, unique=False)
    Address_Province = models.CharField(max_length=50, null=True, unique=False)
    Address_Postal = models.CharField(max_length=50, null=True, unique=False)
    Address_Country = models.CharField(max_length=50, null=True, unique=False)

    class Meta:
        db_table = "tbl_Address"

    def __str__(self):
        # Qraccount from user and email
        return self.QrCode_Account.email


class GPSAddress(models.Model):
    Address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    QrCode_Account = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="my_gps_address")
    Address_Number = models.CharField(max_length=50, null=True, unique=False)
    Address_Street1 = models.CharField(max_length=255, null=True, unique=False)
    Address_Street2 = models.CharField(max_length=255, null=True, unique=False)
    Address_Lat = models.CharField(max_length=255, null=True, unique=False)
    Address_Long = models.CharField(max_length=255, null=True, unique=False)
    Address_City = models.CharField(max_length=50, null=True, unique=False)
    Address_Province = models.CharField(max_length=50, null=True, unique=False)
    Address_Postal = models.CharField(max_length=50, null=True, unique=False)
    Address_Country = models.CharField(max_length=50, null=True, unique=False)
    isGPS = models.BooleanField(default=False)

    def __str__(self):
        # Qraccount from user and email
        return self.QrCode_Account.email


# your_choice=models.ForeignKey(ChoiceList,on_delete=models.CASCADE)

class UserDeviceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    device_id = models.CharField(max_length=1000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user) + ' ' + self.device_id


class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True)
    screen_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.title}'


class UserUnavailability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    unavailableDate = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.user.Name_First} {self.user.Name_Last}'


class UserWeekAvailability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    weekAvailability = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.user.Name_First} {self.user.Name_Last}'


class XeroAccountingToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    access_token = models.CharField(max_length=10000, null=True, blank=True)
    refresh_token = models.CharField(max_length=1000, null=True, blank=True)
    expires_in = models.CharField(max_length=100, null=True, blank=True)
    token_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.token_type}'


class CustomerSupport(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    dateTimeSubmitted = models.DateTimeField(auto_now_add=True, null=True)
    ticketNumber = models.CharField(max_length=100, null=True, blank=True)
    issueText = models.TextField(null=True, blank=True)
    dateTimeResolved = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.ticketNumber


class PreferencesNotifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    isEmail = models.BooleanField(default=False)
    isNotifications = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}"


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    routing_number = models.CharField(max_length=255, null=True, blank=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email}'


class Notification(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChatAbusiveContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    files = models.FileField(upload_to='user/abusive_document')
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.files
