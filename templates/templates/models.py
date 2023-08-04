from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, UserManager,BaseUserManager
import uuid
from .utils import generate_qr
# Create your models here.
import os
import glob
from django.core.files.base import ContentFile

class Account_type (models.Model):

    AccountType = models.CharField(max_length=100,null = False)
    #UserAccountType = models.ForeignKey(User,on_delete = models.DO_NOTHING)

    class Meta:
        db_table = "tbl_AccountType"

    def __str__(self):
        return self.AccountType



class MyUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):

        user = self.model(email=self.normalize_email(email) , **extra_fields)
        user.set_password(password)

        qr_payload = {
            'user ID' : user.account_id,
            #'username' : user.username,
            'phone number':user.phone_number
        }

        #generated_qr_image = generate_qr(user.account_id,'user/tmp/{}.png'.format(user.account_id))
        generated_qr_image = generate_qr(qr_payload, 'user/tmp/{}.png'.format(user.account_id))

        files = glob.glob('user/tmp//*')
        for f in files:
            os.remove(f)


        user.save(using = self._db)
        user.QrCode_Account.save('{}.jpg'.format(user.account_id), ContentFile(generated_qr_image))
        user.save(using = self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user



#class User(AbstractUser):
class User(AbstractBaseUser):
    objects = MyUserManager()

    USER_ACCOUNT_CHOICES = (
        ("Business", "Business"),
        ("Personal", "Personal"),
    )

    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # comment the above based on query performance

    #username = models.CharField(max_length=255,unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255,null=True)

    #temp OTP please remove once Third Party api is given by the client

    otp = models.CharField(max_length=20,null=True)
    otp_status = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20,null=True)
    #UserAccountType = models.CharField(max_length=100, null=True,choices=USER_ACCOUNT_CHOICES)
    UserAccountType = models.ForeignKey(Account_type, null=True,on_delete = models.DO_NOTHING)
    CountryOfBirth = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100,null=True)
    #FileField()
    #QrCode_Account = models.ImageField(upload_to='user/qr_codes', max_length=255)
    QrCode_Account = models.FileField(upload_to='user/qr_codes',  null=True, blank=True)
    CreationDate = models.DateTimeField(auto_now_add=True) #models.TimeField(auto_now=True, auto_now_add=True)
    Name_First = models.CharField(max_length=100, unique=False)
    Name_Last = models.CharField(max_length=100, unique=False)
    PhotoID = models.FileField(
        upload_to='user/PhotoID', null=True, blank=True
    )
    Citizenship = models.CharField(max_length=100, null=False, unique=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    Email_Verified = models.BooleanField(default=False)
    PhoneNumber_Verfied = models.BooleanField(default=False)
    Email_VerificationMethod = models.CharField(max_length = 50, null=True)
    PhoneNumber_VerificationMethod = models.CharField(max_length=50, null=True)
    Birth_Day = models.PositiveSmallIntegerField(max_length=4,null=True)
    Birth_Month = models.PositiveSmallIntegerField(max_length=4, null=True)
    Birth_Year = models.PositiveSmallIntegerField(max_length=6, null=True)
    PhotoID_Number = models.CharField(max_length=100, null=True, unique=False)
    VerificationDate = models.CharField(max_length=50, null=True, unique=False)
    VerificationPersonalID = models.CharField(max_length=100, null=True, unique=False)

    #Use Django Relations later for the below columns, store them in a separate table

    #Address_Number = models.CharField(max_length=50, null=True, unique=False)
    #Address_Street1 = models.CharField(max_length=255, null=True, unique=False)
    #Address_Street2 = models.CharField(max_length=255, null=True, unique=False)
    #Address_City = models.CharField(max_length=50, null=True, unique=False)
    #Address_Province = models.CharField(max_length=50, null=True, unique=False)
    #Address_Postal = models.CharField(max_length=50, null=True, unique=False)
    #Address_Country = models.CharField(max_length=50, null=True, unique=False)
    #CreditCard_Type = models.CharField(max_length=50, null=True, unique=False)
    CreditCard_Type = models.CharField(max_length=50, null=True, unique=False)
    profile_image = models.ImageField(upload_to='user/profile_image',  null=True, blank=True)

    ## Define Username_field

    USERNAME_FIELD = 'email'
    #USERNAME_FIELD = 'username'
    #REQUIRED_FIELDS = ['email','username']
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

    #@property
    #def is_staff(self):
    #    "Is the user a member of staff?"
    #    return self.staff

    #@property
    #def is_admin(self):
    #    "Is the user a admin member?"
    #    return self.admin

    #def __str__(self):
    #    return self.UserAccountType

    class Meta:

        db_table = "tbl_AccountRegistration"





#class Account_type (models.Model):
#    ACCOUNT_CHOICES = (
#        ("Business", "Business"),
#        ("Personal", "Personal"),
#    )
#    account = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#    AccountType_key = models.AutoField(primary_key=True)
#    AccountType = models.CharField(max_length=100, choices = ACCOUNT_CHOICES)
#
#    class Meta:
#        db_table = "tbl_AccountType"

# class Address_Type(models.Model):
#     addressType = models.CharField(max_length=100, null=True, blank=True)

#     def __str__(self):
#         return self.addressType

class Address(models.Model):
    Address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    QrCode_Account = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING,related_name="my_address")
    Address_Number = models.CharField(max_length=50, null=True, unique=False)
    Address_Street1 = models.CharField(max_length=255, null=True, unique=False)
    Address_Street2 = models.CharField(max_length=255, null=True, unique=False)
    Address_City = models.CharField(max_length=50, null=True, unique=False)
    Address_Province = models.CharField(max_length=50, null=True, unique=False)
    Address_Postal = models.CharField(max_length=50, null=True, unique=False)
    Address_Country = models.CharField(max_length=50, null=True, unique=False)


    class Meta:
        db_table = "tbl_Address"


    def __str__(self):
        #Qraccount from user and email
        return self.QrCode_Account.email








#your_choice=models.ForeignKey(ChoiceList,on_delete=models.CASCADE)






